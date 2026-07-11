import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { basename, extname, join, resolve, sep } from "node:path";

import { readJson, runCommand, writeJson } from "./common.js";
import { LANGUAGE_BY_EXTENSION } from "./languages.js";

const DATA_KINDS = new Set(["class", "struct", "interface", "enum", "union"]);
const TYPE_KINDS = new Set(["typedef", "type", "trait"]);
const FUNCTION_KINDS = new Set(["function", "method", "procedure", "func"]);
const ENTRY_SYMBOLS = new Set(["main", "run", "start", "serve", "handler"]);
const AST_LANG = {
  ".js": "javascript",
  ".jsx": "javascript",
  ".ts": "typescript",
  ".tsx": "typescript",
  ".py": "python",
  ".go": "go",
  ".rs": "rust",
  ".java": "java",
  ".kt": "kotlin",
  ".kts": "kotlin",
  ".cs": "csharp",
};
const AST_PATTERNS = {
  javascript: [["function $NAME($$$ARGS) { $$$BODY }", "function"], ["class $NAME { $$$BODY }", "class"]],
  typescript: [["function $NAME($$$ARGS) { $$$BODY }", "function"], ["class $NAME { $$$BODY }", "class"], ["interface $NAME { $$$BODY }", "interface"]],
  python: [["def $NAME($$$ARGS): $$$BODY", "function"], ["class $NAME: $$$BODY", "class"]],
  go: [["func $NAME($$$ARGS) { $$$BODY }", "function"], ["type $NAME struct { $$$BODY }", "struct"], ["type $NAME interface { $$$BODY }", "interface"]],
  rust: [["fn $NAME($$$ARGS) { $$$BODY }", "function"], ["struct $NAME { $$$BODY }", "struct"], ["enum $NAME { $$$BODY }", "enum"]],
  java: [["class $NAME { $$$BODY }", "class"], ["interface $NAME { $$$BODY }", "interface"]],
  kotlin: [["fun $NAME($$$ARGS) { $$$BODY }", "function"], ["class $NAME { $$$BODY }", "class"], ["interface $NAME { $$$BODY }", "interface"]],
  csharp: [["class $NAME { $$$BODY }", "class"], ["interface $NAME { $$$BODY }", "interface"]],
};

function normalize(path) {
  return path.split(sep).join("/");
}

function stableId(file, symbol, type, kind) {
  const seed = `${file}:${symbol}:${type}:${kind}`;
  return `${file}:${symbol}:${type}:${createHash("sha256").update(seed).digest("hex").slice(0, 12)}`;
}

function parseJsonLines(stdout) {
  const values = [];
  for (const line of stdout.split(/\r?\n/)) {
    if (!line.trim()) continue;
    try {
      values.push(JSON.parse(line));
    } catch {
      // A successful enumerator may emit non-tag diagnostics; they do not become denominator entries.
    }
  }
  return values;
}

function ctagsTags(command, repo, file) {
  const absolute = join(repo, file);
  const result = runCommand(command, ["--output-format=json", "--fields=+nK", "--extras=+r", "--sort=no", "-f", "-", absolute]);
  if (!result.ok) return { ok: false, tags: [] };
  return {
    ok: true,
    tags: parseJsonLines(result.stdout)
      .filter((tag) => tag._type === "tag" && tag.name)
      .map((tag) => ({
        name: tag.name,
        line: Number(tag.line ?? 1),
        kind: String(tag.kind ?? tag.kindName ?? "symbol").toLowerCase(),
        reference: String(tag.roles ?? "").split(",").includes("reference"),
        raw: tag,
      })),
  };
}

