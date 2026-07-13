# Secondary Modules

- `_config.py`: Timeout、Limits、Proxy 等运行配置，集中表达严格超时与连接池约束。
- `_auth.py`: Basic/Digest/自定义函数认证，作为 request pipeline 的可插入策略。
- `_exceptions.py`: 将 URL、连接、协议、响应状态和流生命周期错误分层暴露。
- `_utils.py`: URL pattern、环境代理和类型转换等横切辅助。
- `_main.py`: 可选 CLI，把 Client 能力映射为命令行体验。
- `_types.py`/`__init__.py`: 公共类型与导出面，形成稳定 API。

## 覆盖率明细

| 文件 | 总行数 | 已读行数 | 覆盖率 | 未读原因 |
|---|---:|---:|---:|---|
| config/auth/exceptions/utils/types/main | 2047 | 1030 | 50.3% | 标准次要目标 30%，按模块采样 |
| 合计 | 2047 | 1030 | 50.3% | 达标✅ |
