import { basename } from "node:path";

import { loadCapabilities, loadModes, loadToolRules, resolveMode, rulesVersion } from "./rules.js";
import { runCommand } from "./common.js";

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
      lines.push("安装 Graphify，或使用支持 reference 的 Universal Ctags 以满足 reference-edges。");
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
      ? `只补齐 deep 缺失能力：${missing.join(", ")}。优先 Graphify；仅在 Graphify 无法覆盖 symbol-enumeration / reference-edges 时补充 Universal Ctags 或 ast-grep。`
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
