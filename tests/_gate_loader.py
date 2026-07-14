"""Load the Skill-bundled Graphify gate under a stable module name for tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SKILL_GATE_PATH = ROOT / "skills" / "repo-analyzer" / "scripts" / "graphify_gate.py"
SKILL_SCHEMA_PATH = (
    ROOT
    / "skills"
    / "repo-analyzer"
    / "references"
    / "contracts"
    / "graphify-gate-status.schema.json"
)
MODULE_NAME = "repo_analyzer_skill_graphify_gate"


def load_skill_gate() -> ModuleType:
    existing = sys.modules.get(MODULE_NAME)
    if existing is not None and Path(getattr(existing, "__file__", "")) == SKILL_GATE_PATH:
        return existing
    spec = importlib.util.spec_from_file_location(MODULE_NAME, SKILL_GATE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load gate from {SKILL_GATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


def patch_target(name: str) -> str:
    return f"{MODULE_NAME}.{name}"
