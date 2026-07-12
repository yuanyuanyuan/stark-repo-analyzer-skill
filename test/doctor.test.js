import assert from "node:assert/strict";
import { chmodSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

import { cli, createFixture, ctagsOnlyEnv, deepGraphifyEnv, standardOnlyEnv } from "./helpers.js";

test("doctor standard-only：基线放行，deep 阻塞，输出能力矩阵", () => {
  const fixture = createFixture();
  const result = cli("doctor", {
    ...fixture,
    env: standardOnlyEnv(fixture),
    options: { mode: "standard" },
  });

  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed, true);
  assert.equal(report.allowed_standard, true);
  assert.equal(report.allowed_deep, false);
  assert.ok(report.capability_matrix);
  assert.deepEqual(report.capability_matrix.available_modes, ["standard"]);
  assert.ok(report.capability_matrix.blocked_modes.includes("deep"));
  assert.ok(report.capability_matrix.missing_capabilities.deep.includes("graph-queries"));
  assert.equal(report.checks.find((check) => check.id === "graphify").required, false);
  assert.equal(report.checks.find((check) => check.id === "symbol-enumerator").required, false);
  assert.equal(report.enumerator, null);
  assert.ok(report.official_source_refs ?? report.capability_matrix.official_source_refs);
  assert.ok(report.capability_matrix.official_source_refs.every((item) => item.official_source_url && item.verified_date));
});

test("doctor deep-blocked：有 ctags 但缺 graph-queries 时 deep 不可用", () => {
  const fixture = createFixture();
  const result = cli("doctor", {
    ...fixture,
    env: ctagsOnlyEnv(fixture),
    options: { mode: "deep" },
  });

  assert.equal(result.status, 2);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed_standard, true);
  assert.equal(report.allowed_deep, false);
  assert.equal(report.allowed, false);
  assert.ok(report.capability_matrix.missing_capabilities.deep.includes("graph-queries"));
  assert.equal(report.deep_enumerator?.name, "universal-ctags");
});

test("doctor deep-available：Graphify 满足三能力时放行 deep", () => {
  const fixture = createFixture();
  const result = cli("doctor", {
    ...fixture,
    env: deepGraphifyEnv(fixture),
    options: { mode: "deep" },
  });

  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed_deep, true);
  assert.ok(report.capability_matrix.available_modes.includes("deep"));
  assert.equal(report.capability_matrix.capabilities["graph-queries"].available, true);
  assert.equal(report.capability_matrix.capabilities["symbol-enumeration"].available, true);
  assert.equal(report.capability_matrix.capabilities["reference-edges"].available, true);
});

test("doctor 安装 prompt：反映缺失能力且禁止改被分析仓源码", () => {
  const fixture = createFixture();
  const result = cli("doctor", {
    ...fixture,
    env: standardOnlyEnv(fixture),
    options: { mode: "standard", "install-mode": "deep" },
    flags: ["--install-prompt"],
  });

  assert.equal(result.status, 0);
  const prompt = readFileSync(join(fixture.out, "install-prompt.md"), "utf8");
  assert.match(prompt, /graph-queries|Graphify/i);
  assert.match(prompt, /不得.*修改被分析仓库的源码|不得\*\*修改被分析仓库/);
  assert.match(result.stdout, /AI Installation Agent Prompt|目标模式/);
});

test("doctor 在 ctags 不支持主要语言时选择可用的 ast-grep 作为 deep 枚举器", () => {
  const fixture = createFixture();
  writeFileSync(
    fixture.ctags,
    "#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then echo 'Universal Ctags 6.1.0'; else echo 'Python'; fi\n",
  );
  chmodSync(fixture.ctags, 0o755);

  const result = cli("doctor", {
    ...fixture,
    env: {
      REPO_ANALYZER_CTAGS: fixture.ctags,
      REPO_ANALYZER_AST_GREP: fixture.astGrep,
      REPO_ANALYZER_GRAPHIFY: fixture.graphify,
      REPO_ANALYZER_GRAPHIFY_CAPABILITIES: "graph-queries,symbol-enumeration,reference-edges",
      // 本用例 ctags 不吐 reference tags；用 Graphify units 接线开关仅验证 enumerator 选择逻辑
      REPO_ANALYZER_GRAPHIFY_UNITS_REFS: "1",
    },
    options: { mode: "deep" },
  });

  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.deep_enumerator.name, "ast-grep");
});

test("doctor 记录 graphify 缺失但不阻塞 standard", () => {
  const fixture = createFixture();
  const result = cli("doctor", {
    ...fixture,
    env: ctagsOnlyEnv(fixture),
    options: { mode: "standard" },
  });

  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed, true);
  assert.equal(report.checks.find((check) => check.id === "graphify").status, "fail");
});

