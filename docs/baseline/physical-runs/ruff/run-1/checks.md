# Verification checks

| 检查 | 命令/方法 | 状态 | 说明 |
|---|---|---|---|
| 固定源 HEAD | `git -C <source> rev-parse HEAD` | PASS | `c588a3f7f57461692652d339936222b4496c5953` |
| 源树起始和最终状态 | `git -C <source> status --porcelain` | PASS | 两次均为空输出 |
| 必读参考文件 | `wc -l` + `sed` 全文 | PASS | `SKILL.md` 274 行、analysis guide 166 行、module guide 150 行 |
| 模块覆盖表 | `tail` + `rg` | PASS | 三份核心草稿都有达标表 |
| 抽样跨模块证据 | `sed` 阅读 CLI/lint/formatter 关键段 | PASS | 见 `drafts/07-cross-validation.md` |
| 外部调研 | 未执行 | NOT PERFORMED | physical baseline 未调用网络工具 |
| Git 历史 | 未执行 | NOT PERFORMED | 用户禁止 |
| 构建/测试/Clippy | `cargo --version; rustc --version; cargo nextest --version` | NOT PERFORMED | exit 127；且文档测试命令可修改 snapshot |
| 输出 Markdown 语法/链接 | 未运行专用 linter | NOT PERFORMED | 环境无 cargo；未安装独立 Markdown checker |
| 交付完整性 | `test -f/-s` 检查 12 个交付文件 | PASS | 文件存在且非空 |
| 未完成占位符 | `rg 'TODO|TBD|[待填写]|[TODO]'` | PASS | 无匹配 |
