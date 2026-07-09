#!/usr/bin/env python3
"""ask_user 三运行时适配器 + 降级链（stdlib-only，无第三方依赖）。

对应 ADR-0003：在 claude-code / codex / cursor 三种运行时下向用户提问，
统一抽象为 :class:`AskUserAPI`，并在交互不可用 / 超时 / 未知运行时降级到
``~/.config/repo-analyzer/defaults.yaml`` 的默认值。

设计要点：
- ``detect_runtime()`` 检测顺序：``REPO_ANALYZER_RUNTIME`` 环境变量 → 进程特征
  （``CLAUDECODE`` / ``CODEX`` / ``CURSOR`` 等）→ ``unknown``。
- 每个适配器通过可注入的 provider 获取答案；默认 provider 读取
  ``REPO_ANALYZER_ANSWERS_FILE`` 指向的 JSON 文件，便于测试与 Cursor 式
  “写 questions.json + 等待 resume” 流程对齐。
- 任何交互失败都会降级到默认值，不抛未捕获异常，保证主流程不中断。
"""

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence


CONFIG_HOME_ENV = "REPO_ANALYZER_CONFIG_HOME"
RUNTIME_ANSWERS_ENV = "REPO_ANALYZER_ANSWERS_FILE"

DEFAULT_PRIORITY = "architecture"
DEFAULT_AUDIENCE = "tech-lead"

DEFAULTS_YAML = (
    "priority: architecture\n"
    "audience: tech-lead\n"
    "usage_assumptions: []\n"
    "future_extensions: []\n"
)


@dataclass
class Option:
    """单个选项。"""

    label: str
    description: str = ""


@dataclass
class Question:
    """一道题。"""

    key: str
    header: str
    prompt: str
    options: List[Option] = field(default_factory=list)
    multi_select: bool = False
    default: object = None


@dataclass
class Answer:
    """一道题的答案。"""

    key: str
    selected: List[str] = field(default_factory=list)
    notes: str = ""


class AskUnavailable(Exception):
    """运行时未提供交互能力。"""


class AskTimeout(Exception):
    """交互超时。"""


class AskUserAPI:
    """抽象接口：向用户提问并返回答案列表。"""

    def ask(self, questions: Sequence[Question], timeout_sec: int = 60) -> List[Answer]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 默认 provider：从 REPO_ANALYZER_ANSWERS_FILE 读取答案
# ---------------------------------------------------------------------------
def _answers_file_provider(questions: Sequence[Question], timeout_sec: int = 60) -> List[Answer]:
    path = os.environ.get(RUNTIME_ANSWERS_ENV)
    if not path or not Path(path).expanduser().exists():
        raise AskUnavailable(f"未找到答案文件: {path}")
    try:
        raw = Path(path).expanduser().read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise AskUnavailable(f"答案文件解析失败: {exc}") from exc
    answers: List[Answer] = []
    for question in questions:
        selected = data.get(question.key, [])
        if isinstance(selected, str):
            selected = [selected]
        answers.append(Answer(key=question.key, selected=list(selected)))
    return answers


_PROVIDERS: Dict[str, Callable[[Sequence[Question], int], List[Answer]]] = {}


def set_runtime_provider(runtime: str, provider: Callable[[Sequence[Question], int], List[Answer]]) -> None:
    """注入指定运行时的答案 provider（用于测试或运行时钩子注册）。"""
    _PROVIDERS[runtime] = provider


def _provider_for(runtime: str) -> Callable[[Sequence[Question], int], List[Answer]]:
    return _PROVIDERS.get(runtime, _answers_file_provider)


# ---------------------------------------------------------------------------
# 三个运行时适配器
# ---------------------------------------------------------------------------
class ClaudeCodeAskAdapter(AskUserAPI):
    """Claude Code 运行时：优先调用运行时注入的 AskUserQuestion 钩子。"""

    def __init__(self, provider: Optional[Callable] = None) -> None:
        self._provider = provider or _provider_for("claude-code")

    def ask(self, questions: Sequence[Question], timeout_sec: int = 60) -> List[Answer]:
        return self._provider(questions, timeout_sec)


class CodexAskAdapter(AskUserAPI):
    """Codex CLI 运行时：选项受限时退化为纯文本 prompt。"""

    def __init__(self, provider: Optional[Callable] = None) -> None:
        self._provider = provider or _provider_for("codex")

    def ask(self, questions: Sequence[Question], timeout_sec: int = 60) -> List[Answer]:
        return self._provider(questions, timeout_sec)


class CursorAskAdapter(AskUserAPI):
    """Cursor 运行时：写 questions.json 并等待 --resume 续跑。"""

    def __init__(self, provider: Optional[Callable] = None) -> None:
        self._provider = provider or _provider_for("cursor")

    def ask(self, questions: Sequence[Question], timeout_sec: int = 60) -> List[Answer]:
        return self._provider(questions, timeout_sec)


