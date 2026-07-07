#!/usr/bin/env python3
"""Render repo-analyzer audience reports from REPORT_DATA.json."""

import argparse
import json
import re
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates"
REPORT_MODES = ("tech-lead", "business", "learning")


def render_template(template: str, data: dict) -> str:
    def replace(match: re.Match) -> str:
        key = match.group(1).strip()
        value = data.get(key, "")
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, indent=2)
        return str(value)

    return re.sub(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}", replace, template)


def render_report(data_dir: Path, mode: str) -> str:
    data = json.loads((data_dir / "REPORT_DATA.json").read_text(encoding="utf-8"))
    template = (TEMPLATE_DIR / f"ANALYSIS_REPORT.{mode}.tmpl.md").read_text(encoding="utf-8")
    context = {**data, **data.get("audiences", {}).get(mode, {})}
    return render_template(template, context)


def render_all(data_dir: Path, mode: str) -> None:
    modes = REPORT_MODES if mode == "all" else (mode,)
    for report_mode in modes:
        body = render_report(data_dir, report_mode)
        (data_dir / f"ANALYSIS_REPORT.{report_mode}.md").write_text(body, encoding="utf-8")
    if mode == "all":
        overview_template = (TEMPLATE_DIR / "ANALYSIS_REPORT.overview.tmpl.md").read_text(encoding="utf-8")
        data = json.loads((data_dir / "REPORT_DATA.json").read_text(encoding="utf-8"))
        (data_dir / "ANALYSIS_REPORT.md").write_text(render_template(overview_template, data), encoding="utf-8")
    else:
        (data_dir / "ANALYSIS_REPORT.md").write_text(render_report(data_dir, mode), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render repo-analyzer reports from REPORT_DATA.json.")
    parser.add_argument("--template", choices=[*REPORT_MODES, "all"], default="all")
    parser.add_argument("--data", default="analysis", help="analysis output directory")
    return parser


def main(argv: Sequence[str] = None) -> int:
    args = build_parser().parse_args(argv)
    render_all(Path(args.data).expanduser().resolve(), args.template)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
