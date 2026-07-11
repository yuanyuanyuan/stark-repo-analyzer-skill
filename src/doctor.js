import { accessSync, constants, existsSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { extname, join, resolve } from "node:path";

import {
  buildCapabilityMatrix,
  buildInstallPrompt,
  chooseDeepEnumerator,
  detectTools,
  evaluateCapabilities,
} from "./capabilities.js";
import { writeJson } from "./common.js";
import { AST_GREP_LANGUAGES, LANGUAGE_BY_EXTENSION } from "./languages.js";
import { defaultMode, resolveMode, rulesVersion } from "./rules.js";

function walkLanguages(root) {
  const counts = new Map();
  const visit = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      if ([".git", "node_modules", "vendor"].includes(entry.name)) continue;
      const path = join(directory, entry.name);
      if (entry.isDirectory()) visit(path);
      if (entry.isFile()) {
        const language = LANGUAGE_BY_EXTENSION[extname(entry.name).toLowerCase()];
        if (language) counts.set(language, (counts.get(language) ?? 0) + 1);
      }
    }
  };
  visit(root);
  return [...counts.entries()]
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
    .map(([language, files]) => ({ language, files }));
}

function writableCheck(outPath) {
  let writable = true;
  try {
    accessSync(outPath, constants.W_OK);
  } catch {
    try {
      accessSync(resolve(outPath, ".."), constants.W_OK);
    } catch {
      writable = false;
    }
  }
  return {
    id: "output-writable",
    required: true,
    status: writable ? "pass" : "fail",
    path: outPath,
    remediation: writable ? null : `授予输出目录写权限: chmod u+w ${outPath}`,
  };
}

export function doctor({ repo, out, mode, printInstallPrompt = false, installTargetMode }) {
  const repoPath = resolve(repo);
  const outPath = resolve(out);
  if (!existsSync(repoPath) || !statSync(repoPath).isDirectory()) {
    throw new Error(`目标仓库不存在或不是目录: ${repoPath}`);
  }

  const targetMode = resolveMode(mode ?? defaultMode());
  const languages = walkLanguages(repoPath);
  const detected = detectTools();
  // Annotate ast-grep languages for language support diagnostics in deep.
  if (detected.enhanced.astGrep.available) {
    detected.enhanced.astGrep.languages = [...AST_GREP_LANGUAGES];
  }
  const capabilityState = evaluateCapabilities(detected);
  const matrix = buildCapabilityMatrix({ detected, capabilityState, languages });
  let deepEnumerator = chooseDeepEnumerator(detected, capabilityState);
  const primaryLanguages = languages.length === 0 ? [] : languages.filter(({ files }) => files === languages[0].files);
  const supportsPrimary = (candidate) => candidate && primaryLanguages.every(({ language }) =>
    (candidate.languages ?? []).some((item) => item.toLowerCase() === language.toLowerCase())
    || candidate.name === "ast-grep"
    || candidate.name === "graphify"
  );
  if (deepEnumerator && !supportsPrimary(deepEnumerator) && detected.enhanced.astGrep.available) {
    deepEnumerator = {
      name: "ast-grep",
      command: detected.enhanced.astGrep.command,
      version: detected.enhanced.astGrep.version,
      languages: detected.enhanced.astGrep.languages ?? [],
      source: "supplemental_ast_search",
      graph_provider: detected.enhanced.graphify.available ? "graphify" : null,
    };
  }

  const checks = [];
  checks.push({
    id: "git",
    required: true,
    status: detected.baseline.git.status,
    command: detected.baseline.git.command,
    version: detected.baseline.git.version,
    remediation: detected.baseline.git.remediation,
  });
  checks.push({
    id: "text-search",
    required: true,
    status: detected.baseline.textSearch.status,
    command: detected.baseline.textSearch.command,
    version: detected.baseline.textSearch.version,
    remediation: detected.baseline.textSearch.remediation,
  });
  checks.push(writableCheck(outPath));

  // Enhanced tools: always detected, never required for standard baseline allow.
  checks.push({
    id: "graphify",
    required: false,
    status: detected.enhanced.graphify.available ? "pass" : "fail",
    command: detected.enhanced.graphify.command,
    version: detected.enhanced.graphify.version,
    remediation: detected.enhanced.graphify.available
      ? null
      : "可选（deep 优先）：安装 graphify 以满足 graph-queries / 可能的 symbol 与 reference 能力。",
    mode_usage: { standard: "forbidden_ignore", deep: "preferred_graph_provider" },
  });
  checks.push({
    id: "symbol-enumerator",
    required: false,
    status: deepEnumerator ? "pass" : "fail",
    command: deepEnumerator?.command ?? null,
    version: deepEnumerator?.version ?? null,
    remediation: deepEnumerator
      ? null
      : "deep 补充：安装 universal-ctags 或 ast-grep（当 Graphify 未覆盖 symbol-enumeration 时）。",
    mode_usage: { standard: "forbidden_ignore", deep: "supplemental" },
  });

  // language-support is informational for deep enumerator fitness; not a baseline hard fail for standard.
  let languageStatus = "pass";
  let languageRemediation = null;
  const unsupported = [];
  if (languages.length === 0) {
    languageStatus = "fail";
    languageRemediation = "目标仓库中未识别到受支持的源码语言，请确认仓库路径或扩展语言映射。";
  } else if (deepEnumerator?.name === "universal-ctags") {
    for (const { language } of primaryLanguages) {
      if (!deepEnumerator.languages?.some((item) => item.toLowerCase() === language.toLowerCase())) {
        unsupported.push(language);
      }
    }
    if (unsupported.length) {
      languageStatus = "fail";
      languageRemediation = `当前枚举器不支持: ${unsupported.join(", ")}。请安装支持这些语言的枚举器。`;
    }
  }
  checks.push({
    id: "language-support",
    required: false,
    status: languageStatus,
    languages,
    primary_languages: primaryLanguages.map(({ language }) => language),
    unsupported,
    remediation: languageRemediation,
  });

  // Baseline allowed = standard runnable (git + text search + writable). Deep is separate.
  const baselineAllowed = checks
    .filter((check) => check.required)
    .every((check) => check.status === "pass");
  const deepAllowed = baselineAllowed && matrix.available_modes.includes("deep");
  const modeAllowed = targetMode === "deep" ? deepAllowed : baselineAllowed;

  const installPrompt = buildInstallPrompt({
    targetMode: installTargetMode ?? (targetMode === "standard" ? "deep" : targetMode),
    matrix,
  });

  const report = {
    schema_version: 2,
    repo: repoPath,
    output: outPath,
    rules_version: rulesVersion(),
    mode: targetMode,
    tooling_level: targetMode === "deep" ? "enhanced" : "baseline",
    allowed: modeAllowed,
    allowed_standard: baselineAllowed,
    allowed_deep: deepAllowed,
    // enumerator is only meaningful for deep/units enhanced path; standard must ignore it.
    enumerator: targetMode === "deep" ? deepEnumerator : null,
    deep_enumerator: deepEnumerator,
    standard_policy: {
      ignores_enhanced_tools: true,
      forbidden: ["graphify", "universal-ctags", "ast-grep"],
    },
    capability_matrix: matrix,
    capability_state: matrix.capabilities,
    checks,
    install_prompt_path: join(outPath, "install-prompt.md"),
  };

  writeJson(join(outPath, "doctor-report.json"), report);
  writeFileSync(join(outPath, "install-prompt.md"), installPrompt);
  if (printInstallPrompt) {
    process.stdout.write(installPrompt);
  }
  return report;
}
