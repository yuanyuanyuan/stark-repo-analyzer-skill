import assert from "node:assert/strict";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { performance } from "node:perf_hooks";
import test from "node:test";

import { cli, createFixture } from "./helpers.js";

const REQUIRED_ARTIFACTS = [
  "doctor-report.json",
  "repo-map.json",
  "repo-map.md",
  "coverage-units.json",
  "evidence-plan.md",
  "module-evidence/src.json",
  "report.md",
  "quality-gate-report.json",
];

test("代表性仓库完成 v2 全链路并生成最小新旧流程对比", (t) => {
  const fixture = createFixture();
  writeFileSync(join(fixture.repo, "src", "legacy.js"), `${"// legacy compatibility branch\n".repeat(8000)}export const legacy = true;\n`);
  const env = {
    REPO_ANALYZER_CTAGS: fixture.ctags,
    REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
    REPO_ANALYZER_GRAPHIFY: "/missing/graphify",
  };

  const pipelineStarted = performance.now();
  for (const command of ["doctor", "scan", "summarize", "units"]) {
    assert.equal(cli(command, { ...fixture, env }).status, 0);
  }
  const coveragePath = join(fixture.out, "coverage-units.json");
  const coverage = JSON.parse(readFileSync(coveragePath, "utf8"));
  mkdirSync(join(fixture.out, "module-evidence"), { recursive: true });
  const matrix = {
    module: "src",
    module_role: "承接外部入口并隔离服务实现。",
    entry_points: ["src/index.js:1"],
    core_data_structures: ["该 fixture 无核心持久数据结构。"],
    main_flow: ["src/index.js:1 -> src/service.js:1"],
    cross_module_dependencies: [],
    key_design_decisions: ["入口与服务分离，以一层调用换取可替换边界。"],
    risk_areas: [],
    source_evidence: ["src/index.js:1", "src/service.js:1"],
    open_questions: [],
    narrative: "入口层的价值是边界隔离，而不是承载业务逻辑。",
  };
  const baseReport = `# 架构分析报告

## 核心设计与权衡

入口为什么保持轻量：它以一层调用换取服务边界，证据见 \`src/index.js:1\`。

\`\`\`mermaid
flowchart LR
  A[入口] --> B[服务]
\`\`\`

## 风险、限制与 Unsupported Area

当前没有未解析区域；错误转换仍是开放问题。
`;
  const profiles = [
    { mode: "quick", analyzed: 1, risks: 1, time: 30, tokens: 30000, expansion: "" },
    { mode: "standard", analyzed: 2, risks: 2, time: 90, tokens: 90000, expansion: "\n标准模式补充关键边界与主要设计决策。".repeat(8) },
    { mode: "deep", analyzed: 3, risks: 3, time: 240, tokens: 240000, expansion: "\n深度模式补充 legacy 边缘路径、替代方案和工程成熟度判断。".repeat(16) },
  ];
  const profileResults = [];
  for (const profile of profiles) {
    coverage.repo.mode = profile.mode;
    for (const [index, unit] of coverage.units.entries()) {
      const analyzed = index < profile.analyzed;
      unit.status = analyzed ? "analyzed" : "unanalyzed";
      unit.anchor = analyzed ? `${unit.file}:${unit.line}` : null;
      unit.judgment = analyzed ? `${unit.symbol} 在 ${profile.mode} 模式下用于验证角色、流程或权衡。` : null;
      unit.skip_reason = analyzed ? null : `${profile.mode} 模式预算暂不覆盖该单元。`;
    }
    writeFileSync(coveragePath, `${JSON.stringify(coverage, null, 2)}\n`);
    writeFileSync(join(fixture.out, "evidence-plan.md"), `# Evidence Plan\n\n## 架构问题\n- 入口为何保持轻量？\n\n## 候选证据\n- src/index.js:1\n\n## 分工\n- parallelism: degraded\n\n## 预算\n- mode: ${profile.mode}\n- time: ${profile.time}\n- token: ${profile.tokens}\n`);
    matrix.risk_areas = Array.from({ length: profile.risks }, (_, index) => ({
      category: ["error-handling", "compatibility", "configuration"][index],
      evidence: index === 1 ? "src/legacy.js:8001" : index === 2 ? "src/service.js:1" : "src/index.js:1",
      finding: `${profile.mode} 模式风险抽样 ${index + 1}。`,
      impact: "该发现影响模块边界与工程成熟度评价。",
    }));
    matrix.semantic_reviews = profile.mode === "standard" ? [{
      unit_id: coverage.units[0].id,
      anchor: coverage.units[0].anchor,
      judgment: coverage.units[0].judgment,
      source_observation: `${coverage.units[0].anchor} 展示了该单元在 standard 模式下的角色、流程或权衡判断。`,
      verdict: "supported",
    }] : [];
    writeFileSync(join(fixture.out, "module-evidence", "src.json"), `${JSON.stringify(matrix, null, 2)}\n`);
    const report = `${baseReport}${profile.expansion}\n`;
    writeFileSync(join(fixture.out, "report.md"), report);
    assert.equal(cli("gate", { ...fixture, env, options: { mode: profile.mode } }).status, 0);
    const gate = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
    profileResults.push({
      analyzed: gate.checks.find((item) => item.id === "key-unit-coverage").coverage[0].analyzed,
      risks: matrix.risk_areas.length,
      report_length: report.length,
      token_budget: gate.budget.token_budget,
    });
  }
  assert.deepEqual(profileResults.map((item) => item.analyzed), [1, 2, 3]);
  assert.deepEqual(profileResults.map((item) => item.risks), [1, 2, 3]);
  assert.ok(profileResults[0].report_length < profileResults[1].report_length && profileResults[1].report_length < profileResults[2].report_length);
  assert.ok(profileResults[0].token_budget < profileResults[1].token_budget && profileResults[1].token_budget < profileResults[2].token_budget);
  const pipelineElapsedMs = Math.round((performance.now() - pipelineStarted) * 100) / 100;

  assert.ok(REQUIRED_ARTIFACTS.every((artifact) => existsSync(join(fixture.out, artifact))));
  const doctor = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(doctor.checks.find((item) => item.id === "graphify").status, "fail");
  assert.equal(doctor.allowed, true);

  const map = JSON.parse(readFileSync(join(fixture.out, "repo-map.json"), "utf8"));
  const legacyStarted = performance.now();
  const legacySourceBytes = map.files.source.reduce((total, file) => total + statSync(join(fixture.repo, file)).size, 0);
  const legacyElapsedMs = Math.round((performance.now() - legacyStarted) * 100) / 100;
  const anchoredBytes = coverage.units
    .filter((unit) => unit.status === "analyzed")
    .reduce((total, unit) => total + (readFileSync(join(fixture.repo, unit.file), "utf8").split(/\r?\n/)[unit.line - 1]?.length ?? 0), 0);
  const v2EvidenceBytes = statSync(join(fixture.out, "repo-map.md")).size + anchoredBytes;
  const gateReport = JSON.parse(readFileSync(join(fixture.out, "quality-gate-report.json"), "utf8"));
  const passedChecks = gateReport.checks.filter((item) => item.status === "pass").length;
  const benchmark = {
    fixture: "JavaScript 入口/服务 + 8000 行 legacy 兼容区",
    legacy: { elapsed_ms: legacyElapsedMs, approximate_tokens: Math.ceil(legacySourceBytes / 4), core_modules_omitted: 0, quality_gate_pass_rate: null },
    v2: {
      elapsed_ms: pipelineElapsedMs,
      approximate_tokens: Math.ceil(v2EvidenceBytes / 4),
      core_modules_omitted: ["main", "serve", "legacy"].filter((symbol) => !coverage.units.some((unit) => unit.symbol === symbol)).length,
      quality_gate_pass_rate: passedChecks / gateReport.checks.length,
    },
  };
  assert.ok(benchmark.v2.approximate_tokens < benchmark.legacy.approximate_tokens);
  assert.equal(benchmark.v2.core_modules_omitted, 0);
  assert.equal(benchmark.v2.quality_gate_pass_rate, 1);
  t.diagnostic(`benchmark=${JSON.stringify(benchmark)}`);
});
