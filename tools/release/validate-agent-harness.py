#!/usr/bin/env python3
"""Validate Agent harness navigation scaffolding (not product UAT / not Judge).

Checks required files, AGENTS.md route keywords, relative links among harness
docs, active map.yaml entrypoints, ADR index drift (e.g. ADR-0025), and a
minimal green≠ship completion-semantics table.

This check is NOT Judge pass and NOT real-regression UAT. Exit 0 only means
harness navigation scaffolding is mechanically consistent.

Exit codes:
  0 success
  1 validation failure
  2 usage/runtime error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - stdlib fallback
    yaml = None  # type: ignore


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


REQUIRED_FILES = [
    "AGENTS.md",
    "CONTEXT.md",
    "docs/code-map/README.md",
    "docs/code-map/map.yaml",
    "docs/spec/product-map.md",
    "docs/dev-rules/README.md",
    "docs/dev-rules/workflows/README.md",
    "docs/dev-rules/agent-boundaries/README.md",
    "docs/adr/0028-agent-harness-progressive-disclosure-without-parallel-ai-harness.md",
    "tools/release/validate-agent-harness.py",
]

AGENTS_KEYWORDS = [
    "docs/code-map/",
    "docs/spec/product-map.md",
    "docs/dev-rules/workflows/",
    "docs/dev-rules/agent-boundaries/",
    "validate-agent-harness",
    "docs/dev-rules/output-style/",
    "docs/dev-rules/document-control/",
    "docs/dev-rules/dual-agent-review/",
    # Completion-semantics anti-misread (T3): table + hard reminder
    "绿勾",
    "Judge",
    "真实回归 UAT",
]

REQUIRED_SECTION_SNIPPETS: dict[str, list[str]] = {
    "docs/spec/product-map.md": ["场景 1", "边界", "同步规则"],
    "docs/dev-rules/workflows/README.md": ["通用骨架", "任务类型入口", "Same-Type Failure"],
    "docs/dev-rules/agent-boundaries/README.md": ["硬规则", "暂停条件", "Same-Type Failure"],
    "docs/code-map/README.md": ["60 秒用法", "cheat sheet"],
}

LINK_RE = re.compile(r"\]\((?!https?://)(?!#)([^)\s]+)\)")


def _err(msgs: list[str], code: int = 1) -> int:
    print(f"[validate-agent-harness] FAILED (exit {code})", file=sys.stderr)
    for m in msgs:
        print(f"  - {m}", file=sys.stderr)
    return code


def check_required_files(root: Path) -> list[str]:
    missing = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            missing.append(f"missing file: {rel}")
    return missing


def check_agents_keywords(root: Path) -> list[str]:
    path = root / "AGENTS.md"
    if not path.is_file():
        return ["AGENTS.md is missing"]
    text = path.read_text(encoding="utf-8")
    errs = []
    for kw in AGENTS_KEYWORDS:
        if kw not in text:
            errs.append(f"AGENTS.md missing route keyword/path: {kw}")
    return errs


def check_sections(root: Path) -> list[str]:
    errs: list[str] = []
    for rel, snippets in REQUIRED_SECTION_SNIPPETS.items():
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for snip in snippets:
            if snip not in text:
                errs.append(f"{rel}: missing required snippet '{snip}'")
    return errs


def check_dev_rules_index(root: Path) -> list[str]:
    text = (root / "docs/dev-rules/README.md").read_text(encoding="utf-8")
    errs = []
    for name in ("workflows/", "agent-boundaries/"):
        if name not in text:
            errs.append(f"docs/dev-rules/README.md missing registry entry for {name}")
    return errs


def check_relative_links(root: Path) -> list[str]:
    """Check relative md/py links from harness-related markdown files."""
    roots = [
        root / "AGENTS.md",
        root / "docs/spec/product-map.md",
        root / "docs/dev-rules/workflows/README.md",
        root / "docs/dev-rules/agent-boundaries/README.md",
        root / "docs/code-map/README.md",
        root / "docs/dev-rules/README.md",
    ]
    errs: list[str] = []
    for path in roots:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            target = m.group(1).split("#", 1)[0].strip()
            if not target or target.startswith("mailto:"):
                continue
            # skip pure anchors already filtered; allow query-less paths
            if "://" in target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                # outside repo — skip
                continue
            if not resolved.exists():
                rel = path.relative_to(root)
                errs.append(f"{rel}: broken link to {target}")
    return errs


def _parse_map_yaml(text: str) -> dict:
    if yaml is not None:
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    # Minimal fallback: collect entrypoints lines under features
    return {"_raw": text}


def check_map_yaml(root: Path) -> list[str]:
    path = root / "docs/code-map/map.yaml"
    if not path.is_file():
        return ["docs/code-map/map.yaml missing"]
    text = path.read_text(encoding="utf-8")
    errs: list[str] = []
    if "agent-harness-navigation" not in text:
        errs.append("map.yaml missing feature id agent-harness-navigation")

    data = _parse_map_yaml(text)
    entrypoints: list[str] = []
    if yaml is not None and "features" in data:
        for feat in data.get("features") or []:
            if not isinstance(feat, dict):
                continue
            if feat.get("status") == "deprecated":
                continue
            layers = feat.get("layers") or {}
            if not isinstance(layers, dict):
                continue
            for layer in layers.values():
                if not isinstance(layer, dict):
                    continue
                for ep in layer.get("entrypoints") or []:
                    if isinstance(ep, str):
                        entrypoints.append(ep)
    else:
        # fallback regex
        for m in re.finditer(r"-\s+(skills/|docs/|tools/|AGENTS\.md|CONTEXT\.md|\.codex/)[^\s]+", text):
            entrypoints.append(m.group(0).lstrip("- ").strip())

    missing_eps = []
    for ep in sorted(set(entrypoints)):
        # strip quotes
        ep_clean = ep.strip("\"'")
        if not (root / ep_clean).exists():
            missing_eps.append(ep_clean)
    # Cap noise: report up to 20
    for ep in missing_eps[:20]:
        errs.append(f"map.yaml entrypoint missing on disk: {ep}")
    if len(missing_eps) > 20:
        errs.append(f"... and {len(missing_eps) - 20} more missing entrypoints")
    return errs


def check_adr_index_baseline(root: Path) -> list[str]:
    """Fail if ADR-0025 is indexed as unimplemented+proposed (stale drift).

    Behavioral guard only: does not lock full prose. Not Judge / not UAT.
    """
    path = root / "docs/adr/README.md"
    if not path.is_file():
        return ["docs/adr/README.md missing"]
    text = path.read_text(encoding="utf-8")
    errs: list[str] = []

    # Required: 0025 and 0028 appear in the implemented/current baseline narrative
    if "0025" not in text:
        errs.append("docs/adr/README.md missing ADR-0025 reference")
    if "0028" not in text:
        errs.append("docs/adr/README.md missing ADR-0028 reference")

    # Stale combination: pending section still pairs 0025 with proposed/unmigrated
    pending_idx = text.find("## 已接受但尚未实施")
    if pending_idx != -1:
        next_h2 = text.find("\n## ", pending_idx + 1)
        pending_block = text[pending_idx : next_h2 if next_h2 != -1 else None]
        has_0025_pending = "0025" in pending_block or "Skill 交付与安装" in pending_block
        has_stale = (
            "proposed" in pending_block
            or "尚未迁移" in pending_block
            or "均为 `proposed`" in pending_block
        )
        if has_0025_pending and has_stale:
            errs.append(
                "docs/adr/README.md: ADR-0025 still listed under "
                "「已接受但尚未实施」 with proposed/unmigrated wording "
                "(skill-distribution is completed)"
            )

    # Baseline adoption sentence should reach 0028, not stop at 0027-only
    if re.search(r"当前主线只采用.*ADR-0026 至 ADR-0027", text):
        errs.append(
            "docs/adr/README.md: baseline adoption list stops at ADR-0027 "
            "(must include ADR-0025/0028 as implemented baseline)"
        )

    return errs


def check_completion_semantics_table(root: Path) -> list[str]:
    """Require a short green≠ship table in AGENTS and/or version-release."""
    agents = root / "AGENTS.md"
    vr = root / "docs/dev-rules/version-release/README.md"
    errs: list[str] = []
    agents_text = agents.read_text(encoding="utf-8") if agents.is_file() else ""
    vr_text = vr.read_text(encoding="utf-8") if vr.is_file() else ""
    combined = agents_text + "\n" + vr_text

    required_topics = [
        ("Judge", "Judge pass / Judge `pass`"),
        ("Harness", "Harness 契约校验"),
        ("安全扫描", "发布前安全扫描 / 安全扫描"),
        ("Release", "GitHub Release / tag"),
        ("真实回归 UAT", "真实回归 UAT"),
    ]
    hosts = []
    if "绿勾" in agents_text or "不等于" in agents_text:
        hosts.append("AGENTS.md")
    if "绿勾" in vr_text or ("不等于" in vr_text and "Judge" in vr_text):
        hosts.append("version-release")
    if not hosts:
        errs.append(
            "missing green≠ship completion table in AGENTS.md and/or "
            "docs/dev-rules/version-release/README.md"
        )
        return errs

    for needle, label in required_topics:
        if needle not in combined:
            errs.append(f"completion-semantics table missing topic: {label}")

    # Keep the hard reminder sentence on AGENTS
    if agents.is_file():
        if "不等于真实回归 UAT" not in agents_text and not (
            "Judge" in agents_text and "真实回归 UAT" in agents_text
        ):
            errs.append(
                "AGENTS.md must keep Judge pass ≠ real-regression UAT reminder"
            )

    return errs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: inferred from script location)",
    )
    args = parser.parse_args(argv)
    root = (args.root or repo_root()).resolve()
    if not root.is_dir():
        return _err([f"root is not a directory: {root}"], code=2)

    print(f"[validate-agent-harness] root={root}")
    checks: list[tuple[str, list[str]]] = [
        ("required files", check_required_files(root)),
        ("AGENTS.md routes", check_agents_keywords(root)),
        ("required sections", check_sections(root)),
        ("dev-rules index", check_dev_rules_index(root)),
        ("relative links", check_relative_links(root)),
        ("map.yaml", check_map_yaml(root)),
        ("ADR index baseline", check_adr_index_baseline(root)),
        ("completion semantics", check_completion_semantics_table(root)),
    ]

    overall_errs: list[str] = []
    for name, errs in checks:
        marker = "PASS" if not errs else "FAIL"
        print(f"  [{marker}] {name}")
        overall_errs.extend(errs)

    if overall_errs:
        return _err(overall_errs, code=1)

    print("[validate-agent-harness] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
