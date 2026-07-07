# module_002 tests

- 文件数: 10
- 分层: core

## 角色
该模块由确定性扫描按路径分组生成，用于给后续 subagent 提供分析入口。

## 关键符号
- `_run` (tests/conftest.py:19)
- `build_cut_clip` (tests/conftest.py:25)
- `build_static_clip` (tests/conftest.py:55)
- `cut_clip` (tests/conftest.py:73)
- `static_clip` (tests/conftest.py:80)
- `test_default_detail_is_balanced` (tests/test_config.py:5)
- `test_env_overrides_detail` (tests/test_config.py:11)
- `test_invalid_detail_falls_back_to_default` (tests/test_config.py:17)
- `test_get_config_keys` (tests/test_config.py:23)

## MCP 工具/API 表面
- 未识别到 MCP 工具

## 覆盖率明细
| 文件组 | 文件数 | 已读方式 |
|---|---:|---|
| tests | 10 | deterministic scan |
