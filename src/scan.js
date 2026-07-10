import { readFileSync, readdirSync } from "node:fs";
import { basename, dirname, extname, join, relative, resolve, sep } from "node:path";

import { LANGUAGE_BY_EXTENSION } from "./languages.js";
import { runCommand, writeJson } from "./common.js";

const MANIFESTS = new Set(["package.json", "Cargo.toml", "go.mod", "pyproject.toml", "requirements.txt"]);
const ENTRY_NAMES = /^(index|main|app|server|cli|mod|lib)\.[^.]+$/i;
const DOC_NAMES = /^(readme|architecture|design|contributing|changelog)(\.|$)/i;
const CONFIG_NAMES = /(^|\.)(config|rc)(\.|$)|^(dockerfile|makefile|justfile)$/i;
const TEST_SEGMENT = /^(test|tests|spec|specs|__tests__)$/i;
const GENERATED_SEGMENT = /^(generated|dist|build|coverage|target)$/i;
const VENDOR_SEGMENT = /^(vendor|node_modules|third_party)$/i;
const RISK_SIGNAL = /(auth|permission|security|cache|concurr|worker|queue|plugin|extension|config|error|retry|migration)/i;

function normalize(path) {
  return path.split(sep).join("/");
}

function listFiles(root, excludedDirectory) {
  const files = [];
  const visit = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      if (entry.name === ".git") continue;
      const path = join(directory, entry.name);
      if (resolve(path) === excludedDirectory) continue;
      if (entry.isDirectory()) visit(path);
      if (entry.isFile()) files.push(normalize(relative(root, path)));
    }
  };
  visit(root);
  return files;
}

function classify(file) {
  const segments = file.split("/");
  const name = basename(file);
  if (segments.some((segment) => VENDOR_SEGMENT.test(segment))) return "vendor";
  if (segments.some((segment) => GENERATED_SEGMENT.test(segment)) || /\.(min|generated)\./i.test(name)) return "generated";
  if (segments.some((segment) => TEST_SEGMENT.test(segment)) || /\.(test|spec)\.[^.]+$/i.test(name)) return "test";
  if (segments.includes("docs") || DOC_NAMES.test(name) || /\.(md|mdx|rst|adoc)$/i.test(name)) return "docs";
  if (LANGUAGE_BY_EXTENSION[extname(name).toLowerCase()]) return "source";
  return "other";
}

function lineCount(path) {
  const content = readFileSync(path, "utf8");
  if (!content) return 0;
  return content.split(/\r?\n/).length - (content.endsWith("\n") ? 1 : 0);
}

function packageDependencies(path, file) {
  if (basename(file) !== "package.json") return [];
  let manifest;
  try {
    manifest = JSON.parse(readFileSync(path, "utf8"));
  } catch {
    return [];
  }
  const scopes = [
    ["dependencies", "runtime"],
    ["devDependencies", "development"],
    ["peerDependencies", "peer"],
    ["optionalDependencies", "optional"],
  ];
  return scopes.flatMap(([key, scope]) =>
    Object.entries(manifest[key] ?? {}).map(([name, version]) => ({ manifest: file, scope, name, version })),
  );
}