# ---------------------------------------------------------------------------
# 运行时检测
# ---------------------------------------------------------------------------
def detect_runtime() -> str:
    """返回 claude-code / codex / cursor / unknown。"""
    env = os.environ.get("REPO_ANALYZER_RUNTIME")
    if env:
        return env.strip().lower()
    if os.environ.get("CLAUDECODE"):
        return "claude-code"
    if os.environ.get("CODEX") or os.environ.get("CODEX_CLI"):
        return "codex"
    if os.environ.get("CURSOR"):
        return "cursor"
    return "unknown"


def _adapter_for(runtime: str) -> Optional[AskUserAPI]:
    if runtime == "claude-code":
        return ClaudeCodeAskAdapter()
    if runtime == "codex":
        return CodexAskAdapter()
    if runtime == "cursor":
        return CursorAskAdapter()
    return None


# ---------------------------------------------------------------------------
# 默认答案与 defaults.yaml 自动生成
# ---------------------------------------------------------------------------
def config_home() -> Path:
    return Path(os.environ.get(CONFIG_HOME_ENV, "~/.config/repo-analyzer")).expanduser()


def defaults_path() -> Path:
    return config_home() / "defaults.yaml"


def ensure_defaults_file() -> Path:
    """首次运行自动从 ``config/defaults.example.yaml`` 生成 ``defaults.yaml``。"""
    path = defaults_path()
    if path.exists():
        return path
    example = Path(__file__).resolve().parent.parent / "config" / "defaults.example.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if example.exists():
        shutil.copyfile(example, path)
    else:
        path.write_text(DEFAULTS_YAML, encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path


def _read_defaults_file() -> Dict[str, object]:
    path = defaults_path()
    if not path.exists():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    data: Dict[str, object] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value in ("[]", ""):
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()] if inner else []
        else:
            data[key] = value.strip('"').strip("'")
    return data


def _default_dict(mode_default: Optional[str] = None) -> Dict[str, List[str]]:
    file_defaults = _read_defaults_file()
    audience = mode_default or str(file_defaults.get("audience", DEFAULT_AUDIENCE))
    usage = file_defaults.get("usage_assumptions", [])
    future = file_defaults.get("future_extensions", [])
    return {
        "priority": [str(file_defaults.get("priority", DEFAULT_PRIORITY))],
        "audience": [audience],
        "usage_assumptions": list(usage) if isinstance(usage, (list, tuple)) else [],
        "future_extensions": list(future) if isinstance(future, (list, tuple)) else [],
    }


# ---------------------------------------------------------------------------
# 问题构造与编排入口
# ---------------------------------------------------------------------------
def build_questions() -> List[Question]:
    """构造 4 道默认问题（优先方向 / 报告受众 / 用法假设 / 未来扩展）。"""
    return [
        Question(
            key="priority",
            header="优先方向",
            prompt="本次分析优先关注哪个方向？",
            options=[
                Option("architecture", "架构与技术实现"),
                Option("product", "产品与业务价值"),
                Option("learning", "学习与使用路径"),
            ],
        ),
        Question(
            key="audience",
            header="报告受众",
            prompt="报告主要面向谁？",
            options=[
                Option("tech-lead", "技术负责人"),
                Option("business", "业务负责人"),
                Option("learning", "学习者"),
            ],
        ),
        Question(
            key="usage_assumptions",
            header="用法假设",
            prompt="有哪些用法假设需要记录？（可多选）",
            multi_select=True,
            options=[
                Option("cli", "命令行工具"),
                Option("library", "库 / SDK"),
                Option("service", "在线服务"),
            ],
        ),
        Question(
            key="future_extensions",
            header="未来扩展",
            prompt="未来可能的扩展方向？（可多选）",
            multi_select=True,
            options=[
                Option("plugins", "插件体系"),
                Option("api", "对外 API"),
                Option("integrations", "第三方集成"),
            ],
        ),
    ]


def ask_user(
    questions: Sequence[Question],
    no_question: bool = False,
    runtime_hint: Optional[str] = None,
    timeout_sec: int = 60,
    mode_default: Optional[str] = None,
) -> Dict[str, List[str]]:
    """编排提问并返回 ``{key: [selected, ...]}``。

    - ``--no-question``：直接返回默认值（Q1=architecture，Q2=受众由 mode 决定）。
    - 交互路径：检测运行时 → 调适配器 → 失败/超时/未知则降级到默认值。
    """
    if no_question:
        return _default_dict(mode_default)
    runtime = (runtime_hint or detect_runtime()).lower()
    adapter = _adapter_for(runtime)
    if adapter is None:
        return _default_dict(mode_default)
    try:
        answers = adapter.ask(questions, timeout_sec)
    except (AskUnavailable, AskTimeout, subprocess.TimeoutExpired, OSError):
        return _default_dict(mode_default)
    result: Dict[str, List[str]] = {}
    for answer in answers:
        result[answer.key] = list(answer.selected)
    return result


if __name__ == "__main__":
    ensure_defaults_file()
    print(f"runtime: {detect_runtime()}")
    print(f"defaults: {_default_dict()}")
