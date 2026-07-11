import assert from "node:assert/strict";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

import { cli, createFixture } from "./helpers.js";

function reportDraft(extra = "当前没有未解析区域；错误转换仍需在服务边界中单独验证。") {
  return `# 架构分析报告

## 项目全景

该项目将入口、服务和风险处理保持在可追溯的边界内。

## 核心流程

调用从 \`src/index.js:1\` 进入服务边界，并由 \`src/service.js:1\` 返回结果给调用方。

## 模块协作

入口模块通过 \`src/index.js:1\` 调用 \`src/service.js:1\`，避免调用方直接依赖服务实现。

## 核心设计与权衡

入口为什么保持轻量：它以一层间接调用换取服务边界，证据见 \`src/index.js:1\`。

\`\`\`mermaid
flowchart LR
  A[入口] --> B[服务]
\`\`\`

## 风险、限制与 Unsupported Area

${extra}

## 具体改进建议

为服务边界补充错误转换层，并在调用方验证服务失败时的可观测降级路径。
`;
}

function semanticReviewFor(unit, overrides = {}) {
  return {
    unit_id: unit.id,
    anchor: unit.anchor,
    judgment: unit.judgment,
    source_observation: `源码 ${unit.anchor} 表达了该单元的当前判断。`,
    verdict: "supported",
    ...overrides,
  };
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
      semantic_reviews: [semanticReviewFor(coverage.units[0])],
      source_evidence: ["src/index.js:1", "src/service.js:1"],
      open_questions: [],
      narrative: "入口层很薄，其价值在于隔离调用者与服务实现，而非承载业务逻辑。",
    }, null, 2)}\n`,
  );
  writeFileSync(join(fixture.out, "report.md"), reportDraft());
  return { fixture, env, coverage, unitsPath };
}

function prepareStandardArtifacts() {
  const prepared = prepareArtifacts();
  const coverage = JSON.parse(readFileSync(prepared.unitsPath, "utf8"));
  for (const unit of coverage.units) {
    unit.status = "analyzed";
    unit.anchor = `${unit.file}:${unit.line}`;
    unit.judgment = `${unit.symbol} 用于验证 src 模块的角色、流程或权衡。`;
    unit.skip_reason = null;
  }
  writeFileSync(prepared.unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);
  const matrixPath = join(prepared.fixture.out, "module-evidence", "src.json");
  const matrix = JSON.parse(readFileSync(matrixPath, "utf8"));
  matrix.semantic_reviews = [semanticReviewFor(coverage.units[0])];
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);
  writeFileSync(
    join(prepared.fixture.out, "evidence-plan.md"),
    `# Evidence Plan

## 架构问题
- 入口如何约束服务边界？

## 候选证据
- src/index.js:1

## 分工
- parallelism: active
- 子代理分工：subagent-src 负责 src 模块。
- 子代理产物：subagent-src 写入 module-evidence/src.json。
- 主 agent 融合过程：主 agent merge 子代理产物后生成 report.md。

## 预算
- mode: standard
- time: 30 分钟
- token: 30000
`,
  );
  return { ...prepared, coverage, matrixPath };
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
  coverage.parsed = ["src/index.js", "src/parsed-a.js", "src/parsed-b.js", "src/parsed-c.js"];
  coverage.unparsed = ["src/legacy.js"];
  coverage.parse_rate = 0.8;
  delete coverage.parse_health;
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);
  const mapPath = join(fixture.out, "repo-map.json");
  const map = JSON.parse(readFileSync(mapPath, "utf8"));
  map.files.source = [...coverage.parsed, ...coverage.unparsed];
  map.languages = [{ language: "JavaScript", files: 5, lines: 100 }];
  writeFileSync(mapPath, `${JSON.stringify(map, null, 2)}\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  writeFileSync(join(fixture.out, "report.md"), reportDraft("`src/legacy.js` 未解析，不对该区域声明覆盖充分，相关跨模块判断保留为开放问题。"));
  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 0);
});

