#!/usr/bin/env python3
"""Validate that adapter manifests project the root VERSION."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    distribution_url = "https://github.com/yuanyuanyuan/stark-repo-analyzer-skill"
    if not version:
        print("FAIL: VERSION is empty")
        return 1

    failures: list[str] = []

    claude_plugin = load_json(root / ".claude-plugin" / "plugin.json")
    if claude_plugin.get("version") != version:
        failures.append(
            f".claude-plugin/plugin.json version {claude_plugin.get('version')!r} != {version!r}"
        )
    if claude_plugin.get("repository") != distribution_url:
        failures.append(".claude-plugin/plugin.json repository must match the distribution URL")

    claude_market = load_json(root / ".claude-plugin" / "marketplace.json")
    plugins = claude_market.get("plugins") if isinstance(claude_market, dict) else None
    if not isinstance(plugins, list) or not plugins:
        failures.append(".claude-plugin/marketplace.json missing plugins")
    else:
        market_version = plugins[0].get("version")
        if market_version != version:
            failures.append(
                f".claude-plugin/marketplace.json plugins[0].version {market_version!r} != {version!r}"
            )

    codex_plugin = load_json(root / ".codex-plugin" / "plugin.json")
    if codex_plugin.get("version") != version:
        failures.append(
            f".codex-plugin/plugin.json version {codex_plugin.get('version')!r} != {version!r}"
        )
    if codex_plugin.get("skills") != "./skills/":
        failures.append(".codex-plugin/plugin.json skills must be './skills/'")
    if codex_plugin.get("repository") != distribution_url:
        failures.append(".codex-plugin/plugin.json repository must match the distribution URL")

    codex_market = load_json(root / ".agents" / "plugins" / "marketplace.json")
    if not isinstance(codex_market, dict) or codex_market.get("name") != "repo-analyzer":
        failures.append(".agents/plugins/marketplace.json name must be repo-analyzer")
    codex_plugins = codex_market.get("plugins") if isinstance(codex_market, dict) else None
    if not isinstance(codex_plugins, list) or not codex_plugins:
        failures.append(".agents/plugins/marketplace.json missing plugins")
    else:
        source = codex_plugins[0].get("source")
        if source != {"source": "local", "path": "./"}:
            failures.append(
                f".agents/plugins/marketplace.json source {source!r} must point at local ./"
            )

    package_json = root / "package.json"
    if package_json.exists():
        package = load_json(package_json)
        if package.get("version") != version:
            failures.append(f"package.json version {package.get('version')!r} != {version!r}")
        repository = package.get("repository")
        if not isinstance(repository, dict) or repository.get("url") != distribution_url:
            failures.append("package.json repository.url must match the distribution URL")

    core_list = root / "tools" / "release" / "core-package-files.txt"
    if not core_list.is_file():
        failures.append("tools/release/core-package-files.txt missing")
    else:
        for line in core_list.read_text(encoding="utf-8").splitlines():
            item = line.strip()
            if not item or item.startswith("#"):
                continue
            if not (root / item).is_file():
                failures.append(f"core package file missing: {item}")

    if failures:
        print("Release metadata validation: FAIL")
        for item in failures:
            print(f"  - {item}")
        return 1

    print(f"Release metadata validation: PASS (version={version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
