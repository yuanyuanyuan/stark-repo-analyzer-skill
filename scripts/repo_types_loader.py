#!/usr/bin/env python3
"""受限 YAML 子集加载器（stdlib-only，无 PyYAML 依赖）。

该模块解析 `config/repo-types.yaml`，取代 `scripts/repo_analyzer.py` 内嵌的
`SLICES` 常量。只支持本 skill 实际用到的结构：

- 顶层标量：``key: value``
- 顶层映射：``key:`` 后跟缩进的 block 映射
- 顶层 / 嵌套列表：``- `` 开头的 block 列表（列表项为映射或标量）
- 行内流列表：``patterns: ["*.tsx", "*.jsx"]``
- 行内流映射：``{ k: v, k2: v2 }``（保留能力，本文件未使用）

不处理锚点、多文档、复杂嵌套等完整 YAML 特性。
"""

import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


# ---------------------------------------------------------------------------
# 受限 YAML 子集解析
# ---------------------------------------------------------------------------
def _strip_comment(line: str) -> str:
    """去掉整行注释与行尾 `` #`` 注释（本文件值在引号内不含 '#'）。"""
    stripped = line.rstrip("\n").rstrip("\r")
    if stripped.lstrip().startswith("#"):
        return ""
    idx = stripped.find(" #")
    if idx != -1:
        return stripped[:idx]
    return stripped


def _split_flow(inner: str) -> List[str]:
    """在流集合（[...] / {...}）顶层按逗号切分，忽略引号与括号内部的逗号。"""
    parts: List[str] = []
    buf: List[str] = []
    depth = 0
    quote = None
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ('"', "'"):
            quote = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return [part for part in parts if part != ""]


def _parse_scalar_token(token: str):
    token = token.strip()
    if token == "":
        return None
    if token.startswith("[") and token.endswith("]"):
        inner = token[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar_token(item) for item in _split_flow(inner)]
    if token.startswith("{") and token.endswith("}"):
        inner = token[1:-1].strip()
        if not inner:
            return {}
        mapping: Dict[str, object] = {}
        for part in _split_flow(inner):
            key, _, value = part.partition(":")
            mapping[key.strip()] = _parse_scalar_token(value)
        return mapping
    if (token[0] == '"' and token[-1] == '"') or (token[0] == "'" and token[-1] == "'"):
        return token[1:-1]
    low = token.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in ("null", "~", "none"):
        return None
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token


def _parse_yaml(text: str) -> dict:
    raw_lines: List[Tuple[int, str]] = []
    for line in text.splitlines():
        stripped = _strip_comment(line)
        if stripped.strip() == "":
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        raw_lines.append((indent, stripped.strip()))

    index = {"i": 0}

    def parse_node(expected_indent: int):
        if index["i"] >= len(raw_lines):
            return {}
        _indent, content = raw_lines[index["i"]]
        if content.startswith("- "):
            return parse_list(_indent)
        return parse_mapping(_indent)

    def parse_mapping(indent: int) -> dict:
        result: Dict[str, object] = {}
        while index["i"] < len(raw_lines):
            cur_indent, content = raw_lines[index["i"]]
            if cur_indent != indent or content.startswith("- "):
                break
            key, _sep, value = content.partition(":")
            key = key.strip()
            value = value.strip()
            index["i"] += 1
            if value == "":
                if index["i"] < len(raw_lines):
                    _nxt_indent, _nxt_content = raw_lines[index["i"]]
                    if _nxt_indent > indent:
                        result[key] = parse_node(_nxt_indent)
                        continue
                result[key] = {}
            else:
                result[key] = _parse_scalar_token(value)
        return result

    def parse_list(indent: int) -> list:
        items: List[object] = []
        while index["i"] < len(raw_lines):
            cur_indent, content = raw_lines[index["i"]]
            if cur_indent != indent or not content.startswith("- "):
                break
            item_body = content[2:].strip()
            index["i"] += 1
            if ":" in item_body and not (item_body.startswith("[") or item_body.startswith("{")):
                raw_lines.insert(index["i"], (indent + 2, item_body))
                items.append(parse_mapping(indent + 2))
            else:
                items.append(_parse_scalar_token(item_body))
        return items

    return parse_node(0)


# ---------------------------------------------------------------------------
# RepoTypeLoader
# ---------------------------------------------------------------------------
class RepoTypeLoader:
    """加载 ``config/repo-types.yaml`` 并提供切片维度查询。

    ``load(repo_type)`` 必须返回与历史 ``SLICES[repo_type]`` **逐字节一致**的
    ``List[Tuple[str, str, Sequence[str]]]``（filename, label, patterns），
    以保证下游 write_slices / write_repo_type / report_* 产出不变。
    """

    VERSION_BIND = 1  # 绑定 SKILL.md version: 0.1.0

    def __init__(self, path: str = None) -> None:
        self.path = Path(path) if path else self.default_path()
        self._data: dict = None

    @staticmethod
    def default_path() -> Path:
        return Path(__file__).resolve().parent.parent / "config" / "repo-types.yaml"

    def _ensure(self) -> None:
        if self._data is not None:
            return
        if not self.path.exists():
            raise SystemExit(
                f"repo-types.yaml 未找到: {self.path}；请确认 config/repo-types.yaml 已随 skill 提供"
            )
        try:
            text = self.path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SystemExit(f"repo-types.yaml 读取失败: {exc}") from exc
        self._data = _parse_yaml(text)
        self._validate(self._data)

    def _validate(self, data: dict) -> None:
        version = data.get("version")
        try:
            version_int = int(version)
        except (TypeError, ValueError):
            version_int = None
        if version_int != self.VERSION_BIND:
            raise SystemExit(
                f"repo-types.yaml version 与 skill 0.1.0 不一致，请同步升级 "
                f"(期望 {self.VERSION_BIND}，实际 {version})"
            )

    @staticmethod
    def _to_tuple(dim: dict) -> Tuple[str, str, List[str]]:
        return (dim["file"], dim["label"], list(dim.get("patterns", [])))

    def version(self) -> int:
        self._ensure()
        try:
            return int(self._data.get("version", 0))
        except (TypeError, ValueError):
            return 0

    def load(self, repo_type: str) -> List[Tuple[str, str, Sequence[str]]]:
        """返回指定 repo 类型的切片三元组列表；未知类型回退 fallback 并打 warning。"""
        self._ensure()
        types = self._data.get("repo_types", {})
        if repo_type in types:
            return [self._to_tuple(d) for d in types[repo_type].get("dimensions", [])]
        sys.stderr.write(
            f"[repo-types] 未知 repo 类型 {repo_type!r}，回退 fallback_dimensions\n"
        )
        return self.fallback()

    def load_all(self) -> Dict[str, List[Tuple[str, str, Sequence[str]]]]:
        self._ensure()
        return {
            name: [self._to_tuple(d) for d in info.get("dimensions", [])]
            for name, info in self._data.get("repo_types", {}).items()
        }

    def fallback(self) -> List[Tuple[str, str, Sequence[str]]]:
        self._ensure()
        return [self._to_tuple(d) for d in self._data.get("fallback_dimensions", [])]


if __name__ == "__main__":
    loader = RepoTypeLoader()
    print(f"version: {loader.version()}")
    for name in loader.load_all():
        dims = loader.load(name)
        print(f"{name}: {len(dims)} dimensions")
    print(f"fallback: {len(loader.fallback())} dimensions")
