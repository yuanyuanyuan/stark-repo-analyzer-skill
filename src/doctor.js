import { accessSync, constants, existsSync, readdirSync, statSync } from "node:fs";
import { extname, join, resolve } from "node:path";

import { AST_GREP_LANGUAGES, LANGUAGE_BY_EXTENSION } from "./languages.js";
import { runCommand, writeJson } from "./common.js";

function executable(envName, fallback) {
  return process.env[envName] ?? fallback;
}

function commandCheck(id, command, args, remediation, required = true) {
  const result = runCommand(command, args);
  return {
    id,
    required,
    status: result.ok ? "pass" : "fail",
    command,
    version: result.ok ? result.stdout.split("\n")[0] : null,
    remediation: result.ok ? null : remediation,
  };
}

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

function detectCtags(command) {
  const version = runCommand(command, ["--version"]);
  if (!version.ok || !/Universal Ctags/i.test(version.stdout)) return null;
  const languages = runCommand(command, ["--list-languages"]);
  return {
    name: "universal-ctags",
    command,
    version: version.stdout.split("\n")[0],
    languages: languages.ok ? languages.stdout.split("\n").filter(Boolean) : [],
  };
}

function detectAstGrep(command) {
  const version = runCommand(command, ["--version"]);
  if (!version.ok) return null;
  return {
    name: "ast-grep",
    command,
    version: version.stdout.split("\n")[0],
    languages: [...AST_GREP_LANGUAGES],
  };
}

export function doctor({ repo, out }) {
  const repoPath = resolve(repo);
  const outPath = resolve(out);
  if (!existsSync(repoPath) || !statSync(repoPath).isDirectory()) {
    throw new Error(`目标仓库不存在或不是目录: ${repoPath}`);
  }

  const languages = walkLanguages(repoPath);
  const checks = [];
  checks.push(commandCheck("git", executable("REPO_ANALYZER_GIT", "git"), ["--version"], "安装 Git，并确保 git 位于 PATH。"));

  const rg = commandCheck("text-search-rg", executable("REPO_ANALYZER_RG", "rg"), ["--version"], "安装 ripgrep，或确保 grep 可用。", false);
  const grep = commandCheck("text-search-grep", executable("REPO_ANALYZER_GREP", "grep"), ["--version"], "安装 grep 或 ripgrep。", false);
  checks.push({
    id: "text-search",
    required: true,
    status: rg.status === "pass" || grep.status === "pass" ? "pass" : "fail",
    command: rg.status === "pass" ? rg.command : grep.command,
    version: rg.status === "pass" ? rg.version : grep.version,
    remediation: rg.status === "fail" && grep.status === "fail" ? "安装 ripgrep 或 grep，并确保命令位于 PATH。" : null,
  });

  const ctags = detectCtags(executable("REPO_ANALYZER_CTAGS", "ctags"));
  const astGrep = detectAstGrep(executable("REPO_ANALYZER_AST_GREP", "ast-grep"));
  const primaryLanguages = languages.length === 0 ? [] : languages.filter(({ files }) => files === languages[0].files);
  const supportsPrimary = (candidate) => candidate && primaryLanguages.every(({ language }) =>
    candidate.languages.some((item) => item.toLowerCase() === language.toLowerCase()));
  const enumerator = [ctags, astGrep].find(supportsPrimary) ?? ctags ?? astGrep;
  checks.push({
    id: "symbol-enumerator",
    required: true,
    status: enumerator ? "pass" : "fail",
    command: enumerator?.command ?? null,
    version: enumerator?.version ?? null,
    remediation: enumerator ? null : "安装 universal-ctags 或 ast-grep，然后重新运行 doctor。",
  });

  const unsupportedLanguages = enumerator
    ? primaryLanguages.filter(({ language }) => !enumerator.languages.some((item) => item.toLowerCase() === language.toLowerCase()))
    : primaryLanguages;
  checks.push({
    id: "language-support",
    required: true,
    status: languages.length > 0 && unsupportedLanguages.length === 0 ? "pass" : "fail",
    languages,
    primary_languages: primaryLanguages.map(({ language }) => language),
    unsupported: unsupportedLanguages.map(({ language }) => language),
    remediation:
      languages.length === 0
        ? "目标仓库中未识别到受支持的源码语言，请确认仓库路径或扩展语言映射。"
        : unsupportedLanguages.length > 0
          ? `当前枚举器不支持: ${unsupportedLanguages.map(({ language }) => language).join(", ")}。请安装支持这些语言的枚举器。`
          : null,
  });

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
  checks.push({
    id: "output-writable",
    required: true,
    status: writable ? "pass" : "fail",
    path: outPath,
    remediation: writable ? null : `授予输出目录写权限: chmod u+w ${outPath}`,
  });

  const graphify = commandCheck(
    "graphify",
    executable("REPO_ANALYZER_GRAPHIFY", "graphify"),
    ["--version"],
    "可选：安装 graphify 以增强跨文件关系查询。",
    false,
  );
  checks.push(graphify);

  const allowed = checks.filter((check) => check.required).every((check) => check.status === "pass");
  const report = {
    schema_version: 1,
    repo: repoPath,
    output: outPath,
    allowed,
    enumerator,
    checks,
  };
  writeJson(join(outPath, "doctor-report.json"), report);
  return report;
}
