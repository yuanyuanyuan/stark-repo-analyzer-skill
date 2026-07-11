import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

import { cli, createFixture } from "./helpers.js";

function passDoctor(fixture) {
  const result = cli("doctor", {
    ...fixture,
    env: {
      REPO_ANALYZER_CTAGS: "/missing/ctags",
      REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
      REPO_ANALYZER_GRAPHIFY: "/missing/graphify",
    },
    options: { mode: "standard" },
  });
  assert.equal(result.status, 0);
}

test("scan 在 Doctor 未放行时拒绝扫描", () => {
  const fixture = createFixture();
  const result = cli("scan", fixture);

  assert.equal(result.status, 1);
  assert.match(result.stderr, /doctor.*未放行/i);
});

test("scan 不接受为其他仓库生成的 Doctor 报告", () => {
  const first = createFixture();
  const second = createFixture();
  passDoctor(first);

  const result = cli("scan", { ...second, out: first.out });

  assert.equal(result.status, 1);
  assert.match(result.stderr, /报告与当前.*不匹配/);
});

test("scan 生成可审计的候选仓库地图", () => {
  const fixture = createFixture();
  passDoctor(fixture);

  const result = cli("scan", fixture);

  assert.equal(result.status, 0);
  const map = JSON.parse(readFileSync(join(fixture.out, "repo-map.json"), "utf8"));
  assert.equal(map.schema_version, 1);
  assert.equal(map.commit.length, 40);
  assert.deepEqual(map.dependencies, [{ manifest: "package.json", scope: "runtime", name: "hono", version: "^4.0.0" }]);
  assert.ok(map.files.source.includes("src/index.js"));
  assert.ok(map.files.docs.includes("docs/architecture.md"));
  assert.ok(map.files.test.includes("test/service.test.js"));
  assert.ok(map.files.generated.includes("generated/client.js"));
  assert.ok(map.files.vendor.includes("vendor/lib.js"));
  assert.ok(map.entry_candidates.some((item) => item.file === "src/index.js"));
  assert.ok(map.risk_candidates.every((item) => item.signal && item.source));
  assert.equal("architecture" in map, false);
});

test("summarize 稳定生成只含候选信号和待验证问题的 Markdown", () => {
  const fixture = createFixture();
  passDoctor(fixture);
  assert.equal(cli("scan", fixture).status, 0);

  const first = cli("summarize", fixture);
  const firstContent = readFileSync(join(fixture.out, "repo-map.md"), "utf8");
  const second = cli("summarize", fixture);
  const secondContent = readFileSync(join(fixture.out, "repo-map.md"), "utf8");

  assert.equal(first.status, 0);
  assert.equal(second.status, 0);
  assert.equal(firstContent, secondContent);
  assert.match(firstContent, /候选入口/);
  assert.match(firstContent, /排除范围候选/);
  assert.match(firstContent, /待验证问题/);
  assert.match(firstContent, /来源：`repo-map\.json`/);
  assert.doesNotMatch(firstContent, /系统采用|架构是|必然/);
});

test("scan 直接从 Cargo 和 Python manifest 派生依赖", () => {
  const fixture = createFixture();
  writeFileSync(join(fixture.repo, "Cargo.toml"), '[dependencies]\nserde = "1.0"\n[dev-dependencies]\ninsta = { version = "1.39" }\n');
  writeFileSync(join(fixture.repo, "pyproject.toml"), '[project]\ndependencies = ["httpx>=0.27"]\n[tool.poetry.dependencies]\npython = "^3.11"\nrich = "^13"\n');
  passDoctor(fixture);

  assert.equal(cli("scan", fixture).status, 0);
  const map = JSON.parse(readFileSync(join(fixture.out, "repo-map.json"), "utf8"));
  assert.ok(map.dependencies.some((item) => item.manifest === "Cargo.toml" && item.name === "serde" && item.version === "1.0"));
  assert.ok(map.dependencies.some((item) => item.manifest === "Cargo.toml" && item.name === "insta" && item.scope === "development"));
  assert.ok(map.dependencies.some((item) => item.manifest === "pyproject.toml" && item.name === "httpx" && item.version === ">=0.27"));
  assert.ok(map.dependencies.some((item) => item.manifest === "pyproject.toml" && item.name === "rich" && item.version === "^13"));
});
