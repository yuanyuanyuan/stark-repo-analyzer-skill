import assert from "node:assert/strict";
import { chmodSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

import { cli, createFixture } from "./helpers.js";

test("doctor 成功时生成逐项报告并允许进入分析", () => {
  const fixture = createFixture();
  const result = cli("doctor", {
    ...fixture,
    env: { REPO_ANALYZER_CTAGS: fixture.ctags, REPO_ANALYZER_AST_GREP: "/missing/ast-grep" },
  });

  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed, true);
  assert.equal(report.enumerator.name, "universal-ctags");
  assert.equal(report.checks.find((check) => check.id === "graphify").required, false);
  assert.ok(report.checks.filter((check) => check.required).every((check) => check.status === "pass"));
});

test("doctor 缺少符号枚举器时阻塞并给出修复指引", () => {
  const fixture = createFixture();
  const result = cli("doctor", {
    ...fixture,
    env: {
      REPO_ANALYZER_CTAGS: "/missing/ctags",
      REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
    },
  });

  assert.equal(result.status, 2);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed, false);
  const check = report.checks.find((item) => item.id === "symbol-enumerator");
  assert.equal(check.status, "fail");
  assert.match(check.remediation, /universal-ctags.*ast-grep/);
});

test("doctor 记录 graphify 缺失但不因此阻塞", () => {
  const fixture = createFixture();
  const result = cli("doctor", {
    ...fixture,
    env: {
      REPO_ANALYZER_CTAGS: fixture.ctags,
      REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
      REPO_ANALYZER_GRAPHIFY: "/missing/graphify",
    },
  });

  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed, true);
  assert.equal(report.checks.find((check) => check.id === "graphify").status, "fail");
});

test("doctor 在 ctags 不支持主要语言时选择可用的 ast-grep", () => {
  const fixture = createFixture();
  writeFileSync(
    fixture.ctags,
    "#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then echo 'Universal Ctags 6.1.0'; else echo 'Python'; fi\n",
  );
  chmodSync(fixture.ctags, 0o755);

  const result = cli("doctor", {
    ...fixture,
    env: { REPO_ANALYZER_CTAGS: fixture.ctags, REPO_ANALYZER_AST_GREP: fixture.astGrep },
  });

  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.enumerator.name, "ast-grep");
});