function otherDependencies(path, file) {
  const content = readFileSync(path, "utf8");
  if (basename(file) === "requirements.txt") {
    return content.split(/\r?\n/).filter((line) => line && !line.startsWith("#")).map((line) => {
      const match = line.match(/^([^<>=!~\s]+)\s*(.*)$/);
      return { manifest: file, scope: "runtime", name: match?.[1] ?? line, version: match?.[2] || null };
    });
  }
  if (basename(file) === "go.mod") {
    return [...content.matchAll(/^\s*([^\s()]+)\s+(v[^\s]+)\s*$/gm)]
      .filter((match) => match[1] !== "module" && match[1] !== "go")
      .map((match) => ({ manifest: file, scope: "runtime", name: match[1], version: match[2] }));
  }
  if (basename(file) === "Cargo.toml") {
    const dependencies = [];
    let scope = null;
    for (const line of content.split(/\r?\n/)) {
      const section = line.match(/^\s*\[([^\]]+)]\s*$/)?.[1];
      if (section) {
        scope = section === "dependencies" ? "runtime" : section === "dev-dependencies" ? "development" : section === "build-dependencies" ? "build" : null;
        continue;
      }
      if (!scope) continue;
      const match = line.match(/^\s*([A-Za-z0-9_-]+)\s*=\s*(?:"([^"]+)"|\{[^}]*version\s*=\s*"([^"]+)"[^}]*})/);
      if (match) dependencies.push({ manifest: file, scope, name: match[1], version: match[2] ?? match[3] });
    }
    return dependencies;
  }
  if (basename(file) === "pyproject.toml") {
    const dependencies = [];
    const projectBlock = content.match(/\[project]\s*([\s\S]*?)(?=\n\[|$)/)?.[1] ?? "";
    const array = projectBlock.match(/dependencies\s*=\s*\[([\s\S]*?)]/)?.[1] ?? "";
    for (const match of array.matchAll(/["']([^"']+)["']/g)) {
      const parsed = match[1].match(/^([A-Za-z0-9_.-]+)\s*(.*)$/);
      dependencies.push({ manifest: file, scope: "runtime", name: parsed?.[1] ?? match[1], version: parsed?.[2] || null });
    }
    const poetryBlock = content.match(/\[tool\.poetry\.dependencies]\s*([\s\S]*?)(?=\n\[|$)/)?.[1] ?? "";
    for (const line of poetryBlock.split(/\r?\n/)) {
      const match = line.match(/^\s*([A-Za-z0-9_.-]+)\s*=\s*(?:"([^"]+)"|\{[^}]*version\s*=\s*"([^"]+)"[^}]*})/);
      if (match && match[1].toLowerCase() !== "python") {
        dependencies.push({ manifest: file, scope: "runtime", name: match[1], version: match[2] ?? match[3] });
      }
    }
    return dependencies;
  }
  return [];
}

function moduleName(file) {
  const directory = dirname(file);
  return directory === "." ? "." : directory.split("/")[0];
}

export function scan({ repo, out }) {
  const repoPath = resolve(repo);
  const files = listFiles(repoPath, resolve(out));
  const buckets = { source: [], docs: [], test: [], generated: [], vendor: [], other: [] };
  const languageMap = new Map();
  const moduleMap = new Map();
  const manifests = [];
  const dependencies = [];

  for (const file of files) {
    const category = classify(file);
    buckets[category].push(file);
    const path = join(repoPath, file);
    const lines = category === "source" ? lineCount(path) : 0;
    const language = LANGUAGE_BY_EXTENSION[extname(file).toLowerCase()];
    if (language && category === "source") {
      const current = languageMap.get(language) ?? { language, files: 0, lines: 0 };
      current.files += 1;
      current.lines += lines;
      languageMap.set(language, current);
      const module = moduleName(file);
      const moduleData = moduleMap.get(module) ?? { name: module, source_files: 0, lines: 0, signal: "top-level source path" };
      moduleData.source_files += 1;
      moduleData.lines += lines;
      moduleMap.set(module, moduleData);
    }
    if (MANIFESTS.has(basename(file))) {
      manifests.push(file);
      dependencies.push(...packageDependencies(path, file), ...otherDependencies(path, file));
    }
  }

  const commit = runCommand("git", ["rev-parse", "HEAD"], { cwd: repoPath });
  const report = {
    schema_version: 1,
    repo: repoPath,
    commit: commit.ok ? commit.stdout : null,
    generated_by: "repo-analyzer scan",
    files: buckets,
    languages: [...languageMap.values()].sort((a, b) => b.lines - a.lines || a.language.localeCompare(b.language)),
    module_candidates: [...moduleMap.values()].sort((a, b) => b.lines - a.lines || a.name.localeCompare(b.name)),
    manifests: manifests.sort(),
    dependencies: dependencies.sort((a, b) => a.manifest.localeCompare(b.manifest) || a.scope.localeCompare(b.scope) || a.name.localeCompare(b.name)),
    entry_candidates: buckets.source.filter((file) => ENTRY_NAMES.test(basename(file))).map((file) => ({ file, signal: "entry-like filename", source: "filename" })),
    document_candidates: buckets.docs.map((file) => ({ file, signal: "documentation path or extension", source: "path" })),
    config_candidates: files.filter((file) => CONFIG_NAMES.test(basename(file))).map((file) => ({ file, signal: "configuration-like filename", source: "filename" })),
    risk_candidates: files.filter((file) => RISK_SIGNAL.test(file)).map((file) => ({ file, signal: "risk-related path keyword", source: "path" })),
    exclusions: {
      test: buckets.test,
      generated: buckets.generated,
      vendor: buckets.vendor,
    },
  };
  writeJson(join(out, "repo-map.json"), report);
  return report;
}
