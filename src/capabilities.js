import { basename, extname, join } from "node:path";
import { readdirSync } from "node:fs";

import { loadCapabilities, loadModes, loadToolRules, resolveMode, rulesVersion } from "./rules.js";
import { runCommand } from "./common.js";
import { probeGraphifyUnitsRefs } from "./graphify-refs.js";

function executable(envName, fallback) {
  return process.env[envName] ?? fallback;
}

function commandCheck(id, command, args, remediation, required = true, meta = {}) {
  const result = runCommand(command, args);
  return {
    id,
    required,
    status: result.ok ? "pass" : "fail",
    command,
    version: result.ok ? result.stdout.split("\n")[0] : null,
    remediation: result.ok ? null : remediation,
    ...meta,
  };
}

export function detectTools() {
  const git = commandCheck("git", executable("REPO_ANALYZER_GIT", "git"), ["--version"], "安装 Git，并确保 git 位于 PATH。");
  const rg = commandCheck("text-search-rg", executable("REPO_ANALYZER_RG", "rg"), ["--version"], "安装 ripgrep，或确保 grep 可用。", false);
  const grep = commandCheck("text-search-grep", executable("REPO_ANALYZER_GREP", "grep"), ["--version"], "安装 grep 或 ripgrep。", false);
  const textSearch = {
    id: "text-search",
    required: true,
    status: rg.status === "pass" || grep.status === "pass" ? "pass" : "fail",
    command: rg.status === "pass" ? rg.command : grep.command,
    version: rg.status === "pass" ? rg.version : grep.version,
    provider: rg.status === "pass" ? "ripgrep" : grep.status === "pass" ? "grep" : null,
    remediation: rg.status === "fail" && grep.status === "fail" ? "安装 ripgrep 或 grep，并确保命令位于 PATH。" : null,
  };

  const ctagsCommand = executable("REPO_ANALYZER_CTAGS", "ctags");
  const ctagsVersion = runCommand(ctagsCommand, ["--version"]);
  const ctagsOk = ctagsVersion.ok && /Universal Ctags/i.test(ctagsVersion.stdout);
  const ctagsLanguages = ctagsOk ? runCommand(ctagsCommand, ["--list-languages"]) : { ok: false, stdout: "" };
  const ctags = {
    name: "universal-ctags",
    available: ctagsOk,
    command: ctagsOk ? ctagsCommand : null,
    version: ctagsOk ? ctagsVersion.stdout.split("\n")[0] : null,
    languages: ctagsLanguages.ok ? ctagsLanguages.stdout.split("\n").filter(Boolean) : [],
  };

  const astCommand = executable("REPO_ANALYZER_AST_GREP", "ast-grep");
  const astVersion = runCommand(astCommand, ["--version"]);
  const astGrep = {
    name: "ast-grep",
    available: astVersion.ok,
    command: astVersion.ok ? astCommand : null,
    version: astVersion.ok ? astVersion.stdout.split("\n")[0] : null,
  };

  const graphifyCommand = executable("REPO_ANALYZER_GRAPHIFY", "graphify");
  const graphifyVersion = runCommand(graphifyCommand, ["--version"]);
  // Fixture/mock graphify can also prove deep capabilities via env override.
  const graphifyCapabilities = parseCapabilityOverride(process.env.REPO_ANALYZER_GRAPHIFY_CAPABILITIES);
  const graphify = {
    name: "graphify",
    available: graphifyVersion.ok,
    command: graphifyVersion.ok ? graphifyCommand : null,
    version: graphifyVersion.ok ? graphifyVersion.stdout.split("\n")[0] : null,
    capabilities: graphifyCapabilities ?? (graphifyVersion.ok
      ? ["graph-queries", "symbol-enumeration", "reference-edges"]
      : []),
  };

  return {
    baseline: { git, textSearch, rg, grep },
    enhanced: { graphify, ctags, astGrep },
  };
}

function parseCapabilityOverride(raw) {
  if (!raw) return null;
  return raw.split(",").map((item) => item.trim()).filter(Boolean);
}


