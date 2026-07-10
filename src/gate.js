import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

import { budgetFor } from "./budgets.js";
import { readJson, writeJson } from "./common.js";

const MATRIX_FIELDS = [
  "module_role",
  "entry_points",
  "core_data_structures",
  "main_flow",
  "cross_module_dependencies",
  "key_design_decisions",
  "risk_areas",
  "source_evidence",
  "open_questions",
  "narrative",
];
const ANCHOR_PATTERN = /^.+:\d+(?:-\d+)?$/;

function check(id, passed, reasons = [], evidence = []) {
  return { id, status: passed ? "pass" : "fail", reasons: passed ? [] : reasons, evidence };
}

function nonEmpty(value) {
  if (Array.isArray(value)) return value.length > 0;
  return typeof value === "string" ? value.trim().length > 0 : value != null;
}

function evidencePlanCheck(out) {
  const path = join(out, "evidence-plan.md");
  if (!existsSync(path)) return check("evidence-plan", false, ["缺少 evidence-plan.md。"], [path]);
  const content = readFileSync(path, "utf8");
  const requirements = [
    ["架构问题", /架构问题/i],
    ["候选证据", /候选证据/i],
    ["分工或并行降级记录", /分工|parallelism/i],
    ["时间预算", /time|时间/i],
    ["token 预算", /token/i],
  ];
  const missing = requirements.filter(([, pattern]) => !pattern.test(content)).map(([name]) => name);
  return check("evidence-plan", missing.length === 0, missing.map((name) => `Evidence Plan 缺少${name}。`), [path]);
}

