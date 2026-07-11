import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "skills", "repo-analyzer", "rules");

export function rulesRoot() {
  return ROOT;
}

export function loadModes() {
  return JSON.parse(readFileSync(join(ROOT, "modes.json"), "utf8"));
}

export function loadCapabilities() {
  return JSON.parse(readFileSync(join(ROOT, "capabilities.json"), "utf8"));
}

export function loadToolRules() {
  const dir = join(ROOT, "tools");
  return readdirSync(dir)
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map((name) => JSON.parse(readFileSync(join(dir, name), "utf8")));
}

export function rulesVersion() {
  return loadModes().rules_version;
}

export function defaultMode() {
  return loadModes().default_mode;
}

export function supportedModes() {
  return Object.keys(loadModes().modes);
}

export function resolveMode(mode) {
  const modes = loadModes();
  const resolved = mode ?? modes.default_mode;
  if (!modes.modes[resolved]) {
    throw new Error(`未知分析模式: ${resolved}；可选 ${supportedModes().join("、")}。`);
  }
  return resolved;
}