/**
 * 廉价探针：判断当前环境对本仓是否真的能产出 units 可用的 complete 引用边。
 * 仅「工具在 PATH」不足以放行 deep——否则会在 evidence/gate 才失败并浪费 token。
 *
 * 当前 units 合同：
 * - complete 可来自 universal-ctags 的 reference-role 标签；
 * - complete 也可来自 Graphify graph.json 的 EXTRACTED call/import/reference 边（真实接线）；
 * - rg/grep 文本引用一律 partial；
 * - REPO_ANALYZER_GRAPHIFY_UNITS_REFS=1 仍可作为强制启用/测试覆盖开关；
 *   若未设置，只要目标仓存在可用 graphify-out/graph.json EXTRACTED 边，同样视为已接线。
 */
export function probeReferenceEdgeUsability({ repoPath, languages = [], detected, maxFiles = 6 }) {
  const { ctags, graphify } = detected.enhanced;
  const sampleFiles = pickSampleSourceFiles(repoPath, languages, maxFiles);
  let ctagsReferenceTags = 0;
  let ctagsDefinitionTags = 0;
  let filesProbed = 0;
  const sampleEvidence = [];

  if (ctags.available && sampleFiles.length > 0) {
    for (const file of sampleFiles) {
      const absolute = join(repoPath, file);
      const result = runCommand(ctags.command, [
        "--output-format=json",
        "--fields=+nK",
        "--extras=+r",
        "--sort=no",
        "-f",
        "-",
        absolute,
      ]);
      if (!result.ok) {
        sampleEvidence.push({ file, ok: false, error: result.stderr || "ctags failed" });
        continue;
      }
      filesProbed += 1;
      let fileRefs = 0;
      let fileDefs = 0;
      for (const line of result.stdout.split(/\r?\n/)) {
        if (!line.trim()) continue;
        try {
          const tag = JSON.parse(line);
          if (tag._type !== "tag" || !tag.name) continue;
          const isRef = String(tag.roles ?? "")
            .split(",")
            .map((item) => item.trim())
            .includes("reference");
          if (isRef) {
            ctagsReferenceTags += 1;
            fileRefs += 1;
          } else {
            ctagsDefinitionTags += 1;
            fileDefs += 1;
          }
        } catch {
          // ignore non-tag lines
        }
      }
      sampleEvidence.push({ file, ok: true, definition_tags: fileDefs, reference_tags: fileRefs });
    }
  }

  const ctagsUsable = ctags.available && ctagsReferenceTags > 0;

  const envForceGraphifyUnits =
    process.env.REPO_ANALYZER_GRAPHIFY_UNITS_REFS === "1" ||
    process.env.REPO_ANALYZER_GRAPHIFY_UNITS_REFS === "true";
  const graphifyGraphProbe =
    graphify.available && graphify.capabilities.includes("reference-edges")
      ? probeGraphifyUnitsRefs(repoPath)
      : { usable: false, extracted_ref_links: 0, reasons: ["graphify 不可用或不声明 reference-edges"], graph_path: null, nodes: 0, links: 0, symbol_keys: 0 };

  // Real wiring: units.js loads graphify-out/graph.json EXTRACTED edges into refs_status.
  // Env flag remains for fixtures / force-on; auto when target repo has usable graph edges.
  const graphifyUnitsWired =
    envForceGraphifyUnits ||
    (graphify.available &&
      graphify.capabilities.includes("reference-edges") &&
      graphifyGraphProbe.usable);
  const graphifyUsable =
    graphify.available &&
    graphify.capabilities.includes("reference-edges") &&
    graphifyUnitsWired;

  const providers = [];
  if (ctagsUsable) providers.push("universal-ctags");
  if (graphifyUsable) providers.push("graphify");

  const reasons = [];
  if (!ctagsUsable && !graphifyUsable) {
    if (!ctags.available && !graphify.available) {
      reasons.push("未检测到 universal-ctags 或 graphify，无法提供 units 可用的 reference edges。");
    } else if (ctags.available && ctagsReferenceTags === 0) {
      reasons.push(
        `Universal Ctags 在抽样 ${filesProbed || sampleFiles.length} 个源文件中未产出 roles=reference 标签（definition≈${ctagsDefinitionTags}，reference=0）。若无 Graphify EXTRACTED 边，units 只会把 rg/grep 命中标为 partial，deep 的 reference-quality 几乎必然失败。`,
      );
    }
    if (graphify.available && graphify.capabilities.includes("reference-edges") && !graphifyUnitsWired) {
      const detail = graphifyGraphProbe.reasons?.join(" ") || "graphify graph 不可用";
      reasons.push(
        `Graphify 已声明 reference-edges，但目标仓未检测到可用 EXTRACTED 引用边（${detail}）。请在目标仓运行 graphify update . 生成 graphify-out/graph.json，或设置 REPO_ANALYZER_GRAPHIFY_UNITS_REFS=1 并确保 graph 边可被 units 读取。`,
      );
    }
    if (sampleFiles.length === 0 && !graphifyUsable) {
      reasons.push("目标仓未找到可抽样源码文件，无法验证 reference-edge 可用性。");
    }
  }

  return {
    usable: providers.length > 0,
    providers,
    sample_files: sampleFiles,
    files_probed: filesProbed,
    ctags_reference_tags: ctagsReferenceTags,
    ctags_definition_tags: ctagsDefinitionTags,
    graphify_units_refs_wired: Boolean(graphifyUnitsWired),
    graphify_graph: {
      usable: Boolean(graphifyGraphProbe.usable),
      path: graphifyGraphProbe.graph_path ?? null,
      nodes: graphifyGraphProbe.nodes ?? 0,
      links: graphifyGraphProbe.links ?? 0,
      extracted_ref_links: graphifyGraphProbe.extracted_ref_links ?? 0,
      symbol_keys: graphifyGraphProbe.symbol_keys ?? 0,
      env_force: envForceGraphifyUnits,
      reasons: graphifyGraphProbe.reasons ?? [],
    },
    sample_evidence: sampleEvidence,
    reasons,
  };
}

