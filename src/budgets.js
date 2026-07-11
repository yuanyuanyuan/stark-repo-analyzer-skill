import { loadModes, resolveMode } from "./rules.js";

const MODE_BUDGETS = {
  standard: {
    time_minutes: 90,
    token_budget: 90000,
    max_agents: 6,
    evidence_tokens_per_agent: 14000,
    report_words: 9000,
    risk_sampling: "每个核心模块至少 1 条风险路径，重要边界追加抽样",
    quality_gate_minimum: "全部机械检查通过；core/secondary 覆盖率至少 60%/30%",
  },
  deep: {
    time_minutes: 240,
    token_budget: 240000,
    max_agents: 8,
    evidence_tokens_per_agent: 24000,
    report_words: 18000,
    risk_sampling: "核心模块多路径抽样，并覆盖边缘路径与替代方案",
    quality_gate_minimum: "全部机械检查通过；core/secondary 覆盖率至少 90%/60%",
  },
};

export function budgetFor(mode) {
  const resolved = resolveMode(mode);
  const modes = loadModes();
  const policy = modes.modes[resolved];
  const budget = MODE_BUDGETS[resolved];
  return {
    mode: resolved,
    ...budget,
    coverage: { ...policy.coverage },
    tooling_level: policy.tooling_level,
    rules_version: modes.rules_version,
  };
}

// Back-compat export shape for callers that listed budgets map.
export const BUDGETS = Object.fromEntries(
  Object.keys(MODE_BUDGETS).map((mode) => [mode, budgetFor(mode)]),
);
