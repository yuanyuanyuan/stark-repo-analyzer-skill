# 本地开源工具配置

本文给出研究方案的可复现实例。命令用于设计验证，不代表已经接入 analyzer skill，也不改变 V1 的 Graphify deep 命令或 UAT 契约。

## 1. 版本锁定

| 工具 | 建议锁定 | 许可证 | 备注 |
|---|---:|---|---|
| Graphify | `0.9.13` | MIT | 必须具备 `--code-only` 与 `--out` 修复 |
| Tree-sitter core | `0.26.11` | MIT | Graphify 当前依赖需以其自身 pin 为准 |
| py-tree-sitter | `0.26.0` | MIT | 仅自定义 query adapter 使用 |
| Repomix | `1.16.1` | MIT | Node.js 22+；本机调研时为 Node 24.18.0 |
| Serena | `1.5.3` | MIT | 只允许 LSP backend |
| ast-grep | `0.44.1` | MIT | 结构查询可选层 |
| Joern | `4.0.579` | Apache-2.0 | deep-dataflow only |
| Universal Ctags | 固定发行版/commit | GPL-2.0 | 广语言 symbol fallback |

生产化前不能只锁顶层版本。还要保存安装来源、源码 commit、依赖 lock、许可证快照和 SBOM。

## 2. 隔离工作目录

```bash
TARGET=/absolute/path/to/repository
WORK_DIR=/absolute/path/to/analysis-work

mkdir -p \
  "$WORK_DIR/.cache" \
  "$WORK_DIR/.uv-cache" \
  "$WORK_DIR/.uv-tools" \
  "$WORK_DIR/.uv-bin" \
  "$WORK_DIR/graphify-out" \
  "$WORK_DIR/context"

export XDG_CACHE_HOME="$WORK_DIR/.cache"
export UV_CACHE_DIR="$WORK_DIR/.uv-cache"
export UV_TOOL_DIR="$WORK_DIR/.uv-tools"
export UV_TOOL_BIN_DIR="$WORK_DIR/.uv-bin"
export GRAPHIFY_OUT="$WORK_DIR/graphify-out"
```

这些目录不能位于目标仓库内部。运行前后都应记录目标仓库 `git status --porcelain=v1 -z` 和文件系统快照，以检测工具越界写入。

## 3. Git SourceUniverse

建立 target-relative、NUL 安全的 source list：

```bash
git -C "$TARGET" ls-files -z --cached --others --exclude-standard \
  > "$WORK_DIR/source-files.zlist"
```

控制器随后逐项 `stat`、hash 并分类。不要直接用换行分割原始 Git 输出。面向只接受 newline list 的工具时，必须先拒绝包含换行的路径，或通过结构化控制器安全转换。

最小身份信息：

```bash
git -C "$TARGET" rev-parse HEAD
git -C "$TARGET" status --porcelain=v1 -z --untracked-files=all
git -C "$TARGET" submodule status --recursive
```

`git ls-files` 不负责验证 LFS、sparse checkout、缺失 tracked 文件和 submodule 内容，控制器必须另行分类。

## 4. Graphify code-only

### 初次建立静态图

```bash
uvx --from graphifyy==0.9.13 graphify extract "$TARGET" \
  --code-only \
  --out "$WORK_DIR" \
  --no-cluster \
  --timing

uvx --from graphifyy==0.9.13 graphify cluster-only "$WORK_DIR" \
  --no-label \
  --no-viz \
  --timing
```

配置意图：

- `--code-only`：不处理文档、论文和图片，不触发 LLM semantic extraction；
- `--out` + absolute `GRAPHIFY_OUT`：缓存和产物留在 work dir；
- `--no-cluster` 后单独 `cluster-only`：分别记录 AST 与聚类耗时；
- `--no-label`：不调用 LLM 为社区命名；
- `--no-viz`：不生成不需要的可视化文件。

不能在 V2 默认命令里加入 `--mode deep`、backend、model 或 API key。`--mode deep` 属于 Graphify 的语义增强路径，不是 code AST 深度开关。

### 增量更新

Graphify `update` 没有与 `extract` 对称的 `--out`，因此必须使用绝对 `GRAPHIFY_OUT`：

```bash
GRAPHIFY_OUT="$WORK_DIR/graphify-out" \
  uvx --from graphifyy==0.9.13 graphify update "$TARGET" --no-cluster

GRAPHIFY_OUT="$WORK_DIR/graphify-out" \
  uvx --from graphifyy==0.9.13 graphify cluster-only "$WORK_DIR" \
    --no-label --no-viz --timing
```

更新后必须重新执行：source identity 检查、删除/重命名驱逐检查、Graphify corpus reconciliation 和 source-location validation。不能因为 `update` 退出 0 就默认缓存新鲜。

### Ignore 与 corpus reconciliation

Graphify 会读取 `.gitignore` 和 `.graphifyignore`，并支持负向 `--exclude`。它没有已确认稳定的正向 file-list 提取接口。因此：

- Git manifest 定义期望源码全集；
- `.graphifyignore` 只添加 V2 明确排除项；
- 不依赖 `.graphifyinclude` 作为 allowlist；
- 提取后比较 graph source files 与 manifest；
- graph 中出现 manifest 外路径时立即阻断。

## 5. Repomix hotspot pack

配置样例位于 [repomix-hotspot.config.example.json](repomix-hotspot.config.example.json)。控制器必须生成一个非空的 target-relative 文件清单：

```bash
test -s "$WORK_DIR/hotspot-files.txt" || {
  echo "empty hotspot file list" >&2
  exit 64
}
```