function reportDraftCheck(out) {
  const path = join(out, "report.md");
  if (!existsSync(path)) return check("report-draft", false, ["缺少 report.md 叙事草稿。"], [path]);
  const content = readFileSync(path, "utf8");
  const requirements = [
    ["架构或设计分析", /架构|设计/],
    ["Why > What 的动机或权衡", /为什么|动机|权衡|替代方案/],
    ["源码锚点", /\b[^\s`]+\.[A-Za-z0-9]+:\d+(?:-\d+)?\b/],
    ["风险、限制或开放问题", /风险|限制|开放问题|unsupported area/i],
    ["Mermaid 图", /```mermaid/],
  ];
  const missing = requirements.filter(([, pattern]) => !pattern.test(content)).map(([name]) => name);
  if (!content.trim()) missing.unshift("非空叙事内容");
  return check("report-draft", missing.length === 0, missing.map((name) => `report.md 缺少${name}。`), [path]);
}

function loadMatrices(out) {
  const directory = join(out, "module-evidence");
  if (!existsSync(directory)) return [];
  return readdirSync(directory)
    .filter((file) => file.endsWith(".json"))
    .sort()
    .map((file) => ({ path: join(directory, file), value: readJson(join(directory, file)) }));
}

function matrixCheck(coverage, matrices) {
  const coreModules = coverage.modules.filter((module) => module.classification === "core");
  const byModule = new Map(matrices.map((item) => [item.value.module, item]));
  const reasons = [];
  const evidence = [];
  if (coreModules.length === 0) reasons.push("模块分级中至少需要一个 core 模块。");
  for (const module of coreModules) {
    const matrix = byModule.get(module.name);
    if (!matrix) {
      reasons.push(`core 模块 ${module.name} 缺少 Evidence Matrix。`);
      continue;
    }
    evidence.push(matrix.path);
    for (const field of MATRIX_FIELDS) {
      if (field === "cross_module_dependencies" || field === "open_questions") {
        if (!Array.isArray(matrix.value[field])) reasons.push(`${module.name}.${field} 必须是数组。`);
      } else if (!nonEmpty(matrix.value[field])) {
        reasons.push(`${module.name}.${field} 缺失或为空。`);
      }
    }
    for (const anchor of matrix.value.source_evidence ?? []) {
      if (!ANCHOR_PATTERN.test(anchor)) reasons.push(`${module.name} 的源码证据不是 file:line 锚点: ${anchor}`);
    }
    for (const risk of matrix.value.risk_areas ?? []) {
      for (const field of ["category", "evidence", "finding", "impact"]) {
        if (!nonEmpty(risk[field])) reasons.push(`${module.name} 风险抽样缺少 ${field}。`);
      }
      if (nonEmpty(risk.evidence) && !ANCHOR_PATTERN.test(risk.evidence)) {
        reasons.push(`${module.name} 的风险证据不是 file:line 锚点: ${risk.evidence}`);
      }
    }
    for (const dependency of matrix.value.cross_module_dependencies ?? []) {
      if (!/:\d+/.test(dependency) && (matrix.value.open_questions?.length ?? 0) === 0) {
        reasons.push(`${module.name} 的跨模块依赖缺少两端锚点，也未保留为开放问题: ${dependency}`);
      }
    }
  }
  return check("module-evidence-matrix", reasons.length === 0, reasons, evidence);
}

function moduleCoverage(coverage, budget) {
  const summaries = [];
  const reasons = [];
  const evidence = [];
  for (const module of coverage.modules.filter((item) => item.classification !== "excluded")) {
    const units = coverage.units.filter((unit) => unit.module === module.name);
    const analyzedUnits = units.filter((unit) => unit.status === "analyzed" && ANCHOR_PATTERN.test(unit.anchor ?? "") && nonEmpty(unit.judgment));
    const percent = units.length === 0 ? 0 : Math.round((analyzedUnits.length / units.length) * 10000) / 100;
    const threshold = budget.coverage[module.classification];
    summaries.push({ module: module.name, classification: module.classification, total: units.length, analyzed: analyzedUnits.length, percent, threshold });
    if (percent < threshold) reasons.push(`${module.name} 覆盖率 ${percent}% 未达到 ${module.classification} 阈值 ${threshold}%。`);
    for (const unit of units.filter((item) => item.status === "analyzed" && (!ANCHOR_PATTERN.test(item.anchor ?? "") || !nonEmpty(item.judgment)))) {
      evidence.push(`未满足双硬条件: ${unit.id}`);
    }
    for (const unit of units.filter((item) => item.status === "unanalyzed" && !nonEmpty(item.skip_reason) && module.classification === "core")) {
      evidence.push(`core 未覆盖且无原因: ${unit.id}`);
      reasons.push(`core 未覆盖单元 ${unit.id} 缺少 skip_reason。`);
    }
  }
  return { ...check("key-unit-coverage", reasons.length === 0, reasons, evidence), coverage: summaries };
}

function classificationCheck(coverage) {
  const reasons = [];
  for (const module of coverage.modules) {
    if (!["core", "secondary", "excluded"].includes(module.classification)) reasons.push(`${module.name} 的 classification 非法。`);
    if (!nonEmpty(module.reason)) reasons.push(`${module.name} 缺少分级理由。`);
    if (module.classification === "excluded" && !nonEmpty(module.reason)) reasons.push(`excluded 模块 ${module.name} 必须说明排除理由。`);
  }
  return check("module-classification", reasons.length === 0, reasons, ["coverage-units.json#modules"]);
}

function unsupportedCheck(coverage, reportContent) {
  const coreNames = new Set(coverage.modules.filter((module) => module.classification === "core").map((module) => module.name));
  const moduleForFile = (file) => coverage.modules.find((module) =>
    module.name === "." ? !file.includes("/") : file === module.name || file.startsWith(`${module.name}/`))?.name;
  const coreUnparsed = coverage.unparsed.filter((file) => coreNames.has(moduleForFile(file)));
  const reasons = [];
  for (const file of coreUnparsed) {
    if (!/unsupported area/i.test(reportContent) || !reportContent.includes(file)) {
      reasons.push(`未解析 core 文件 ${file} 未在报告中声明为 unsupported area。`);
    }
  }
  return check("core-unparsed-areas", reasons.length === 0, reasons, coreUnparsed);
}

function referenceCheck(coverage, matrices, reportContent) {
  const reasons = [];
  const evidence = [];
  const matrixByModule = new Map(matrices.map((item) => [item.value.module, item.value]));
  for (const unit of coverage.units.filter((item) => item.refs_status === "missing")) {
    const matrix = matrixByModule.get(unit.module);
    if ((matrix?.cross_module_dependencies?.length ?? 0) === 0) continue;
    evidence.push(unit.id);
    const exposed = (matrix.open_questions?.length ?? 0) > 0 || (/unsupported area/i.test(reportContent) && reportContent.includes(unit.file));
    if (!exposed) reasons.push(`${unit.id} 引用不完整，但跨模块结论未暴露为开放问题或 unsupported area。`);
  }
  return check("reference-completeness", reasons.length === 0, reasons, evidence);
}

export function gate({ out, mode }) {
  const budget = budgetFor(mode);
  const coverage = readJson(join(out, "coverage-units.json"));
  const matrices = loadMatrices(out);
  const reportPath = join(out, "report.md");
  const reportContent = existsSync(reportPath) ? readFileSync(reportPath, "utf8") : "";
  const checks = [
    evidencePlanCheck(out),
    reportDraftCheck(out),
    classificationCheck(coverage),
    matrixCheck(coverage, matrices),
    moduleCoverage(coverage, budget),
    unsupportedCheck(coverage, reportContent),
    referenceCheck(coverage, matrices, reportContent),
  ];
  const result = {
    schema_version: 1,
    mode,
    budget,
    checks,
    allowed_to_synthesize: checks.every((item) => item.status === "pass"),
  };
  writeJson(join(out, "quality-gate-report.json"), result);
  return result;
}