test("gate 拒绝缺少 Why、源码锚点和 Mermaid 的空洞报告", () => {
  const { fixture, env } = prepareArtifacts();
  writeFileSync(join(fixture.out, "report.md"), "# 分析报告\n\n项目包含两个文件。\n");

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  assert.ok(report.checks.find((item) => item.id === "report-draft").reasons.length >= 3);
});

test("gate 在主语言实际解析质量过低时阻止 synthesis", () => {
  const { fixture, env, unitsPath } = prepareArtifacts();
  const coverage = JSON.parse(readFileSync(unitsPath, "utf8"));
  coverage.parsed = ["src/index.js"];
  coverage.unparsed = ["src/service.js"];
  coverage.parse_rate = 0.5;
  coverage.parse_health = { source_files: 2, parsed_files: 2, unparsed_files: 0, parse_rate: 1 };
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "parse-quality");
  assert.equal(check.status, "fail");
  assert.match(check.reasons.join("\n"), /parse_rate/);
});

test("gate 不让次要语言的解析结果掩盖主语言 parse health", () => {
  const { fixture, env, unitsPath } = prepareArtifacts();
  const coverage = JSON.parse(readFileSync(unitsPath, "utf8"));
  coverage.parsed = ["src/index.js", "src/service.js", "src/extra-a.js", "src/extra-b.js"];
  coverage.unparsed = ["tools/primary.ts"];
  coverage.parse_rate = 0.8;
  coverage.parse_health = {
    source_files: 5,
    parsed_files: 4,
    unparsed_files: 1,
    parse_rate: 0.8,
    primary_languages: ["TypeScript"],
    primary: { source_files: 1, parsed_files: 1, unparsed_files: 0, parse_rate: 1 },
  };
  const mapPath = join(fixture.out, "repo-map.json");
  const map = JSON.parse(readFileSync(mapPath, "utf8"));
  map.files.source = [...coverage.parsed, ...coverage.unparsed];
  map.languages = [{ language: "TypeScript", files: 1, lines: 100 }, { language: "JavaScript", files: 4, lines: 10 }];
  writeFileSync(mapPath, `${JSON.stringify(map, null, 2)}\n`);
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "parse-quality");
  assert.equal(check.status, "fail");
  assert.match(check.reasons.join("\n"), /主语言/);
});

test("gate 在 core 单元引用不完整比例过高时阻止 synthesis", () => {
  const { fixture, env, unitsPath } = prepareArtifacts();
  const coverage = JSON.parse(readFileSync(unitsPath, "utf8"));
  for (const unit of coverage.units) {
    unit.refs = [];
    unit.refs_status = "partial";
  }
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "reference-quality");
  assert.equal(check.status, "fail");
  assert.match(check.reasons.join("\n"), /partial\/missing/);
});

test("gate 拒绝缺少项目叙事、模块协作和改进建议的浅报告", () => {
  const { fixture, env } = prepareArtifacts();
  writeFileSync(join(fixture.out, "report.md"), `# 分析报告\n\n## 风险\n\n只列出未支持区域。\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "report-depth");
  assert.equal(check.status, "fail");
  assert.match(check.reasons.join("\n"), /项目全景/);
  assert.match(check.reasons.join("\n"), /模块协作/);
  assert.match(check.reasons.join("\n"), /改进建议/);
});

test("gate 拒绝只有模板句的完整标题报告", () => {
  const { fixture, env } = prepareArtifacts();
  writeFileSync(join(fixture.out, "report.md"), `# 架构分析报告

## 项目全景

这是一个没有项目特异性的泛化项目全景模板文本，用于填充表面结构。

## 核心流程

这是一个没有项目特异性的泛化核心流程模板文本，用于填充表面结构。

## 模块协作

这是一个没有项目特异性的泛化模块协作模板文本，用于填充表面结构。

## 核心设计与权衡

这是一个没有项目特异性的泛化权衡模板文本，为什么采用模板没有明确依据。

\`\`\`mermaid
flowchart LR
  A --> B
\`\`\`

## 风险、限制与 Unsupported Area

这是一个没有项目特异性的泛化风险限制模板文本，用于填充表面结构。

## 具体改进建议

这是一个没有项目特异性的泛化改进建议模板文本，用于填充表面结构。
`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "report-depth");
  assert.equal(check.status, "fail");
  assert.match(check.reasons.join("\n"), /核心流程/);
});

