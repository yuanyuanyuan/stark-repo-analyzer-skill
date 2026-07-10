import { parseArgs, requiredPath, requireDoctor } from "./common.js";
import { doctor } from "./doctor.js";
import { scan } from "./scan.js";
import { summarize } from "./summarize.js";
import { units } from "./units.js";
import { gate } from "./gate.js";

const usage = `用法: repo-analyzer <doctor|scan|units|summarize|gate> --repo <path> --out <path>`;

export async function run(args) {
  const { command, options } = parseArgs(args);
  if (!command) throw new Error(usage);

  if (command === "doctor") {
    const report = doctor({ repo: requiredPath(options, "repo"), out: requiredPath(options, "out") });
    console.log(JSON.stringify({ command, artifact: "doctor-report.json", allowed: report.allowed }));
    if (!report.allowed) process.exitCode = 2;
    return;
  }

  const repo = requiredPath(options, "repo");
  const out = requiredPath(options, "out");
  const doctorReport = requireDoctor(repo, out);

  if (command === "scan") {
    const report = scan({ repo, out });
    console.log(JSON.stringify({ command, artifact: "repo-map.json", files: Object.values(report.files).flat().length }));
    return;
  }

  if (command === "summarize") {
    summarize({ repo, out });
    console.log(JSON.stringify({ command, artifact: "repo-map.md" }));
    return;
  }

  if (command === "units") {
    const report = units({ repo, out, doctor: doctorReport });
    console.log(JSON.stringify({ command, artifact: "coverage-units.json", units: report.units.length, parse_rate: report.parse_rate }));
    return;
  }

  if (command === "gate") {
    const report = gate({ out, mode: options.mode ?? "standard" });
    console.log(JSON.stringify({ command, artifact: "quality-gate-report.json", allowed: report.allowed_to_synthesize }));
    if (!report.allowed_to_synthesize) process.exitCode = 3;
    return;
  }

  throw new Error(`未知命令: ${command}\n${usage}`);
}
