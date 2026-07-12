# 次要模块：CLI 打包与 JavaScript 工作区元数据

## 范围与定位

本节只覆盖 JavaScript/npm 的分发与维护外层：根工作区清单、`codex-cli`
元包、其 Node 启动器及三个脚本。根 README 将 Codex CLI 描述为本地运行的
coding agent，并列出安装入口（`README.md:1,14-40`）；这里的代码负责把已构建
的本地可执行文件交付给用户和维护者。它**不定义**代理的模型调用、工具选择、
权限决策或 Rust 运行时行为。【待主 agent 验证】

```mermaid
flowchart LR
  W[根 pnpm 工作区] --> M[@openai/codex 元包]
  M --> L[bin/codex.js Node 启动器]
  M -. optionalDependencies .-> P[同名、平台后缀的 npm 包]
  P --> V[vendor/<target>/bin/codex]
  L --> V
  B[build_npm_package.py] --> M
  B --> P
  C[run_in_container.sh] --> L
```

## 关注点 1：工作区工具链与依赖治理

**责任。** 根 `package.json` 把仓库声明为私有的维护工具项目，提供 JSON/Markdown/
JavaScript 格式检查与 hooks schema 生成命令（`package.json:2-11`）。它固定
Node `>=22`、pnpm `>=10.33.0` 及带校验信息的 pnpm 版本（`package.json:34-38`），
并通过 `resolutions`/`overrides` 集中约束传递依赖版本（`package.json:13-32`）。

**系统角色与做法。** `pnpm-workspace.yaml` 仅登记三个 JS 发布面：CLI、responses
proxy npm 包、TypeScript SDK（`pnpm-workspace.yaml:1-4`），因此这是跨包一致性和
发布准备的开发维护层，而不是 Rust runtime 的宿主。工作区要求构建依赖严格受控：
禁止自动信任构建、严格构建依赖、禁止信任策略降级，并把新包最小发布年龄设为
10080 分钟（7 天）（`pnpm-workspace.yaml:6-17`）。

**约束。** 根工具链要求 Node 22，但可发布 CLI 元包只要求 Node 16（
`codex-cli/package.json:9-12`）；维护环境与最终启动器兼容范围有意不同。`esbuild`
被列为忽略的 built dependency（`pnpm-workspace.yaml:6-7`），不能据此推断运行时
缺少或使用该依赖。【待主 agent 验证】

## 关注点 2：轻量元包与多平台原生载荷

**责任。** `@openai/codex` 是 ESM npm 元包，暴露唯一的 `codex` bin，发布内容只
包含 Node 启动器（`codex-cli/package.json:2-15`）。打包脚本将六个目标映射为
Linux musl、macOS 和 Windows 的 x64/arm64 组合及相应 npm 别名
（`codex-cli/scripts/build_npm_package.py:21-66`）。

**系统角色与做法。** 发布时脚本复制启动器和 README，给元包写入六个
`optionalDependencies`；每个依赖用 npm alias 指向相同包名但带平台后缀版本
（`build_npm_package.py:229-303`）。平台包只携带 `vendor`，并以 `os`/`cpu` 约束
安装目标（`build_npm_package.py:243-271`）。后缀版本以 `<release>-<platform>`
生成，规避 npm 禁止同名同版本重发的规则（`build_npm_package.py:321-324`）。

**约束。** 原生包必须提供 `--vendor-src`，脚本会复制目标目录并在目标缺失时失败
（`build_npm_package.py:155-173,353-408`）；这将 native artifact 的取得与 npm
组装分离。脚本 README 指定常规发布应走根目录 `stage_npm_packages.py`，由它下载
artifact、填充 `vendor/` 并输出 `dist/npm/`，直接调用仅用于调试
（`codex-cli/scripts/README.md:3-23`）。后者的实现不在本模块阅读范围，故其
artifact 来源、签名和发布编排【待主 agent 验证】。

## 关注点 3：跨平台启动、安装修复提示与进程语义

**责任。** `bin/codex.js` 依照 `process.platform`/`arch` 选择六个 target triple，
不支持的组合立即报错（`codex-cli/bin/codex.js:16-77`）。它先解析平台 optional
dependency 的 `package.json`，不可解析时才回退到元包的 `vendor/`；随后检查实际
二进制的存在性（`codex-cli/bin/codex.js:79-108`）。

**系统角色与做法。** 这是 Node 到原生 `codex` 可执行文件的兼容性适配器。缺少
payload 时，它依据 pnpm/bun/npm 安装痕迹给出相应的全局重装命令
（`codex-cli/bin/codex.js:98-107,118-177`）。启动时写入规范包根和单一
`CODEX_MANAGED_BY_{NPM|PNPM|BUN}` 环境标记，先清除其他两个标记
（`codex-cli/bin/codex.js:179-198`）；这些标记的下游消费语义【待主 agent 验证】。

