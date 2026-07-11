import assert from "node:assert/strict";
import { chmodSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

import { cli, createFixture } from "./helpers.js";

function prepare(fixture) {
  const env = { REPO_ANALYZER_CTAGS: fixture.ctags, REPO_ANALYZER_AST_GREP: "/missing/ast-grep" };
  assert.equal(cli("doctor", { ...fixture, env }).status, 0);
  assert.equal(cli("scan", { ...fixture, env }).status, 0);
  return env;
}

test("units 由符号枚举器生成稳定、可审计的关键单元分母", () => {
  const fixture = createFixture();
  const env = prepare(fixture);

  assert.equal(cli("units", { ...fixture, env }).status, 0);
  const first = JSON.parse(readFileSync(join(fixture.out, "coverage-units.json"), "utf8"));
  assert.equal(first.repo.commit.length, 40);
  assert.deepEqual(first.parsed, ["src/index.js", "src/service.js"]);
  assert.deepEqual(first.unparsed, []);
  assert.equal(first.parse_rate, 1);
  assert.deepEqual(first.parse_health, {
    source_files: 2,
    parsed_files: 2,
    unparsed_files: 0,
    parse_rate: 1,
    primary_languages: ["JavaScript"],
    primary: {
      source_files: 2,
      parsed_files: 2,
      unparsed_files: 0,
      parse_rate: 1,
    },
  });
  assert.deepEqual(first.modules, [{ name: "src", path_globs: ["src/**"], classification: "core", reason: "源码规模最大的模块候选", source: "repo-map.json" }]);
  assert.equal(first.units.length, 2);
  assert.ok(first.units.every((unit) => unit.id && unit.status === "unanalyzed" && unit.module === "src"));
  assert.ok(first.units.some((unit) => unit.symbol === "serve" && unit.refs.some((ref) => ref.file === "src/index.js" && ref.source === "ctags")));
  assert.ok(first.units.some((unit) => unit.refs_status === "complete"));

  first.units[0].status = "analyzed";
  first.units[0].anchor = `${first.units[0].file}:${first.units[0].line}`;
  first.units[0].judgment = "该入口把外部调用收敛到服务边界，避免上层直接依赖实现细节。";
  writeFileSync(join(fixture.out, "coverage-units.json"), `${JSON.stringify(first, null, 2)}\n`);

  assert.equal(cli("units", { ...fixture, env }).status, 0);
  const second = JSON.parse(readFileSync(join(fixture.out, "coverage-units.json"), "utf8"));
  assert.deepEqual(second.units.map((unit) => unit.id), first.units.map((unit) => unit.id));
  assert.equal(second.units[0].status, "analyzed");
  assert.equal(second.units[0].judgment, first.units[0].judgment);
});

test("units 在 Doctor 之后枚举器失效时阻塞且不降级到正则分母", () => {
  const fixture = createFixture();
  const env = prepare(fixture);
  unlinkSync(fixture.ctags);

  const result = cli("units", { ...fixture, env });

  assert.equal(result.status, 1);
  assert.match(result.stderr, /符号枚举器.*不可用/);
});

test("units 使用 Doctor 选中的 ast-grep 枚举 JavaScript 单元", () => {
  const fixture = createFixture();
  const env = { REPO_ANALYZER_CTAGS: "/missing/ctags", REPO_ANALYZER_AST_GREP: fixture.astGrep };
  assert.equal(cli("doctor", { ...fixture, env }).status, 0);
  assert.equal(cli("scan", { ...fixture, env }).status, 0);

  const result = cli("units", { ...fixture, env });

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
    REPO_ANALYZER_RG: "/missing/rg",
    REPO_ANALYZER_GREP: "grep",
  };
  assert.equal(cli("doctor", { ...fixture, env }).status, 0);
  assert.equal(cli("scan", { ...fixture, env }).status, 0);

  assert.equal(cli("units", { ...fixture, env }).status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "coverage-units.json"), "utf8"));
  const serve = report.units.find((unit) => unit.symbol === "serve");
  assert.ok(serve.refs.some((ref) => ref.file === "src/index.js" && ref.source === "grep"));
  assert.equal(serve.refs_status, "partial");
});