function pickSampleSourceFiles(repoPath, languages, maxFiles) {
  const preferred = new Set(
    (languages ?? [])
      .slice(0, 3)
      .map((item) => String(item.language || item).toLowerCase()),
  );
  const sourceExts = new Set([
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".py", ".go", ".rs", ".java", ".kt", ".kts", ".cs",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".rb", ".php", ".swift",
  ]);
  const preferredFiles = [];
  const otherFiles = [];
  const skipDirs = new Set([".git", "node_modules", "vendor", "dist", "build", "coverage", ".next", "graphify-out"]);

  const visit = (directory, rel = "") => {
    if (preferredFiles.length >= maxFiles) return;
    let entries;
    try {
      entries = readdirSync(directory, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (preferredFiles.length >= maxFiles && otherFiles.length >= maxFiles) return;
      if (skipDirs.has(entry.name)) continue;
      const abs = join(directory, entry.name);
      const childRel = rel ? `${rel}/${entry.name}` : entry.name;
      if (entry.isDirectory()) {
        visit(abs, childRel);
        continue;
      }
      if (!entry.isFile()) continue;
      const ext = extname(entry.name).toLowerCase();
      if (!sourceExts.has(ext)) continue;
      // Prefer non-test application sources for reference probes.
      if (/\b(test|spec|__tests__|__mocks__)\b/i.test(childRel)) continue;
      const lang = LANGUAGE_BY_EXT_HINT[ext];
      if (lang && preferred.has(lang.toLowerCase())) preferredFiles.push(childRel);
      else otherFiles.push(childRel);
    }
  };
  visit(repoPath);
  const ordered = [...preferredFiles, ...otherFiles];
  return ordered.slice(0, maxFiles);
}

const LANGUAGE_BY_EXT_HINT = {
  ".js": "JavaScript",
  ".jsx": "JavaScript",
  ".mjs": "JavaScript",
  ".cjs": "JavaScript",
  ".ts": "TypeScript",
  ".tsx": "TypeScript",
  ".py": "Python",
  ".go": "Go",
  ".rs": "Rust",
  ".java": "Java",
  ".kt": "Kotlin",
  ".kts": "Kotlin",
  ".cs": "C#",
  ".c": "C",
  ".cc": "C++",
  ".cpp": "C++",
  ".rb": "Ruby",
  ".php": "PHP",
  ".swift": "Swift",
};

/**
 * 用探针结果收紧 reference-edges：工具存在 ≠ 对本仓可产出 complete refs。
 * 返回更新后的 capabilityState（就地修改并返回）。
 */
export function applyReferenceEdgeProbe(capabilityState, probe) {
  const next = capabilityState;
  const previousProviders = next["reference-edges"]?.providers ?? [];
  if (probe.usable) {
    next["reference-edges"] = {
      ...(next["reference-edges"] ?? {}),
      available: true,
      providers: probe.providers,
      definition_providers: next["reference-edges"]?.definition_providers ?? ["graphify", "universal-ctags"],
      description: next["reference-edges"]?.description ?? "引用/调用边或等价 reference edges",
      usability_probe: summarizeProbe(probe),
      presence_only_providers: previousProviders.filter((item) => !probe.providers.includes(item)),
    };
    return next;
  }

  next["reference-edges"] = {
    ...(next["reference-edges"] ?? {}),
    available: false,
    providers: [],
    definition_providers: next["reference-edges"]?.definition_providers ?? ["graphify", "universal-ctags"],
    description: next["reference-edges"]?.description ?? "引用/调用边或等价 reference edges",
    usability_probe: summarizeProbe(probe),
    presence_only_providers: previousProviders,
    blocked_reason: (probe.reasons ?? []).join(" "),
  };
  return next;
}

function summarizeProbe(probe) {
  return {
    usable: probe.usable,
    providers: probe.providers,
    sample_files: probe.sample_files,
    files_probed: probe.files_probed,
    ctags_reference_tags: probe.ctags_reference_tags,
    ctags_definition_tags: probe.ctags_definition_tags,
    graphify_units_refs_wired: probe.graphify_units_refs_wired,
    reasons: probe.reasons,
  };
}


export function evaluateCapabilities(detected) {
  const capabilityDefs = loadCapabilities().capabilities;
  const { graphify, ctags, astGrep } = detected.enhanced;
  const providers = {
    git: detected.baseline.git.status === "pass",
    ripgrep: detected.baseline.rg.status === "pass",
    grep: detected.baseline.grep.status === "pass",
    "node-fs": true,
    graphify: graphify.available,
    "universal-ctags": ctags.available,
    "ast-grep": astGrep.available,
  };

  const capabilityState = {};
  for (const [name, def] of Object.entries(capabilityDefs)) {
    const satisfiedBy = (def.providers ?? []).filter((provider) => {
      if (provider === "graphify") {
        return graphify.available && graphify.capabilities.includes(name);
      }
      return providers[provider];
    });
    // Special-case: graphify alone can claim all deep caps when available with full capability list.
    capabilityState[name] = {
      available: satisfiedBy.length > 0,
      providers: satisfiedBy,
      definition_providers: def.providers,
      description: def.description,
    };
  }

  // Deep core three capabilities with explicit provider evidence
  const deepRequired = ["graph-queries", "symbol-enumeration", "reference-edges"];
  for (const cap of deepRequired) {
    const providersForCap = [];
    if (graphify.available && graphify.capabilities.includes(cap)) providersForCap.push("graphify");
    if (cap === "symbol-enumeration") {
      if (ctags.available) providersForCap.push("universal-ctags");
      if (astGrep.available) providersForCap.push("ast-grep");
    }
    if (cap === "reference-edges" && ctags.available) providersForCap.push("universal-ctags");
    capabilityState[cap] = {
      available: providersForCap.length > 0,
      providers: [...new Set(providersForCap)],
      definition_providers: capabilityDefs[cap]?.providers ?? [],
      description: capabilityDefs[cap]?.description ?? cap,
    };
  }

  return capabilityState;
}

export function chooseDeepEnumerator(detected, capabilityState) {
  const { graphify, ctags, astGrep } = detected.enhanced;
  // Prefer concrete symbol providers for units extraction; Graphify remains preferred for graph capabilities.
  if (ctags.available) {
    return {
      name: "universal-ctags",
      command: ctags.command,
      version: ctags.version,
      languages: ctags.languages,
      source: "supplemental_symbols",
      graph_provider: graphify.available ? "graphify" : null,
    };
  }
  if (astGrep.available) {
    return {
      name: "ast-grep",
      command: astGrep.command,
      version: astGrep.version,
      source: "supplemental_ast_search",
      graph_provider: graphify.available ? "graphify" : null,
    };
  }
  if (graphify.available && capabilityState["symbol-enumeration"]?.providers.includes("graphify")) {
    return {
      name: "graphify",
      command: graphify.command,
      version: graphify.version,
      source: "preferred_graph_provider",
      graph_provider: "graphify",
    };
  }
  return null;
}

export function modeAvailability(capabilityState, detected) {
  const modes = loadModes();
  const baselineOk =
    detected.baseline.git.status === "pass" &&
    detected.baseline.textSearch.status === "pass";
  const deepMissing = (modes.modes.deep.required_capabilities ?? []).filter(
    (cap) => !capabilityState[cap]?.available,
  );
  return {
    available_modes: [
      ...(baselineOk ? ["standard"] : []),
      ...(baselineOk && deepMissing.length === 0 ? ["deep"] : []),
    ],
    blocked_modes: [
      ...(!baselineOk ? ["standard", "deep"] : deepMissing.length > 0 ? ["deep"] : []),
    ],
    missing_capabilities: {
      standard: baselineOk ? [] : ["baseline-git/text-search"],
      deep: deepMissing,
    },
  };
}

export function buildCapabilityMatrix({ detected, capabilityState, languages = [] }) {
  const modes = loadModes();
  const tools = loadToolRules();
  const availability = modeAvailability(capabilityState, detected);
  const detectedTools = [
    {
      name: "git",
      available: detected.baseline.git.status === "pass",
      version: detected.baseline.git.version,
      class: "baseline",
    },
    {
      name: detected.baseline.textSearch.provider ?? "text-search",
      available: detected.baseline.textSearch.status === "pass",
      version: detected.baseline.textSearch.version,
      class: "baseline",
    },
    {
      name: "graphify",
      available: detected.enhanced.graphify.available,
      version: detected.enhanced.graphify.version,
      class: "enhanced",
      capabilities: detected.enhanced.graphify.capabilities,
    },
    {
      name: "universal-ctags",
      available: detected.enhanced.ctags.available,
      version: detected.enhanced.ctags.version,
      class: "enhanced",
    },
    {
      name: "ast-grep",
      available: detected.enhanced.astGrep.available,
      version: detected.enhanced.astGrep.version,
      class: "enhanced",
    },
  ];

  return {
    rules_version: rulesVersion(),
    default_mode: modes.default_mode,
    available_modes: availability.available_modes,
    blocked_modes: availability.blocked_modes,
    missing_capabilities: availability.missing_capabilities,
    capabilities: capabilityState,
    detected_tools: detectedTools,
    languages,
    official_source_refs: tools.map((tool) => ({
      tool_name: tool.tool_name,
      official_source_url: tool.official_source_url,
      verified_date: tool.verified_date,
      mode_usage: tool.mode_usage,
      class: tool.class,
    })),
    remediation: buildRemediation(availability, capabilityState),
  };
}

function buildRemediation(availability, capabilityState) {
  const lines = [];
  if (availability.missing_capabilities.standard?.length) {
    lines.push("安装 Git 与 ripgrep/grep 以满足 standard 基线。");
  }
  for (const cap of availability.missing_capabilities.deep ?? []) {
    if (cap === "graph-queries") lines.push("安装 Graphify（优先图提供方）以满足 graph-queries。");
    if (cap === "symbol-enumeration") {
      lines.push("安装 Graphify，或补充 Universal Ctags / ast-grep 以满足 symbol-enumeration。");
    }
    if (cap === "reference-edges") {
      lines.push(
        "deep 需要对本仓可验证的 reference edges：Universal Ctags 须在抽样源文件中产出 roles=reference；或目标仓 graphify-out/graph.json 含 EXTRACTED call/import/reference 边（units 已真实接入 refs_status）。仅安装工具但无法产出 complete refs 仍会拦截 deep，避免后续 evidence/gate 浪费 token。",
      );
    }
  }
  if (!lines.length) lines.push("当前环境已满足已检测模式的能力合同。");
  return lines;
}

export function buildInstallPrompt({ targetMode = "deep", matrix }) {
  const mode = resolveMode(targetMode);
  const missing = matrix.missing_capabilities[mode] ?? [];
  const official = matrix.official_source_refs
    .filter((item) => item.class === "enhanced" || missing.length)
    .map((item) => `- ${item.tool_name}: ${item.official_source_url} (verified ${item.verified_date})`)
    .join("\n");

  const focus = mode === "deep"
    ? missing.length
      ? `只补齐 deep 缺失能力：${missing.join(", ")}。优先使 reference-edges 在目标仓可验证：Universal Ctags 须能产出 roles=reference，或在目标仓运行 graphify update . 使 graphify-out/graph.json 含 EXTRACTED 引用边（units 已接线）。symbol-enumeration 可再补 ast-grep。`
      : "deep 能力已满足；若用户仍要安装，仅做版本确认并回报，不要重复安装。"
    : "standard 仅需 Git + 文本搜索；不要为 standard 安装 Graphify/Ctags/ast-grep。";

  return `# AI Installation Agent Prompt

目标模式: ${mode}
规则版本: ${matrix.rules_version}

## 任务
为 Repo Analyzer 配置可选增强工具，使目标模式可用。

## 范围约束（强制）
1. **不得**修改被分析仓库的源码或依赖清单（package.json / Cargo.toml / go.mod / pyproject.toml 等），除非用户对本次安装显式授权且与分析证据隔离。
2. 只安装或配置满足缺失能力所需的最小工具集；禁止为凑齐工具包盲目安装。
3. 安装后回报：命令路径、版本号、以及 doctor 能力矩阵是否放行目标模式。
4. 不要在分析 run 内把 deep 静默降级为 standard。

## 当前能力矩阵摘要
- available_modes: ${matrix.available_modes.join(", ") || "(none)"}
- blocked_modes: ${matrix.blocked_modes.join(", ") || "(none)"}
- deep missing: ${(matrix.missing_capabilities.deep ?? []).join(", ") || "(none)"}

## 安装焦点
${focus}

## 官方来源
${official || "- 见 skills/repo-analyzer/rules/tools/"}

## 验收
重新运行:
\`repo-analyzer doctor --repo <REPO> --out <OUT>\`
确认 capability matrix 中目标模式 available，且未污染被分析仓库。
`;
}

export function assertModeRunnable(mode, matrix) {
  const resolved = resolveMode(mode);
  if (!matrix.available_modes.includes(resolved)) {
    const missing = matrix.missing_capabilities[resolved] ?? [];
    const error = new Error(
      `模式 ${resolved} 不可用：缺失能力 [${missing.join(", ") || "baseline"}]。不会降级到其他模式。请查看 doctor capability matrix 或安装 prompt。`,
    );
    error.code = "MODE_BLOCKED";
    error.mode = resolved;
    error.missing = missing;
    throw error;
  }
  return resolved;
}

export function isEnhancedToolName(name) {
  return ["graphify", "universal-ctags", "ctags", "ast-grep"].includes(String(name).toLowerCase());
}

export function standardToolingPolicy() {
  return {
    allowed: ["git", "ripgrep", "grep", "node-fs", "jq"],
    forbidden: ["graphify", "universal-ctags", "ast-grep"],
    note: "standard 即使检测到增强工具也必须忽略",
  };
}