function astGrepTags(command, repo, file) {
  const language = AST_LANG[extname(file).toLowerCase()];
  if (!language) return { ok: false, tags: [] };
  const patterns = AST_PATTERNS[language] ?? [];
  const tags = [];
  let succeeded = false;
  for (const [pattern, kind] of patterns) {
    const result = runCommand(command, ["--lang", language, "--pattern", pattern, "--json=stream", join(repo, file)]);
    if (!result.ok) continue;
    succeeded = true;
    for (const match of parseJsonLines(result.stdout)) {
      const name = match.metaVariables?.single?.NAME?.text ?? match.metaVariables?.NAME?.text;
      if (!name) continue;
      tags.push({
        name,
        line: Number(match.range?.start?.line ?? 0) + 1,
        kind,
        reference: false,
        raw: match,
      });
    }
  }
  return { ok: succeeded, tags };
}

function sourceLine(repo, file, line) {
  try {
    return readFileSync(join(repo, file), "utf8").split(/\r?\n/)[line - 1] ?? "";
  } catch {
    return "";
  }
}

function unitType(tag, file, lineText) {
  if (ENTRY_SYMBOLS.has(tag.name.toLowerCase()) || /^(index|main|app|server|cli)\./i.test(basename(file))) return "entrypoint";
  if (DATA_KINDS.has(tag.kind)) return "datastruct";
  if (TYPE_KINDS.has(tag.kind)) return "type";
  if (/\b(state|store|reducer)\b/i.test(tag.name)) return "state";
  if (/\b(config|settings|options)\b/i.test(tag.name)) return "config";
  if (/\b(export|public|pub)\b/.test(lineText) || FUNCTION_KINDS.has(tag.kind)) return "export";
  return null;
}

function findRefs(repo, sourceFiles, symbol, definitionFile, definitionLine, searchCommand) {
  const isRg = basename(searchCommand).includes("rg");
  const args = isRg ? ["-n", "-w", "--fixed-strings", symbol, ...sourceFiles] : ["-n", "-w", "-F", symbol, ...sourceFiles];
  const result = runCommand(searchCommand, args, { cwd: repo });
  if (!result.ok && !result.stdout) return [];
  const sourceSet = new Set(sourceFiles);
  const refs = [];
  for (const line of result.stdout.split(/\r?\n/)) {
    const match = line.match(/^(.+?):(\d+):(.*)$/);
    if (!match) continue;
    const file = normalize(match[1]);
    const lineNumber = Number(match[2]);
    if (!sourceSet.has(file) || (file === definitionFile && lineNumber === definitionLine)) continue;
    refs.push({ file, line: lineNumber, dir: "inbound", source: isRg ? "rg" : "grep", confidence: "heuristic" });
  }
  return refs.sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line);
}

function enumeratorRefs(tagsByFile, symbol, definitionFile, definitionLine) {
  const refs = [];
  for (const [file, tags] of tagsByFile) {
    for (const tag of tags) {
      if (!tag.reference || tag.name !== symbol || (file === definitionFile && tag.line === definitionLine)) continue;
      refs.push({ file, line: tag.line, dir: "inbound", source: "ctags", confidence: "exact" });
    }
  }
  return refs.sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line);
}

function modulesFromMap(map) {
  return map.module_candidates.map((candidate, index) => ({
    name: candidate.name,
    path_globs: candidate.name === "." ? ["*"] : [`${candidate.name}/**`],
    classification: index === 0 ? "core" : "secondary",
    reason: index === 0 ? "源码规模最大的模块候选" : "其余顶层源码模块候选",
    source: "repo-map.json",
  }));
}

function moduleFor(file, modules) {
  return modules.find((module) => module.name === "." ? !file.includes("/") : file === module.name || file.startsWith(`${module.name}/`))?.name ?? ".";
}

function mergeAgentFields(unit, previous) {
  if (!previous) return unit;
  return {
    ...unit,
    status: previous.status === "analyzed" ? "analyzed" : "unanalyzed",
    anchor: previous.anchor ?? null,
    judgment: previous.judgment ?? null,
    skip_reason: previous.skip_reason ?? null,
  };
}