test("standard gate 要求每个 core 模块至少一个有效 semantic review", () => {
  const { fixture, env } = prepareStandardArtifacts();

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "standard" } }).status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "semantic-source-review");
  assert.equal(check.status, "pass");
  assert.deepEqual(check.modules[0].units.length, 1);
  assert.equal(check.threshold.per_core_module, 1);
});

test("standard/deep gate 不把 parallelism degraded 视为多子代理执行通过", () => {
  const { fixture, env } = prepareStandardArtifacts();
  writeFileSync(
    join(fixture.out, "evidence-plan.md"),
    `# Evidence Plan

## 架构问题
- 入口如何约束服务边界？

## 候选证据
- src/index.js:1

## 分工
- parallelism: degraded，主 agent 串行执行。

## 预算
- mode: standard
- time: 30 分钟
- token: 30000
`,
  );

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "standard" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "parallelism-execution");
  assert.equal(check.status, "fail");
  assert.match(check.reasons.join("\n"), /parallelism: degraded/);
  assert.equal(report.allowed_to_synthesize, false);
});

test("quick gate 允许 parallelism degraded 且不因缺少 active 而失败", () => {
  const { fixture, env } = prepareArtifacts();

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "parallelism-execution");
  assert.equal(check.status, "pass");
  assert.equal(report.allowed_to_synthesize, true);
  assert.match(readFileSync(join(fixture.out, "evidence-plan.md"), "utf8"), /parallelism:\s*degraded/i);
});

test("standard/deep gate 要求显式记录 active parallelism", () => {
  const { fixture, env } = prepareStandardArtifacts();
  writeFileSync(
    join(fixture.out, "evidence-plan.md"),
    `# Evidence Plan

## 架构问题
- 入口如何约束服务边界？

## 候选证据
- src/index.js:1

## 分工
- 子代理分工：subagent-src 负责 src 模块。
- 子代理产物：subagent-src 写入 module-evidence/src.json。
- 主 agent 融合过程：主 agent merge 子代理产物后生成 report.md。

## 预算
- mode: standard
- time: 30 分钟
- token: 30000
`,
  );

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "standard" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const check = report.checks.find((item) => item.id === "parallelism-execution");
  assert.equal(check.status, "fail");
  assert.match(check.reasons.join("\n"), /parallelism: active/);
});

test("quick gate 要求全局 2-3 条 semantic review，可用 analyzed unit 不足时要求全抽", () => {
  const { fixture, env, unitsPath, matrixPath, coverage } = prepareStandardArtifacts();
  const matrix = JSON.parse(readFileSync(matrixPath, "utf8"));

  matrix.semantic_reviews = [semanticReviewFor(coverage.units[0])];
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);
  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  let report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  let check = report.checks.find((item) => item.id === "semantic-source-review");
  assert.match(check.reasons.join("\n"), /quick 模式全局有效 semantic review 1\/2/);
  assert.equal(check.threshold.min, 2);
  assert.equal(check.threshold.max, 2);

  matrix.semantic_reviews = [semanticReviewFor(coverage.units[0]), semanticReviewFor(coverage.units[1])];
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);
  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 0);
  report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  check = report.checks.find((item) => item.id === "semantic-source-review");
  assert.equal(check.global.valid, 2);

  coverage.units.push(
    { ...coverage.units[0], id: "src/index.js#extra-1", symbol: "extraOne", judgment: "extraOne 用于验证 quick 超预算。" },
    { ...coverage.units[0], id: "src/index.js#extra-2", symbol: "extraTwo", judgment: "extraTwo 用于验证 quick 超预算。" },
  );
  matrix.semantic_reviews = coverage.units.slice(0, 4).map((unit) => semanticReviewFor(unit));
  writeFileSync(unitsPath, `${JSON.stringify(coverage, null, 2)}\n`);
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);
  assert.equal(cli("gate", { ...fixture, env, options: { mode: "quick" } }).status, 3);
  report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  check = report.checks.find((item) => item.id === "semantic-source-review");
  assert.match(check.reasons.join("\n"), /quick 模式全局有效 semantic review 4\/3/);
});