test("doctor 拦截：ctags 无 reference-role 且 Graphify 未接线 units 时 deep 不可用", () => {
  const fixture = createFixture();
  writeFileSync(
    fixture.ctags,
    `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('Universal Ctags 6.1.0'); process.exit(0); }
if (args.includes('--list-languages')) { console.log('JavaScript\nTypeScript'); process.exit(0); }
const file = args.at(-1);
// 只产出 definition，不产出 roles=reference —— 模拟真实 TS/JS ctags 限制
if (file?.endsWith('src/index.js')) console.log(JSON.stringify({_type:'tag',name:'main',path:file,line:1,kind:'function'}));
if (file?.endsWith('src/service.js')) console.log(JSON.stringify({_type:'tag',name:'serve',path:file,line:1,kind:'function'}));
`,
  );
  chmodSync(fixture.ctags, 0o755);

  const result = cli("doctor", {
    ...fixture,
    env: {
      REPO_ANALYZER_CTAGS: fixture.ctags,
      REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
      REPO_ANALYZER_GRAPHIFY: fixture.graphify,
      REPO_ANALYZER_GRAPHIFY_CAPABILITIES: "graph-queries,symbol-enumeration,reference-edges",
    },
    options: { mode: "deep" },
  });

  assert.equal(result.status, 2);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed_standard, true);
  assert.equal(report.allowed_deep, false);
  assert.equal(report.allowed, false);
  assert.ok(report.capability_matrix.missing_capabilities.deep.includes("reference-edges"));
  assert.equal(report.capability_matrix.capabilities["reference-edges"].available, false);
  const probeCheck = report.checks.find((check) => check.id === "reference-edge-usability");
  assert.equal(probeCheck.status, "fail");
  assert.ok(probeCheck.ctags_reference_tags === 0);
  assert.match(probeCheck.reasons.join("\n"), /reference|partial|roles/i);
  assert.ok(report.reference_probe);
  assert.equal(report.reference_probe.usable, false);
});

test("doctor 放行：ctags 抽样能产出 roles=reference 时 deep 可用", () => {
  const fixture = createFixture();
  const result = cli("doctor", {
    ...fixture,
    env: deepGraphifyEnv(fixture),
    options: { mode: "deep" },
  });
  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed_deep, true);
  const probeCheck = report.checks.find((check) => check.id === "reference-edge-usability");
  assert.equal(probeCheck.status, "pass");
  assert.ok(probeCheck.ctags_reference_tags > 0);
  assert.ok(report.capability_matrix.capabilities["reference-edges"].providers.includes("universal-ctags"));
});

test("doctor 放行：Graphify units 接线开关打开时即使无 ctags reference 也可 deep", () => {
  const fixture = createFixture();
  writeFileSync(
    fixture.ctags,
    `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('Universal Ctags 6.1.0'); process.exit(0); }
if (args.includes('--list-languages')) { console.log('JavaScript'); process.exit(0); }
const file = args.at(-1);
if (file?.endsWith('.js')) console.log(JSON.stringify({_type:'tag',name:'main',path:file,line:1,kind:'function'}));
`,
  );
  chmodSync(fixture.ctags, 0o755);
  const result = cli("doctor", {
    ...fixture,
    env: {
      REPO_ANALYZER_CTAGS: fixture.ctags,
      REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
      REPO_ANALYZER_GRAPHIFY: fixture.graphify,
      REPO_ANALYZER_GRAPHIFY_CAPABILITIES: "graph-queries,symbol-enumeration,reference-edges",
      REPO_ANALYZER_GRAPHIFY_UNITS_REFS: "1",
    },
    options: { mode: "deep" },
  });
  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed_deep, true);
  assert.ok(report.capability_matrix.capabilities["reference-edges"].providers.includes("graphify"));
});


test("doctor 放行：目标仓 graphify-out/graph.json 有 EXTRACTED 边时无需 env 开关", () => {
  const fixture = createFixture();
  writeFileSync(
    fixture.ctags,
    `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('Universal Ctags 6.1.0'); process.exit(0); }
if (args.includes('--list-languages')) { console.log('JavaScript'); process.exit(0); }
const file = args.at(-1);
if (file?.endsWith('.js')) console.log(JSON.stringify({_type:'tag',name:'main',path:file,line:1,kind:'function'}));
`,
  );
  chmodSync(fixture.ctags, 0o755);
  mkdirSync(join(fixture.repo, "graphify-out"), { recursive: true });
  writeFileSync(
    join(fixture.repo, "graphify-out", "graph.json"),
    JSON.stringify({
      nodes: [
        { id: "a", label: "main()", source_file: "src/index.js", source_location: "L1", file_type: "code" },
        { id: "b", label: "serve()", source_file: "src/service.js", source_location: "L1", file_type: "code" },
      ],
      links: [
        { source: "a", target: "b", relation: "calls", confidence: "EXTRACTED", source_file: "src/index.js", source_location: "L1" },
      ],
    }),
  );

  const result = cli("doctor", {
    ...fixture,
    env: {
      REPO_ANALYZER_CTAGS: fixture.ctags,
      REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
      REPO_ANALYZER_GRAPHIFY: fixture.graphify,
      REPO_ANALYZER_GRAPHIFY_CAPABILITIES: "graph-queries,symbol-enumeration,reference-edges",
    },
    options: { mode: "deep" },
  });
  assert.equal(result.status, 0);
  const report = JSON.parse(readFileSync(join(fixture.out, "doctor-report.json"), "utf8"));
  assert.equal(report.allowed_deep, true);
  assert.ok(report.capability_matrix.capabilities["reference-edges"].providers.includes("graphify"));
  assert.equal(report.reference_probe.graphify_units_refs_wired, true);
  assert.ok(report.reference_probe.graphify_graph?.extracted_ref_links >= 1);
});
