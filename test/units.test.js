import assert from "node:assert/strict";
import { chmodSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

import { cli, createFixture, deepGraphifyEnv, standardOnlyEnv } from "./helpers.js";

function prepareDeep(fixture) {
  const env = deepGraphifyEnv(fixture);
  assert.equal(cli("doctor", { ...fixture, env, options: { mode: "deep" } }).status, 0);
  assert.equal(cli("scan", { ...fixture, env, options: { mode: "deep" } }).status, 0);
  return env;
}

function prepareStandard(fixture) {
  const env = standardOnlyEnv(fixture);
  assert.equal(cli("doctor", { ...fixture, env, options: { mode: "standard" } }).status, 0);
  assert.equal(cli("scan", { ...fixture, env, options: { mode: "standard" } }).status, 0);
  return env;
}

test("standard units 使用启发式发现且忽略增强工具", () => {
  const fixture = createFixture();
  const env = {
    ...standardOnlyEnv(fixture),
    REPO_ANALYZER_CTAGS: fixture.ctags, // present but must be ignored
  };
  assert.equal(cli("doctor", { ...fixture, env, options: { mode: "standard" } }).status, 0);
  assert.equal(cli("scan", { ...fixture, env, options: { mode: "standard" } }).status, 0);

  assert.equal(cli("units", { ...fixture, env, options: { mode: "standard" } }).status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "coverage-units.json"), "utf8"));
  assert.equal(report.repo.mode, "standard");
  assert.equal(report.repo.tooling_level, "baseline");
  assert.equal(report.enumerator.name, "heuristic-text");
  assert.ok(report.limitations.some((item) => /heuristic/i.test(item)));
  assert.ok(report.units.some((unit) => unit.symbol === "main"));
  assert.ok(report.units.some((unit) => unit.discovery === "heuristic"));
});

test("units 由符号枚举器生成稳定、可审计的关键单元分母", () => {
  const fixture = createFixture();
  const env = prepareDeep(fixture);

  assert.equal(cli("units", { ...fixture, env, options: { mode: "deep" } }).status, 0);
  const first = JSON.parse(readFileSync(join(fixture.out, "coverage-units.json"), "utf8"));
  assert.equal(first.repo.commit.length, 40);
  assert.equal(first.repo.mode, "deep");
  assert.deepEqual(first.parsed, ["src/index.js", "src/service.js"]);
  assert.deepEqual(first.unparsed, []);
  assert.equal(first.parse_rate, 1);
  assert.deepEqual(first.modules, [{ name: "src", path_globs: ["src/**"], classification: "core", reason: "源码规模最大的模块候选", source: "repo-map.json" }]);
  assert.equal(first.units.length, 2);
  assert.ok(first.units.every((unit) => unit.id && unit.status === "unanalyzed" && unit.module === "src"));
  assert.ok(first.units.some((unit) => unit.symbol === "serve" && unit.refs.some((ref) => ref.file === "src/index.js" && ref.source === "ctags")));
  assert.ok(first.units.some((unit) => unit.refs_status === "complete"));

  first.units[0].status = "analyzed";
  first.units[0].anchor = `${first.units[0].file}:${first.units[0].line}`;
  first.units[0].judgment = "该入口把外部调用收敛到服务边界，避免上层直接依赖实现细节。";
  writeFileSync(join(fixture.out, "coverage-units.json"), `${JSON.stringify(first, null, 2)}\n`);

  assert.equal(cli("units", { ...fixture, env, options: { mode: "deep" } }).status, 0);
  const second = JSON.parse(readFileSync(join(fixture.out, "coverage-units.json"), "utf8"));
  assert.deepEqual(second.units.map((unit) => unit.id), first.units.map((unit) => unit.id));
  assert.equal(second.units[0].status, "analyzed");
  assert.equal(second.units[0].judgment, first.units[0].judgment);
});