function healthFor(files, parsedFiles) {
  const parsed = files.filter((file) => parsedFiles.has(file)).length;
  const unparsed = files.length - parsed;
  return {
    source_files: files.length,
    parsed_files: parsed,
    unparsed_files: unparsed,
    parse_rate: files.length === 0 ? 0 : parsed / files.length,
  };
}

export function units({ repo, out, doctor }) {
  const repoPath = resolve(repo);
  const map = readJson(join(out, "repo-map.json"));
  const enumerator = doctor.enumerator;
  if (!enumerator || !runCommand(enumerator.command, ["--version"]).ok) {
    throw new Error("符号枚举器当前不可用；请修复 universal-ctags 或 ast-grep 后重跑 doctor。");
  }
  const searchCommand = doctor.checks.find((check) => check.id === "text-search")?.command;

  const modules = modulesFromMap(map);
  const parsed = [];
  const unparsed = [];
  const discovered = [];
  const tagsByFile = new Map();
  for (const file of map.files.source) {
    const result = enumerator.name === "universal-ctags"
      ? ctagsTags(enumerator.command, repoPath, file)
      : astGrepTags(enumerator.command, repoPath, file);
    if (!result.ok) {
      unparsed.push(file);
      continue;
    }
    parsed.push(file);
    tagsByFile.set(file, result.tags);
  }
  for (const [file, tags] of tagsByFile) {
    for (const tag of tags.filter((item) => !item.reference)) {
      const lineText = sourceLine(repoPath, file, tag.line);
      const type = unitType(tag, file, lineText);
      if (!type) continue;
      const exactRefs = enumerator.name === "universal-ctags" ? enumeratorRefs(tagsByFile, tag.name, file, tag.line) : [];
      const refs = exactRefs.length > 0 || !searchCommand ? exactRefs : findRefs(repoPath, map.files.source, tag.name, file, tag.line, searchCommand);
      discovered.push({
        id: stableId(file, tag.name, type, tag.kind),
        file,
        line: tag.line,
        symbol: tag.name,
        type,
        module: moduleFor(file, modules),
        refs,
        refs_status: exactRefs.length > 0 ? "complete" : refs.length > 0 ? "partial" : "missing",
        status: "unanalyzed",
        anchor: null,
        judgment: null,
        skip_reason: null,
      });
    }
  }

  let previousById = new Map();
  const artifactPath = join(out, "coverage-units.json");
  if (existsSync(artifactPath)) {
    try {
      const previous = readJson(artifactPath);
      if (previous.repo?.commit === map.commit) previousById = new Map(previous.units.map((unit) => [unit.id, unit]));
    } catch {
      previousById = new Map();
    }
  }
  const allParsed = [...parsed].sort();
  const allUnparsed = [...unparsed].sort();
  const parsedFiles = new Set(allParsed);
  const health = healthFor(map.files.source, parsedFiles);
  const largestLanguageSize = map.languages[0]?.lines ?? 0;
  const primaryLanguages = map.languages.filter((language) => language.lines === largestLanguageSize).map((language) => language.language);
  const primaryFiles = map.files.source.filter((file) => primaryLanguages.includes(LANGUAGE_BY_EXTENSION[extname(file).toLowerCase()]));
  const primaryHealth = healthFor(primaryFiles, parsedFiles);
  const report = {
    schema_version: 1,
    repo: { path: repoPath, commit: map.commit, skill_version: "2.0.0", mode: null },
    modules,
    units: discovered
      .sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line || a.symbol.localeCompare(b.symbol))
      .map((unit) => mergeAgentFields(unit, previousById.get(unit.id))),
    parsed: allParsed,
    unparsed: allUnparsed,
    parse_rate: health.parse_rate,
    parse_health: {
      ...health,
      primary_languages: primaryLanguages,
      primary: primaryHealth,
    },
    enumerator: { name: enumerator.name, version: enumerator.version },
  };
  writeJson(artifactPath, report);
  return report;
}
