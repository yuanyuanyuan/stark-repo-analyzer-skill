import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import test from "node:test";

test("发布包包含 v2 运行时且排除本机配置和测试证据", () => {
  const output = execFileSync("npm", ["pack", "--dry-run", "--json"], { encoding: "utf8" });
  const [report] = JSON.parse(output);
  const files = report.files.map((item) => item.path);

  assert.ok(files.includes("bin/repo-analyzer.js"));
  assert.ok(files.includes("src/gate.js"));
  assert.ok(files.includes("skills/repo-analyzer/references/evidence-first-v2.md"));
  assert.ok(files.includes("CHANGELOG.md"));
  assert.ok(files.every((file) => !file.startsWith("test/") && !file.startsWith("测试证据/")));
  assert.ok(files.every((file) => !file.includes(".codex") && !file.includes(".claude/settings")));
});
