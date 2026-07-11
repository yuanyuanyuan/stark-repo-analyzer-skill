import { parseArgs, requiredPath, requireDoctor } from "./common.js";
import { assertModeRunnable } from "./capabilities.js";
import { doctor } from "./doctor.js";
import { scan } from "./scan.js";
import { summarize } from "./summarize.js";
import { units } from "./units.js";
import { gate } from "./gate.js";
import { defaultMode, resolveMode, supportedModes } from "./rules.js";

const usage = `用法: repo-analyzer <doctor|scan|units|summarize|gate> --repo <path> --out <path> [--mode standard|deep]

模式:
  --mode standard   默认；仅基线工具，忽略 Graphify/Ctags/ast-grep
  --mode deep       能力门禁；缺能力拒绝且不降级

doctor 额外选项:
  --install-prompt  打印 AI 安装 prompt（并写入 out/install-prompt.md）
  --install-mode    安装 prompt 目标模式（默认 deep）
`;

export async function run(args) {
  const { command, options, flags } = parseArgs(args);
  if (!command) throw new Error(usage);

  if (command === "doctor") {
    const mode = options.mode ? resolveMode(options.mode) : defaultMode();
    const report = doctor({
      repo: requiredPath(options, "repo"),
      out: requiredPath(options, "out"),
      mode,
      printInstallPrompt: Boolean(flags["install-prompt"]),
      installTargetMode: options["install-mode"],
    });
    console.log(JSON.stringify({
      command,
      artifact: "doctor-report.json",
      allowed: report.allowed,
      mode: report.mode,
      available_modes: report.capability_matrix.available_modes,
      blocked_modes: report.capability_matrix.blocked_modes,
    }));
    if (!report.allowed) process.exitCode = 2;
    return;
  }

  const repo = requiredPath(options, "repo");
  const out = requiredPath(options, "out");
  const mode = resolveMode(options.mode ?? defaultMode());

  // gate only validates artifacts/budgets; capability gating happens in doctor/scan/units.
  if (command === "gate") {
    const report = gate({ out, mode });
    console.log(JSON.stringify({
      command,
      artifact: "quality-gate-report.json",
      allowed: report.allowed_to_synthesize,
      mode: report.mode,
      rules_version: report.rules_version,
    }));
    if (!report.allowed_to_synthesize) process.exitCode = 3;
    return;
  }

  const doctorReport = requireDoctor(repo, out, mode);

  if (["scan", "units", "summarize"].includes(command)) {
    try {
      assertModeRunnable(mode, doctorReport.capability_matrix ?? {
        available_modes: doctorReport.allowed_standard ? ["standard"] : [],
        missing_capabilities: { standard: [], deep: [] },
      });
    } catch (error) {
      if (error.code === "MODE_BLOCKED") {
        console.error(error.message);
        process.exitCode = 2;
        return;
      }
      throw error;
    }
  }

  if (command === "scan") {
    const report = scan({ repo, out, mode, doctor: doctorReport });
    console.log(JSON.stringify({
      command,
      artifact: "repo-map.json",
      files: Object.values(report.files).flat().length,
      mode,
      tooling_level: mode === "deep" ? "enhanced" : "baseline",
    }));
    return;
  }

  if (command === "summarize") {
    summarize({ repo, out, mode });
    console.log(JSON.stringify({ command, artifact: "repo-map.md", mode }));
    return;
  }

  if (command === "units") {
    if (mode === "standard") {
      const report = units({ repo, out, doctor: doctorReport, mode: "standard" });
      console.log(JSON.stringify({
        command,
        artifact: "coverage-units.json",
        units: report.units.length,
        parse_rate: report.parse_rate,
        mode: "standard",
        tooling_level: "baseline",
        limitations: report.limitations,
      }));
      return;
    }

    if (!doctorReport.deep_enumerator && !doctorReport.enumerator) {
      console.error("deep 模式缺少符号枚举能力；拒绝执行且不降级 standard。");
      process.exitCode = 2;
      return;
    }

    const report = units({
      repo,
      out,
      doctor: {
        ...doctorReport,
        enumerator: doctorReport.deep_enumerator ?? doctorReport.enumerator,
      },
      mode: "deep",
    });
    console.log(JSON.stringify({
      command,
      artifact: "coverage-units.json",
      units: report.units.length,
      parse_rate: report.parse_rate,
      mode: "deep",
      tooling_level: "enhanced",
    }));
    return;
  }

  throw new Error(`未知命令: ${command}\n支持模式: ${supportedModes().join(", ")}\n${usage}`);
}