test("deep gate 要求每个 core 模块抽查全部不足 3 条的 analyzed unit", () => {
  const { fixture, env, matrixPath, coverage } = prepareStandardArtifacts();
  const matrix = JSON.parse(readFileSync(matrixPath, "utf8"));
  matrix.semantic_reviews = [semanticReviewFor(coverage.units[0])];
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "deep" } }).status, 3);
  let report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  let check = report.checks.find((item) => item.id === "semantic-source-review");
  assert.match(check.reasons.join("\n"), /deep 模式有效 semantic review 1\/2/);

  matrix.semantic_reviews = [semanticReviewFor(coverage.units[0]), semanticReviewFor(coverage.units[1])];
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);
  assert.equal(cli("gate", { ...fixture, env, options: { mode: "deep" } }).status, 0);
  report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  check = report.checks.find((item) => item.id === "semantic-source-review");
  assert.deepEqual(check.modules[0].units.length, 2);
  assert.equal(check.modules[0].denominator, 2);
});

test("standard gate 拒绝缺失、未知、非 analyzed 和重复的 semantic review", () => {
  const { fixture, env, unitsPath, matrixPath, coverage } = prepareStandardArtifacts();
  const matrix = JSON.parse(readFileSync(matrixPath, "utf8"));

  delete matrix.semantic_reviews;
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);
  assert.equal(cli("gate", { ...fixture, env, options: { mode: "standard" } }).status, 3);
  let report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  assert.match(report.checks.find((item) => item.id === "semantic-source-review").reasons.join("\n"), /semantic_reviews 必须是数组/);

  matrix.semantic_reviews = [
    semanticReviewFor(coverage.units[0], { unit_id: "missing-unit" }),
    semanticReviewFor(coverage.units[0]),
    semanticReviewFor(coverage.units[0]),
  ];
  const updatedCoverage = JSON.parse(readFileSync(unitsPath, "utf8"));
  updatedCoverage.units[1].status = "unanalyzed";
  matrix.semantic_reviews.push(semanticReviewFor(updatedCoverage.units[1]));
  writeFileSync(unitsPath, `${JSON.stringify(updatedCoverage, null, 2)}\n`);
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "standard" } }).status, 3);
  report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const reasons = report.checks.find((item) => item.id === "semantic-source-review").reasons.join("\n");
  assert.match(reasons, /未知 unit_id/);
  assert.match(reasons, /重复抽查 unit/);
  assert.match(reasons, /不是 analyzed 状态/);
});

test("standard gate 拒绝过期 anchor、过期 judgment、空 observation 和非 supported verdict", () => {
  const { fixture, env, matrixPath, coverage } = prepareStandardArtifacts();
  const matrix = JSON.parse(readFileSync(matrixPath, "utf8"));
  matrix.semantic_reviews = [
    semanticReviewFor(coverage.units[0], {
      anchor: "src/index.js:999",
      judgment: "过期判断。",
      source_observation: "",
      verdict: "partial",
    }),
  ];
  writeFileSync(matrixPath, `${JSON.stringify(matrix, null, 2)}\n`);

  assert.equal(cli("gate", { ...fixture, env, options: { mode: "standard" } }).status, 3);
  const report = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const reasons = report.checks.find((item) => item.id === "semantic-source-review").reasons.join("\n");
  assert.match(reasons, /anchor 与 coverage 当前值不一致/);
  assert.match(reasons, /judgment 与 coverage 当前值不一致/);
  assert.match(reasons, /source_observation 缺失或为空/);
  assert.match(reasons, /verdict 必须为 supported/);
});
