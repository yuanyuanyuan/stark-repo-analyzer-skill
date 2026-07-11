import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

export function parseArgs(args) {
  const [command, ...rest] = args;
  const options = {};
  const flags = {};
  const booleanFlags = new Set(["install-prompt", "help"]);
  for (let index = 0; index < rest.length; index += 1) {
    const item = rest[index];
    if (!item.startsWith("--")) {
      throw new Error(`无法识别的参数: ${item}`);
    }
    const key = item.slice(2);
    if (booleanFlags.has(key)) {
      flags[key] = true;
      continue;
    }
    const value = rest[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`参数 --${key} 缺少值`);
    }
    options[key] = value;
    index += 1;
  }
  return { command, options, flags };
}

export function runCommand(command, args = [], options = {}) {
  try {
    return {
      ok: true,
      stdout: execFileSync(command, args, {
        cwd: options.cwd,
        encoding: "utf8",
        env: { ...process.env, NODE_OPTIONS: "", ...(options.env ?? {}) },
        stdio: ["ignore", "pipe", "pipe"],
        timeout: options.timeout ?? 60_000,
      }).trim(),
    };
  } catch (error) {
    return {
      ok: false,
      stdout: error.stdout?.toString().trim() ?? "",
      stderr: error.stderr?.toString().trim() ?? error.message,
    };
  }
}

export function writeJson(path, value) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

export function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

export function requiredPath(options, name) {
  const value = options[name];
  if (!value) {
    throw new Error(`缺少必需参数 --${name}`);
  }
  return resolve(value);
}

export function requireDoctor(repo, out, mode = "standard") {
  const reportPath = join(out, "doctor-report.json");
  let report;
  try {
    report = readJson(reportPath);
  } catch {
    throw new Error(`Doctor 未放行：请先运行 doctor 生成 ${reportPath}`);
  }
  if (resolve(report.repo) !== resolve(repo) || resolve(report.output) !== resolve(out)) {
    throw new Error("Doctor 报告与当前 --repo/--out 不匹配；请针对当前目标重新运行 doctor。");
  }
  const standardOk = report.allowed_standard ?? report.allowed;
  const deepOk = report.allowed_deep ?? false;
  if (mode === "deep") {
    if (!deepOk) {
      throw new Error("Doctor 未放行 deep：缺失能力合同，拒绝执行且不降级。请查看 capability matrix / install-prompt.md。");
    }
  } else if (!standardOk) {
    throw new Error("Doctor 未放行：修复 doctor-report.json 中的必需检查后重跑 doctor。");
  }
  return report;
}