Repomix `1.16.1` 的 `--stdin` 与目录参数互斥。应在目标仓库根目录运行，以 target-relative 路径作为 stdin，同时用绝对 `--output` 把产物写到 work dir：

```bash
cd "$TARGET"
npx --yes repomix@1.16.1 \
  --config /absolute/path/to/repomix-hotspot.config.example.json \
  --output "$WORK_DIR/context/repomix-hotspot.xml" \
  --stdin \
  < "$WORK_DIR/hotspot-files.txt"
```

约束：

- stdin 为空时不得调用 Repomix；
- `--stdin` 模式不传 repository directory 参数；
- 文件清单由 `HotspotRanker` 产生，不让 Repomix 重新决定 corpus；
- `--output` 必须是 target 外的绝对路径；
- security check 保持开启；
- 不启用 `input.processors`，因为它允许执行任意命令；
- 不信任 remote repository config，不使用 `--remote-trust-config`；
- token budget 非零退出视为 `CONTEXT_OVER_BUDGET`；
- pack 只用于方向性上下文，最终引用由 Agent 直接读取源码。

需要让少数 seed 文件保持全文时，控制器应生成一次性 runtime config，在 `output.patterns` 最前面加入精确 glob：

```json
{
  "pattern": "src/core.py",
  "compress": false
}
```

不能把任意绝对路径直接插入 glob。先验证它属于 manifest，再转换为 target-relative POSIX path。

## 6. Serena OSS-LSP precision adapter

Serena 默认提供免费的 language-server backend，同时另有付费 JetBrains backend。本方案只允许前者。

Codex MCP 配置示例：

```toml
[mcp_servers.serena]
command = "uvx"
args = [
  "--from",
  "git+https://github.com/oraios/serena@v1.5.3",
  "serena",
  "start-mcp-server",
  "--project-from-cwd",
  "--context=codex"
]
```

使用要求：

- 从目标仓库根目录启动，或使用 Serena 支持的显式 `--project <path>` 形式；
- 初始化时保持默认 LSP backend，不传 `-b JetBrains`；
- 项目配置和运行 metadata 必须记录 backend=`LSP`；
- 每种 language server 单独进入 OSS allowlist；
- 不允许“freely available”但许可证不明确的 server 自动下载后成为必选依赖；
- 只开放读取型 symbol 工具给分析流程，不需要 rename/edit/debug 能力；
- 保存 query、结果路径/range、耗时、server/version 和失败原因。

首批可审计 allowlist 候选：

| 语言 | Language server | 许可证 |
|---|---|---|
| Rust | rust-analyzer | Apache-2.0 / MIT（按发行物核验） |
| Go | gopls (`golang.org/x/tools`) | BSD-3-Clause |
| Java | Eclipse JDT LS | EPL-2.0 |

Pyright、TypeScript language server、clangd 等必须在接入前对具体发行物和传递依赖做直接 LICENSE 审核，不能只依赖 GitHub API 的概括字段。

## 7. Universal Ctags fallback

在目标仓库根目录使用 controller 生成的文件清单：

```bash
cd "$TARGET"
ctags \
  --output-format=json \
  --fields=+nK \
  --extras=+q \
  --file-scope=yes \
  -L "$WORK_DIR/hotspot-files.txt" \
  -f "$WORK_DIR/precision/ctags.jsonl"
```

Ctags 只补定义、kind 和 scope，不提供可靠 references、call graph 或 dataflow。GPL-2.0 工具以独立进程使用；若未来随产品分发二进制或修改版，需要单独完成许可证义务评审。

## 8. ast-grep structural queries

单次结构查询示例：

```bash
ast-grep run \
  --lang python \
  --pattern '@$DECORATOR\ndef $FUNC($$$ARGS): $$$BODY' \
  --json=stream \
  "$TARGET" \
  > "$WORK_DIR/precision/ast-grep.jsonl"
```

生产使用应把 rule、language、tool version、query digest 和命中 source range 一起保存。ast-grep 适合回答“哪些函数使用某种 decorator/registration 结构”，不承担跨文件 name resolution。

## 9. Joern deep-dataflow

只在显式 deep mode 的隔离目录运行：

```bash
mkdir -p "$WORK_DIR/deep/joern"
cd "$WORK_DIR/deep/joern"

joern-parse "$TARGET"
joern-export --repr pdg --out "$WORK_DIR/deep/pdg"
```

需要 dataflow overlay 时，在 Joern 查询脚本中显式执行 `run.ossdataflow`，并保存脚本、CPG/tool version、语言 frontend、耗时和结果。不要把整个大仓库的 Joern index 作为 standard 前置步骤。

## 10. 禁止配置

以下配置不能出现在接受方案中：

- Graphify 默认 code path 中的 LLM backend、API key、`--mode deep`；
- Serena `-b JetBrains` 或任何需要付费插件的 capability；
- CodeQL CLI/database；
- Semgrep 商业 cross-file/Pro engine；
- Sourcegraph Cloud 或其他闭源 SaaS；
- Repomix processors、`--remote-trust-config`、关闭 security check；
- 未固定版本、未核验许可证的 SCIP indexer 或 language server。

## 11. 每次运行必须记录

```text
target path and source identity
tool names, versions, install source and license snapshot
exact commands and sanitized environment
start/end/elapsed time and exit code
input manifest/config/query digests
output paths and checksums
node/edge/file/token counts
network/provider activity (expected: none on default structure path)
source-tree cleanliness before/after
failure classification and retry count
```
