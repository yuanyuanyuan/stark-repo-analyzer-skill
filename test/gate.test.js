import assert from "node:assert/strict";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

import { cli, createFixture } from "./helpers.js";

function reportDraft(extra = "当前没有未解析区域。") {
  return `# 架构分析报告

## 核心设计与权衡

入口为什么保持轻量：它以一层间接调用换取服务边界，证据见 \`src/index.js:1\`。

\`\`\`mermaid
flowchart LR
  A[入口] --> B[服务]
\`\`\`

## 风险、限制与 Unsupported Area

${extra}
`;
}

function prepareArtifacts() {
  const fixture = createFixture();
  const env = { REPO_ANALYZER_CTAGS: fixture.ctags, REPO_ANALYZER_AST_GREP: "/missing/ast-grep", REPO_ANALYZER_GRAPHIFY: "/missing/graphify" };
  for (const command of ["doctor", "scan", "summarize", "units"]) {
    assert.equal(cli(command, { ...fixture, env }).status, 0);
  }
  const unitsPath = join(fixture.out, "coverage-units.json");
  const coverage = JSON.parse(readFileSync(unitsPath, "utf8"));
  coverage.units[0].status = "analyzed";
  coverage.units[0].anchor = `${coverage.units[0].file}:${coverage.units[0].line}`;
  coverage.units[0].judgment = "该单元把入口调用收敛到服务边界，权衡了简单调用与边界隔离。";
  coverage.units[1].skip_reason = "快速模式优先验证主入口，保留该单元供后续深读。";
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);

  writeFileSync(
    join(fixture.out, "evidence-plan.md"),
    `# Evidence Plan\n\n## 架构问题\n- 入口如何约束服务边界？\n\n## 候选证据\n- src/index.js:1\n\n## 分工\n- parallelism: degraded，主 agent 串行执行。\n\n## 预算\n- mode: quick\n- time: 10 分钟\n- token: 10000\n`,
  );
  mkdirSync(join(fixture.out, "module-evidence"), { recursive: true });
  writeFileSync(
    join(fixture.out, "module-evidence", "src.json"),
    `${JSON.stringify({
      module: "src",
      module_role: "承接入口并调用服务实现。",
      entry_points: ["src/index.js:1"],
      core_data_structures: ["本 fixture 无持久数据结构。"],
      main_flow: ["src/index.js:1 -> src/service.js:1"],
      cross_module_dependencies: [],
      key_design_decisions: ["入口与服务函数分离，保留替换实现的边界。"],
      risk_areas: [{ category: "error-handling", evidence: "src/index.js:1", finding: "未发现错误转换层。", impact: "错误会直接穿透入口。" }],
      source_evidence: ["src/index.js:1", "src/service.js:1"],
      open_questions: [],
      narrative: "入口层很薄，其价值在于隔离调用者与服务实现，而非承载业务逻辑。",
    }, null, 2)}\n`,
  );
  writeFileSync(join(fixture.out, "report.md"), reportDraft());
  return { fixture, env, coverage, unitsPath };
}

test("gate 以双硬条件计算覆盖率，并按预算档决定是否放行", () => {
  const { fixture, env } = prepareArtifacts();

  const quick = cli("gate", { ...fixture, env, options: { mode: "quick" } });
  assert.equal(quick.status, 0);
  const quickReport = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  assert.equal(quickReport.allowed_to_synthesize, true);
  assert.equal(quickReport.budget.mode, "quick");
  assert.equal(quickReport.checks.find((check) => check.id === "key-unit-coverage").coverage[0].percent, 50);

  const standard = cli("gate", { ...fixture, env, options: { mode: "standard" } });
  assert.equal(standard.status, 3);
  const standardReport = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  assert.equal(standardReport.allowed_to_synthesize, false);
  assert.match(standardReport.checks.find((check) => check.id === "key-unit-coverage").reasons[0], /60%/);

  const deep = cli("gate", { ...fixture, env, options: { mode: "deep" } });
  assert.equal(deep.status, 3);
  const deepReport = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  assert.equal(deepReport.budget.coverage.core, 90);
  assert.ok(deepReport.budget.token_budget > standardReport.budget.token_budget);
});

test("gate 不把缺少实质判断的 analyzed 单元计入分子", () => {
  const { fixture, env, unitsPath } = prepareArtifacts();
  const coverage = JSON.parse(readFileSync(unitsPath, "utf8"));
  coverage.units[0].judgment = "";
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);

  const result = cli("gate", { ...fixture, env, options: { mode: "quick" } });

  assert.equal(result.status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "key-unit-coverage");
  assert.equal(check.coverage[0].analyzed, 0);
  assert.ok(check.evidence.some((item) => item.includes(coverage.units[0].id)));
});

test("gate 不把非法锚点计入分子，并拒绝无行号的风险证据", () => {
  const { fixture, env, unitsPath } = prepareArtifacts();
  const coverage = JSON.parse(readFileSync(unitsPath, "utf8"));
  coverage.units[0].anchor = "随便一段文本";
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);
  const matrixPath = join(fixture.out, "module-evidence", "src.json");
  const matrix = JSON.parse(readFileSync(matrixPath, "utf8"));
  matrix.risk_areas[0].evidence = "src/index.js";
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  assert.equal(report.checks.find((item) => item.id === "key-unit-coverage").coverage[0].analyzed, 0);
  assert.match(report.checks.find((item) => item.id === "module-evidence-matrix").reasons.join("\n"), /风险证据不是 file:line/);
});

test("gate 要求 core 未覆盖单元记录 skip_reason", () => {
  const { fixture, env, unitsPath } = prepareArtifacts();
  const coverage = JSON.parse(readFileSync(unitsPath, "utf8"));
  coverage.units[1].skip_reason = "";
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);

  const result = cli("gate", { ...fixture, env, options: { mode: "quick" } });

  assert.equal(result.status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  assert.match(report.checks.find((item) => item.id === "key-unit-coverage").reasons.join("\n"), /skip_reason/);
});

test("gate 对未解析 core 文件要求报告显式声明 unsupported area", () => {
  const { fixture, env, unitsPath } = prepareArtifacts();
  const coverage = JSON.parse(readFileSync(unitsPath, "utf8"));
  coverage.parsed = ["src/index.js"];
  coverage.unparsed = ["src/service.js"];
  coverage.parse_rate = 0.5;
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  writeFileSync(join(fixture.out, "report.md"), reportDraft("`src/service.js` 未解析，不对该区域声明覆盖充分。"));
  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 0);
});

test("gate 拒绝缺少 Why、源码锚点和 Mermaid 的空洞报告", () => {
  const { fixture, env } = prepareArtifacts();
  writeFileSync(join(fixture.out, "report.md"), "# 分析报告\n\n项目包含两个文件。\n");

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  assert.ok(report.checks.find((item) => item.id === "report-draft").reasons.length >= 3);
});
