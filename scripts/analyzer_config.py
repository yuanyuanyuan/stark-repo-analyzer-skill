#!/usr/bin/env python3
"""Configuration loading and merging for repo-analyzer.

Extracted from repo_analyzer.py (T02).
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from analyzer_common import CONFIG_HOME_ENV


def config_home() -> Path:
    return Path(os.environ.get(CONFIG_HOME_ENV, "~/.config/repo-analyzer")).expanduser()


def parse_scalar(value: str):
    value = value.strip().strip('"').strip("'")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


def parse_simple_yaml(text: str) -> dict:
    result = {}
    current = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith(" ") and ":" in raw:
            key, value = raw.split(":", 1)
            key = key.strip()
            if value.strip():
                result[key] = parse_scalar(value)
                current = None
            else:
                result[key] = [] if key == "extends" else {}
                current = key
            continue
        if current == "extends" and raw.strip().startswith("- "):
            result[current].append(parse_scalar(raw.strip()[2:]))
        elif current and ":" in raw:
            key, value = raw.strip().split(":", 1)
            result[current][key.strip()] = parse_scalar(value)
    return result


def merge_config(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if key == "extends":
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged


def flatten_config(config: dict) -> dict:
    flat = dict(config)
    if isinstance(config.get("target_coverage"), dict):
        flat["target_coverage_core"] = config["target_coverage"].get("core", flat.get("target_coverage_core"))
        flat["target_coverage_minor"] = config["target_coverage"].get("minor", flat.get("target_coverage_minor"))
    if isinstance(config.get("sla_budget"), dict):
        flat["sla_minutes"] = config["sla_budget"].get("minutes", flat.get("sla_minutes"))
    return flat


def load_config_file(path: Path, seen=None) -> dict:
    seen = seen or set()
    config_path = path.expanduser().resolve()
    if config_path in seen:
        raise SystemExit(f"配置文件继承循环: {config_path}")
    if not config_path.exists():
        return {}
    seen.add(config_path)
    try:
        text = config_path.read_text(encoding="utf-8")
        config = json.loads(text) if config_path.suffix == ".json" else parse_simple_yaml(text)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"配置文件读取失败: {config_path}: {exc}") from exc
    merged = {}
    for parent in config.get("extends", []) if isinstance(config.get("extends"), list) else []:
        merged = merge_config(merged, load_config_file(Path(str(parent)), seen))
    return merge_config(merged, config)


def load_config(path: str) -> dict:
    explicit = Path(path).expanduser() if path else config_home() / "defaults.yaml"
    return flatten_config(load_config_file(explicit))


def env_config() -> dict:
    mapping = {
        "REPO_ANALYZER_MODE": ("mode", str),
        "REPO_ANALYZER_NO_QUESTION": ("no_question", bool_config),
        "REPO_ANALYZER_OFFLINE": ("offline", bool_config),
        "REPO_ANALYZER_TARGET_COVERAGE_CORE": ("target_coverage_core", float),
        "REPO_ANALYZER_TARGET_COVERAGE_MINOR": ("target_coverage_minor", float),
        "REPO_ANALYZER_SLA_BUDGET_MINUTES": ("sla_minutes", float),
        "REPO_ANALYZER_COVERAGE_ENGINE": ("coverage_engine", str),
        "REPO_ANALYZER_AGENT_MODE": ("agent_mode", str),
        "REPO_ANALYZER_AGENT_COMMAND": ("agent_command", str),
        "REPO_ANALYZER_AGENT_MODEL": ("agent_model", str),
        "REPO_ANALYZER_AGENT_REASONING_EFFORT": ("agent_reasoning_effort", str),
        "REPO_ANALYZER_AGENT_MAX_ATTEMPTS": ("agent_max_attempts", int),
        "REPO_ANALYZER_AGENT_TIMEOUT_SECONDS": ("agent_timeout_seconds", int),
    }
    result = {}
    for name, (key, cast) in mapping.items():
        if name in os.environ:
            result[key] = cast(os.environ[name])
    return result


def last_session_path() -> Path:
    return config_home() / "last-session.json"


def load_last_session(use_last_pref: bool) -> dict:
    path = last_session_path()
    if not use_last_pref or not path.exists():
        return {}
    if time.time() - path.stat().st_mtime > 30 * 24 * 60 * 60:
        path.unlink()
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("flags_used", {})
    except (OSError, json.JSONDecodeError):
        return {}


def bool_config(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def set_if_default(args: argparse.Namespace, key: str, value) -> None:
    defaults = {
        "mode": "tech-lead",
        "no_question": False,
        "offline": False,
        "coverage_engine": "auto",
        "agent_mode": "codex",
        "agent_command": "",
        "agent_model": "",
        "agent_reasoning_effort": "",
    }
    if getattr(args, key) == defaults.get(key):
        setattr(args, key, value)


def apply_config_values(args: argparse.Namespace, config: dict, force: bool = False) -> None:
    if not config:
        return
    if "mode" in config:
        setattr(args, "mode", str(config["mode"])) if force else set_if_default(args, "mode", str(config["mode"]))
    if "no_question" in config:
        setattr(args, "no_question", bool_config(config["no_question"])) if force else set_if_default(args, "no_question", bool_config(config["no_question"]))
    if "offline" in config:
        setattr(args, "offline", bool_config(config["offline"])) if force else set_if_default(args, "offline", bool_config(config["offline"]))
    if "target_coverage_core" in config and (force or args.target_coverage_core is None):
        args.target_coverage_core = float(config["target_coverage_core"])
    if "target_coverage_minor" in config and (force or args.target_coverage_minor is None):
        args.target_coverage_minor = float(config["target_coverage_minor"])
    if "sla_minutes" in config and (force or args.sla_minutes is None):
        args.sla_minutes = float(config["sla_minutes"])
    if "coverage_engine" in config:
        setattr(args, "coverage_engine", str(config["coverage_engine"])) if force else set_if_default(args, "coverage_engine", str(config["coverage_engine"]))
    if "agent_mode" in config:
        setattr(args, "agent_mode", str(config["agent_mode"])) if force else set_if_default(args, "agent_mode", str(config["agent_mode"]))
    if "agent_command" in config:
        setattr(args, "agent_command", str(config["agent_command"])) if force else set_if_default(args, "agent_command", str(config["agent_command"]))
    if "agent_model" in config:
        setattr(args, "agent_model", str(config["agent_model"])) if force else set_if_default(args, "agent_model", str(config["agent_model"]))
    if "agent_reasoning_effort" in config:
        setattr(args, "agent_reasoning_effort", str(config["agent_reasoning_effort"])) if force else set_if_default(args, "agent_reasoning_effort", str(config["agent_reasoning_effort"]))
    if "agent_max_attempts" in config and (force or args.agent_max_attempts is None):
        args.agent_max_attempts = int(config["agent_max_attempts"])
    if "agent_timeout_seconds" in config and (force or args.agent_timeout_seconds is None):
        args.agent_timeout_seconds = int(config["agent_timeout_seconds"])


def save_last_session(args: argparse.Namespace) -> None:
    path = last_session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "flags_used": {
            "mode": args.mode,
            "no_question": bool(args.no_question),
            "offline": bool(args.offline),
            "coverage_engine": args.coverage_engine,
            "agent_mode": args.agent_mode,
            "agent_command": args.agent_command,
            "agent_model": args.agent_model,
            "agent_reasoning_effort": args.agent_reasoning_effort,
            "agent_max_attempts": args.agent_max_attempts,
            "agent_timeout_seconds": args.agent_timeout_seconds,
            "resume": bool(args.resume),
        },
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def apply_config(args: argparse.Namespace) -> argparse.Namespace:
    apply_config_values(args, load_config(args.config))
    apply_config_values(args, load_last_session(args.use_last_pref))
    apply_config_values(args, env_config(), force=True)
    args.target_coverage_core = 0.8 if args.target_coverage_core is None else args.target_coverage_core
    args.target_coverage_minor = 0.2 if args.target_coverage_minor is None else args.target_coverage_minor
    args.sla_minutes = 30.0 if args.sla_minutes is None else args.sla_minutes
    args.agent_model = "5.4" if not args.agent_model else args.agent_model
    args.agent_reasoning_effort = "medium" if not args.agent_reasoning_effort else args.agent_reasoning_effort
    args.agent_max_attempts = 3 if args.agent_max_attempts is None else args.agent_max_attempts
    args.agent_timeout_seconds = 0 if args.agent_timeout_seconds is None else args.agent_timeout_seconds
    return args
