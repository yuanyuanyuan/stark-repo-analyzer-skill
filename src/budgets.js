export const BUDGETS = {
  quick: {
    mode: "quick",
    time_minutes: 30,
    token_budget: 30000,
    max_agents: 3,
    evidence_tokens_per_agent: 8000,
    report_words: 4000,
    risk_sampling: "每个核心模块至少 1 条最相关风险路径",
    quality_gate_minimum: "全部机械检查通过；core/secondary 覆盖率至少 30%/10%",
    coverage: { core: 30, secondary: 10 },
  },
  standard: {
    mode: "standard",
    time_minutes: 90,
    token_budget: 90000,
    max_agents: 6,
    evidence_tokens_per_agent: 14000,
    report_words: 9000,
    risk_sampling: "每个核心模块至少 1 条风险路径，重要边界追加抽样",
    quality_gate_minimum: "全部机械检查通过；core/secondary 覆盖率至少 60%/30%",
    coverage: { core: 60, secondary: 30 },
  },
  deep: {
    mode: "deep",
    time_minutes: 240,
    token_budget: 240000,
    max_agents: 8,
    evidence_tokens_per_agent: 24000,
    report_words: 18000,
    risk_sampling: "核心模块多路径抽样，并覆盖边缘路径与替代方案",
    quality_gate_minimum: "全部机械检查通过；core/secondary 覆盖率至少 90%/60%",
    coverage: { core: 90, secondary: 60 },
  },
};

export function budgetFor(mode) {
  const budget = BUDGETS[mode];
  if (!budget) throw new Error(`未知分析模式: ${mode}；可选 quick、standard、deep。`);
  return budget;
}