test("deep units 在枚举器失效时阻塞且不降级", () => {
  const fixture = createFixture();
  const env = prepareDeep(fixture);
  unlinkSync(fixture.ctags);
  unlinkSync(fixture.graphify);

  const result = cli("units", { ...fixture, env, options: { mode: "deep" } });

  assert.notEqual(result.status, 0);
  assert.match(`${result.stderr}\n${result.stdout}`, /不降级|不可用|拒绝/);
});

test("units 使用 Doctor 选中的 ast-grep 枚举 JavaScript 单元", () => {
  const fixture = createFixture();
  const env = {
    REPO_ANALYZER_CTAGS: "/missing/ctags",
    REPO_ANALYZER_AST_GREP: fixture.astGrep,
    REPO_ANALYZER_GRAPHIFY: fixture.graphify,
    REPO_ANALYZER_GRAPHIFY_CAPABILITIES: "graph-queries,symbol-enumeration,reference-edges",
    REPO_ANALYZER_GRAPHIFY_UNITS_REFS: "1",
  };
  assert.equal(cli("doctor", { ...fixture, env, options: { mode: "deep" } }).status, 0);
  assert.equal(cli("scan", { ...fixture, env, options: { mode: "deep" } }).status, 0);

  const result = cli("units", { ...fixture, env, options: { mode: "deep" } });

  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "coverage-units.json"), "utf8"));
  assert.equal(report.enumerator.name, "ast-grep");
  assert.deepEqual(report.units.map((unit) => unit.symbol), ["main", "serve"]);
  assert.equal(report.parse_rate, 1);
});

test("units 在仅有 grep 时使用 Doctor 选中的文本搜索工具补充引用", () => {
  const fixture = createFixture();
  writeFileSync(
    fixture.ctags,
    `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('Universal Ctags 6.1.0'); process.exit(0); }
if (args.includes('--list-languages')) { console.log('JavaScript'); process.exit(0); }
const file = args.at(-1);
if (file?.endsWith('src/index.js')) console.log(JSON.stringify({_type:'tag',name:'main',line:1,kind:'function'}));
if (file?.endsWith('src/service.js')) console.log(JSON.stringify({_type:'tag',name:'serve',line:1,kind:'function'}));
`,
  );
  chmodSync(fixture.ctags, 0o755);
  const env = {
    REPO_ANALYZER_CTAGS: fixture.ctags,
    REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
    REPO_ANALYZER_GRAPHIFY: fixture.graphify,
    REPO_ANALYZER_GRAPHIFY_CAPABILITIES: "graph-queries,symbol-enumeration,reference-edges",
    // 本用例刻意让 ctags 不吐 reference-role，只测 grep partial refs；用 Graphify units 开关让 doctor 放行 deep
    REPO_ANALYZER_GRAPHIFY_UNITS_REFS: "1",
    REPO_ANALYZER_RG: "/missing/rg",
    REPO_ANALYZER_GREP: "grep",
  };
  assert.equal(cli("doctor", { ...fixture, env, options: { mode: "deep" } }).status, 0);
  assert.equal(cli("scan", { ...fixture, env, options: { mode: "deep" } }).status, 0);

  assert.equal(cli("units", { ...fixture, env, options: { mode: "deep" } }).status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "coverage-units.json"), "utf8"));
  const serve = report.units.find((unit) => unit.symbol === "serve");
  assert.ok(serve.refs.some((ref) => ref.file === "src/index.js" && ref.source === "grep"));
  assert.equal(serve.refs_status, "partial");
});

test("deep 缺能力时 units 拒绝且不生成降级分析路径", () => {
  const fixture = createFixture();
  const env = standardOnlyEnv(fixture);
  assert.equal(cli("doctor", { ...fixture, env, options: { mode: "standard" } }).status, 0);
  // doctor for deep fails
  assert.equal(cli("doctor", { ...fixture, env, options: { mode: "deep" } }).status, 2);
  const result = cli("units", { ...fixture, env, options: { mode: "deep" } });
  assert.notEqual(result.status, 0);
  assert.match(`${result.stderr}\n${result.stdout}`, /不降级|不可用|未放行 deep|缺失能力/);
});