**约束。** 采用异步 `spawn` 且继承 stdio，转发 `SIGINT`/`SIGTERM`/`SIGHUP`；
子进程退出后 Node 重发同一信号或镜像退出码（`codex-cli/bin/codex.js:112-116,
195-249`）。这保证 shell/自动化能观察原生程序的终止结果，却不改变原生程序
如何处理参数或信号。【待主 agent 验证】

## 关注点 4：可复现暂存、SDK 联动与 tarball 隔离

**责任。** `build_npm_package.py` 要求显式版本，若同时给 `--version` 和
`--release-version` 则必须相同，并拒绝非空的指定暂存目录
（`build_npm_package.py:91-150,217-226`）。它支持 CLI 元包、六个平台包、responses
proxy 和 SDK（`build_npm_package.py:68-89`）。

**系统角色与做法。** 除 CLI 外，该脚本也作为相邻 npm 产品的统一暂存器：proxy
复制其 launcher/README，SDK 使用冻结 lockfile 安装并构建 `dist`，移除发布包的
`prepare`，然后让 SDK 依赖本次版本的 `@openai/codex`
（`build_npm_package.py:272-314,327-350`）。可选 `--pack-output` 在临时目录及独立
npm cache/log 目录中执行 `npm pack --json`，解析并移动确定的 tarball
（`build_npm_package.py:410-447`）。

**约束。** 暂存目录若为临时目录会被保留以便检查（`build_npm_package.py:209-212`）；
这有利于发布排障但会留下临时产物。脚本输出建议的 `--version`/`--help` 或 payload
目录检查，并不实际执行这些验证（`build_npm_package.py:175-208`）。SDK 的构建行为
及 proxy 的运行时不属于本节的 agent 行为结论。【待主 agent 验证】

## 关注点 5：面向容器的受限网络启动辅助

**责任。** `run_in_container.sh` 启动名为工作目录派生的 Docker 容器，映射工作目录、
传入 `OPENAI_API_KEY`，以 `NET_ADMIN`/`NET_RAW` 初始化 firewall，最后在容器中以
`workspace-write` 与 `on-request` 参数运行 `codex`（
`codex-cli/scripts/run_in_container.sh:11-15,26-36,59-66,79-95`）。

**系统角色与做法。** 调用者可用空格分隔的 `OPENAI_ALLOWED_DOMAINS` 覆盖默认
`api.openai.com`；脚本通过正则验证域名、写入 root 持有且只读的配置文件，然后
删除初始化脚本（`run_in_container.sh:13-14,68-86`）。`init_firewall.sh` 读取该文件
（缺失时回退默认值），清空规则，允许 DNS/loopback/宿主子网，解析允许域名为 IPv4
ipset，默认 DROP，仅允许 established 与命中 ipset 的出站通信
（`init_firewall.sh:5-23,25-44,46-89`）。最后检查 `example.com` 不通而
`api.openai.com` 可达（`init_firewall.sh:91-115`）。

**约束。** 该辅助程序需要 Docker、root 容器权限、iptables/ipset/dig/curl，以及
可解析 IPv4 A 记录；无 IPv6 处理，DNS 变更也不会在启动后自动刷新
（`init_firewall.sh:46-62`）。工作目录被挂载到容器中的 `/app$WORK_DIR`，并非
只读挂载（`run_in_container.sh:59-65`）；容器安全边界和原生 runtime 的实际
sandbox 执行细节【待主 agent 验证】。命令参数虽逐项 `%q` 转义，接口仍接收任意
调用者提供的命令（`run_in_container.sh:88-95`）。

## 文件覆盖记录

| 文件名 | 总行数 | 已读行数 | 覆盖率% | 未读原因 |
|---|---:|---:|---:|---|
| `package.json` | 39 | 39 | 100 | - |
| `pnpm-workspace.yaml` | 17 | 17 | 100 | - |
| `codex-cli/package.json` | 22 | 22 | 100 | - |
| `codex-cli/bin/codex.js` | 249 | 249 | 100 | - |
| `codex-cli/scripts/build_npm_package.py` | 453 | 453 | 100 | - |
| `codex-cli/scripts/run_in_container.sh` | 95 | 95 | 100 | - |
| `codex-cli/scripts/init_firewall.sh` | 115 | 115 | 100 | - |
| `codex-cli/scripts/README.md` | 23 | 23 | 100 | - |
| `README.md`（安装关联） | 71 | 71 | 100 | - |
| **合计（声明范围）** | **1084** | **1084** | **100** | **达标✅** |
