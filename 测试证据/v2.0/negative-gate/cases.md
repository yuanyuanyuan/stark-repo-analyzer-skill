# v2.0 负向用例记录

## 已由自动化覆盖

来源：`npm test`

覆盖用例：

- doctor 缺少符号枚举器时阻塞。
- graphify 缺失记录为 fail，但不阻塞。
- scan 在 doctor 未放行时拒绝执行。
- units 在 doctor 后枚举器失效时阻塞，不退回正则分母。
- gate 不把缺少实质判断的 analyzed 单元计入分子。
- gate 不把非法锚点计入分子。
- gate 要求 core 未覆盖单元记录 `skip_reason`。
- gate 要求未解析 core 文件进入 Unsupported Area。
- gate 拒绝缺少 Why、源码锚点和 Mermaid 的空洞报告。
- standard gate 要求每个 core 模块至少一个有效 semantic review。
- quick gate 要求全局 2-3 条 semantic review。
- deep gate 要求每个 core 模块抽查全部不足 3 条的 analyzed unit。
- gate 拒绝缺失、未知、非 analyzed、重复的 semantic review。
- gate 拒绝过期 anchor、过期 judgment、空 observation 和非 supported verdict。

## 本次真实环境覆盖

用例：真实目标仓库缺少符号枚举器。

命令：

```bash
node bin/repo-analyzer.js doctor --repo /tmp/Long_screenshot_splitting_tool --out 测试证据/v2.0/standard
```

结果：

- 退出码：2
- `allowed:false`
- `symbol-enumerator: fail`
- `language-support: fail`

用例：doctor 未放行时 scan 拒绝继续。

命令：

```bash
node bin/repo-analyzer.js scan --repo /tmp/Long_screenshot_splitting_tool --out 测试证据/v2.0/standard
```

结果：

```text
Doctor 未放行：修复 doctor-report.json 中的必需检查后重跑 doctor。
```

## 决策

不继续手工构造真实目标仓库的 gate 负向产物。

原因：

- gate 前置产物需要 `scan/summarize/units`，而这些步骤被 doctor 正确阻塞。
- 人工伪造真实目标仓库的 gate 输入会降低证据可信度。
- gate 负向语义已经由自动化 fixture 覆盖，且本次 `npm test` 全部通过。
