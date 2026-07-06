# video-use 仓库分析方案 v2（基于 repomix + repo-analyzer 框架）

> 目标：用 repomix 做**原料采购** + 用 subagent 做**业务模块深度分析** + 多源融合产出**架构研究报告**。三层产物的最终交付是 `analysis/ANALYSIS_REPORT.md`。
>
> 参考：[yzddmr6/repo-analyzer](https://github.com/yzddmr6/repo-analyzer) 的 8 阶段分析框架；本方案在其基础上结合 repomix 的批量打包能力做了**原料层前置**。
>
> 分析模式：**核心 80% / 次要 20% 非对称门控**（核心模块 ≥80%、次要模块 ≥20%）。这是一种**自定义非对称模式**——比 repo-analyzer 的"标准"档（60/30）更深地探索核心模块，但次要模块只做轻量盘点（低于"标准"档的 30%），把节省下来的预算倾斜给核心。
>
> 外部调研：**可选层（默认 OFF）**，执行到阶段五后由用户决定是否开启。

---

## 0. 环境与目录约定

| 项 | 值 |
|----|----|
| 工作根目录 | `/mnt/d/projects/mynote/mac-projects/myIP` |
| 交付物目录 | `analysis/`（相对工作根目录） |
| 仓库克隆目录 | `/tmp` 下动态生成的临时目录（详见 §1） |
| 工具 | `repomix`（已 `npm install -g`）、`git`、`mktemp`、Claude Agent（subagent） |
| 全局 ignore 规则 | **全语言版**（Node/Python/Go/Rust/Java/Ruby/PHP/.NET/C-C++/媒体/IDE/密钥/日志），见 §2 完整定义；**锁文件 + AI Agent 配置不放全局 ignore**（维度 09/05 单独 include） |
| 输出格式 | 切片统一 `--style xml`；分析报告统一 Markdown |
| 分析模式 | **核心 80% / 次要 20%**（自定义非对称） |
| 外部调研 | 可选开关（默认 OFF） |

---

## 1. 阶段零：克隆 + 元数据采集

```bash
REPO_DIR=$(mktemp -d -t video-use-XXXXXX)
echo "克隆到: $REPO_DIR"
git clone --depth=1 https://github.com/browser-use/video-use "$REPO_DIR"
cd "$REPO_DIR"

# 采集元数据（写到 analysis/00-meta.txt）
{
  echo "## Git 元数据"
  git log -1 --pretty=full
  echo
  echo "## 贡献者 Top10"
  git shortlog -sn --all | head -10
  echo
  echo "## 代码量统计（按扩展名）"
  git ls-files | awk -F. '{print $NF}' | sort | uniq -c | sort -rn | head -20
} > /mnt/d/projects/mynote/mac-projects/myIP/analysis/00-meta.txt
```

> 避免写死路径：使用 `mktemp -d` 动态生成临时目录。

---

## 2. 阶段一：宏观认知建模（压缩 repomix）

**目的**：以最小 token 成本建立项目心智模型，作为切片决策的依据。

```bash
# 在 $REPO_DIR 内执行
#
# ===== 全局 ignore 详表（全语言版） =====
#   Node.js/TS/JS : node_modules, dist, build, out, .next, .nuxt, .svelte-kit, .cache,
#                   .parcel-cache, coverage, .nyc_output, *.tsbuildinfo
#   Python        : __pycache__, *.pyc|pyo|pyd, .venv, venv, env, *.egg-info,
#                   .pytest_cache, .mypy_cache, .ruff_cache, htmlcov, .tox
#   Go            : vendor
#   Rust          : target
#   Java/Kotlin   : target, build, *.class, *.jar, *.war, .gradle
#   Ruby          : vendor/bundle, .bundle, tmp, log
#   PHP           : vendor, storage/framework, bootstrap/cache
#   C#/.NET       : bin, obj, *.dll, *.exe, *.pdb
#   C/C++         : build, cmake-build-*, *.o, *.obj, *.so, *.dylib, *.a, CMakeFiles
#   媒体/二进制    : *.png, *.jpg, *.jpeg, *.gif, *.webp, *.bmp, *.ico, *.svg,
#                   *.mp4, *.webm, *.mov, *.mp3, *.wav,
#                   *.pdf, *.zip, *.tar, *.tar.gz, *.tgz, *.7z, *.rar,
#                   *.ttf, *.otf, *.woff, *.woff2, *.wasm
#   IDE/编辑器     : .idea, .vscode, *.swp, *.swo, Thumbs.db, .DS_Store
#   密钥/环境(高危): .env, .env.*, *.pem, *.key
#   日志/临时     : *.log, tmp, .tmp
#   已压缩产物    : *.min.js, *.min.css
#
#   ⚠️ 例外放行（不放全局 ignore，下游切片单独 include）：
#     - 锁文件  (*.lock / package-lock.json / yarn.lock / pnpm-lock.yaml /
#                Pipfile.lock / poetry.lock)                    → 维度 09
#     - AI Agent 配置 (.claude/** .codex/** .cursor/**
#                     CLAUDE.md AGENTS.md .cursorrules)          → 维度 05
# ====================================================================

IGNORE_GLOB="**/node_modules/**,**/dist/**,**/build/**,**/out/**,**/.next/**,**/.nuxt/**,**/.svelte-kit/**,**/.cache/**,**/.parcel-cache/**,**/coverage/**,**/.nyc_output/**,**/*.tsbuildinfo,**/__pycache__/**,**/*.pyc,**/*.pyo,**/*.pyd,**/.venv/**,**/venv/**,**/env/**,**/*.egg-info/**,**/.pytest_cache/**,**/.mypy_cache/**,**/.ruff_cache/**,**/htmlcov/**,**/.tox/**,**/vendor/**,**/target/**,**/*.class,**/*.jar,**/*.war,**/.gradle/**,**/vendor/bundle/**,**/.bundle/**,**/tmp/**,**/log/**,**/storage/framework/**,**/bootstrap/cache/**,**/bin/**,**/obj/**,**/*.dll,**/*.exe,**/*.pdb,**/cmake-build-debug/**,**/cmake-build-release/**,**/*.o,**/*.obj,**/*.so,**/*.dylib,**/*.a,**/CMakeFiles/**,**/*.png,**/*.jpg,**/*.jpeg,**/*.gif,**/*.webp,**/*.bmp,**/*.ico,**/*.svg,**/*.mp4,**/*.webm,**/*.mov,**/*.mp3,**/*.wav,**/*.pdf,**/*.zip,**/*.tar,**/*.tar.gz,**/*.tgz,**/*.7z,**/*.rar,**/*.ttf,**/*.otf,**/*.woff,**/*.woff2,**/*.wasm,**/.idea/**,**/.vscode/**,**/*.swp,**/*.swo,**/Thumbs.db,**/.DS_Store,**/.env,**/.env.*,**/*.pem,**/*.key,**/*.log,**/.tmp/**,**/*.min.js,**/*.min.css"

npx repomix --compress \
  --ignore "$IGNORE_GLOB" \
  -o /tmp/video-use-overview.xml
```

### 2.1 宏观认知建模的机制与原理

`--compress` 之所以能让"宏观认知建模"成立，关键在于它**不是简单的字符删减**，而是基于 **Tree-sitter AST 的结构化抽取**。

#### 2.1.1 机制：repomix `--compress` 内部做了什么

| 步骤 | 动作 | 保留什么 | 丢弃什么 |
|------|------|----------|----------|
| 1. 解析 | 用 Tree-sitter 把每份源码解析为 AST | 完整结构树 | 注释、空行、字符串字面量 |
| 2. 抽取 | 遍历 AST 提取声明（函数签名 / 类定义 / 接口 / 类型） | 类型签名、参数列表、返回值 | 函数体实现、变量赋值、循环体 |
| 3. 占位 | 用 `...implementation...` 占位符替换实现段 | 抽象边界（函数 / 方法 / 类的入口与出口） | 业务逻辑、控制流 |
| 4. 重组 | 按文件树结构重组，加入文件路径与行号 | 目录结构、模块边界、调用关系 | 字符串、字面量、日志、调试信息 |

> 关键事实：**不是调用 LLM 来"压缩"**，是纯本地的 AST 抽取 + 占位，所以压缩比稳定（通常 5-15×），不依赖外部 API、不消耗 token、不会因模型差异产生不一致。

#### 2.1.2 原理：为什么"宏观认知建模"能成立

压缩后的产物本质是"**代码的骨架**"——读者拿到的是：

- ✅ **接口契约**：每个类暴露什么方法、每个函数接受什么返回什么
- ✅ **依赖拓扑**：哪些文件 import 哪些、模块如何被组织
- ✅ **类型系统**：数据结构形状、继承链、接口实现
- ✅ **目录语义**：源码的物理组织映射到逻辑分层

但**被剥离**的是：

- ❌ 业务实现（具体怎么算的、状态怎么变的）
- ❌ 错误处理细节（catch 块、retry 逻辑、回退路径）
- ❌ 字符串与文案（配置项的值、用户提示语、日志格式）

这正好对应**宏观认知所需的"轮廓信息"**——就像看城市天际线 vs 看每一栋楼的户型图：天际线能告诉你"有几座 CBD、哪里是住宅区、哪里是工业区"，但户型图要等到具体要买房时才看。

#### 2.1.3 与 overview.md 14 项的对应关系

| 认知项 | 信息源 | 仅靠压缩包能否写 | 兜底方式 |
|--------|--------|------------------|----------|
| 1. 项目定位 | `package.json` / `pyproject.toml` / README 头部 | ✅ 完全可获取 | — |
| 2. 技术栈 | 依赖声明文件、`import` 列表 | ✅ 完全可获取 | — |
| 3. 架构分层 | 目录树 + 类 / 模块的命名空间 | ✅ 可推断 | 入口点交叉验证 |
| 4. 项目能力 | README + 入口函数签名 | ✅ 大部分可获取 | 维度 10 示例 |
| 5. 安装方式 | README + `Makefile` + `setup.py` | ✅ 完全可获取 | — |
| 6. 配置方式 | 环境变量引用 + 配置文件路径 | ⚠️ 路径可，值需查 | 维度 07 切片 |
| 7. 执行方式 | CLI 入口 / API 路由 / 库导出 | ✅ 完全可获取 | — |
| 8. 卸载方式 | README + `Makefile` 的 `uninstall` 目标 | ⚠️ 部分（可能未明示） | 维度 04 切片 |
| 9. 核心代码设计 | 抽象类 / 接口定义 + 关键调用图 | ✅ 抽象可获取，**实现需切片** | 维度 02 切片 |
| 10. 场景化问题 | 项目背景、用户故事 | ❌ 压缩包内不可获取 | §5 外部调研（可选） |
| 11. 设计哲学 | 命名 / 抽象 / 取舍的归纳 | ⚠️ 需 LLM 二次推理 | 阶段五 subagent |
| 12. 核心模块清单 | 业务功能划分 | ✅ 文件级可推断，**业务归类需切片** | 阶段五 |
| 13. 架构评价 | 深度分析 | ❌ 仅基于压缩包无法深入 | ANALYSIS_REPORT.md |
| 14. 切片索引 | 阶段二产物 | 阶段二完成后补 | — |

> **点睛句**：压缩包是"**骨架**"，12 维切片是"**血肉**"。先看骨架建认知、再按需查看血肉补细节——这就是"两阶段"方法论的根基。overview.md 的 14 项里，**前 9 项基本可由压缩包独立完成，第 10-13 项必须借助切片与（可选）外部调研，第 14 项是索引自身**。

#### 2.1.4 失效边界：什么场景下压缩机制不够用

| 场景 | 失效原因 | 兜底方案 |
|------|----------|----------|
| 项目主体是配置文件 / 数据文件 | AST 抽取后剩余信息极少 | 走维度 09 / 11 切片补足 |
| 大量使用宏 / 代码生成 | AST 抽取不到真实调用点 | 维度 02 切片对比压缩包 |
| 业务逻辑完全在 SQL / HTML 模板 | Tree-sitter 对这些 DSL 支持弱 | 维度 03 / 10 切片 |
| 项目核心是 build script / CI | 关注点不在源码 | 维度 07 切片 |
| 高度动态的反射 / 字符串执行 | AST 看不到运行时行为 | 必须读源码（阶段五 subagent） |
| 项目主要用 JS/TS 的 prototype / dynamic import | Tree-sitter 能解析但语义弱 | 维度 02 切片 |

> **设计含义**：阶段一（压缩 + overview 前 9 项）是**必要不充分**的——它给出"是什么、长什么样"，但**不回答"为什么这样设计、有没有更好的方案"**。这两类问题的答案来自阶段五 subagent 团队的深度分析。

### 2.2 并行子代理提取策略

14 项 overview 不应由单次 Claude turn 串行产出——既慢又会出现"上下文漂移"（前几项写得细、后几项敷衍）。改用**多 subagent 并行 + 主 agent 合并**的模式。

#### 2.2.1 分组策略（按"信息源"切，不是按"项号"切）

| Subagent | 负责项 | 主要输入 | 写入位置 |
|----------|--------|----------|----------|
| **A · 基础元数据** | 1, 2, 5, 6 | `package.json` / `pyproject.toml` / `README.md` 头部 / `requirements*.txt` | `overview.md` §1-4 |
| **B · 执行与生命周期** | 4, 7, 8 | CLI 入口点 / `Makefile` / `setup.py` / `install.sh` / `uninstall` 目标 | `overview.md` §5-7 |
| **C · 架构与设计** | 3, 9, 12 | 目录树 / 入口类 / 抽象接口 / 关键调用图 | `overview.md` §8-10 |
| **D · 哲学与评价** | 11, 13 | 跨切面：命名风格 / 抽象取舍 / 一致性归纳 | `overview.md` §11-12 |
| **E · 场景化引入** 【可选】 | 10 | 阶段三半外部调研产物 `03-research.md` | `overview.md` §0（TL;DR 之前） |

> **设计原则**：按"看什么文件"切分，而不是按"写哪几项"切分。每个 subagent 一次只需要熟悉 1-2 类文件，**主 agent 不再自己读全部压缩包**，只做合并与润色。

#### 2.2.2 Subagent Prompt 模板

```
你是一位资深架构师，正在为 {项目名} 撰写「宏观概览」的第 {N} 段。

## 输入材料
- 压缩包路径：/tmp/video-use-overview.xml
- 你的负责文件类型：{A: 依赖与元数据 / B: 执行与生命周期 / C: 架构与设计 / D: 哲学与评价}
- 你的输出段落：§{N}，覆盖 overview.md 的第 {item-list} 项

## 你的产出
用 Markdown 写 1-3 段话（200-500 字），覆盖：
- {item 1 的具体内容要求}
- {item 2 的具体内容要求}
- ...

## 风格
- 简洁、有观点、不堆砌
- 引用时用 文件路径:行号 格式
- 不要重复其他 subagent 会写的内容（如"项目定位"在 A 写过，你就不要重复）

## 写入
请直接追加到 /mnt/d/projects/mynote/mac-projects/myIP/analysis/overview.md
使用 ## 段落标题：§{N} {段落名}
```

#### 2.2.3 执行流程

```
                 ┌─ Subagent A (基础元数据)       ─→ overview.md §1-4  ─┐
                 ├─ Subagent B (执行与生命周期)   ─→        §5-7      ─┤
/tmp/video-use- ─┼─ Subagent C (架构与设计)       ─→        §8-10     ─┼─→ 主 agent
  overview.xml   ├─ Subagent D (哲学与评价)       ─→        §11-12    ─┤   合并 + §14
                 └─ Subagent E (场景化引入, 可选) ─→        §0        ─┘   切片索引回填
```

1. **同消息并行下发**：4（或 5）个 Agent 工具调用在同一 message 中发出
2. **每个 subagent 独立完成 §N 的写作**：直接 Write/Edit 到 `overview.md` 对应位置
3. **主 agent 合并**：
   - 检查 14 项是否全部覆盖（用 §0 的 checklist 自检）
   - 消除跨 subagent 重复（如"项目定位"被 A 和 D 都写了）
   - 补 §14（切片索引，等阶段二完成后回填）
4. **总耗时**：压缩 + 4 并行 subagent + 主合并 ≈ **2-3 分钟**（vs 串行 5-8 分钟）

#### 2.2.4 冲突与去重规则

| 冲突类型 | 例子 | 处理方式 |
|----------|------|----------|
| 同一事实被多 subagent 写到 | "Python 3.10+" 出现在 A 和 B | 主 agent 合并时只保留第一次出现的位置，删后续 |
| 评价性内容相互矛盾 | A 说"测试充分"、D 说"测试薄弱" | 主 agent 标注【冲突待定】，阶段五裁决 |
| 引用同一文件不同行 | A 引用 `setup.py:12`、B 引用 `setup.py:45` | 保留信息量更大的引用，删冗余 |
| 段落顺序错乱 | C 写到 §8 后又追加到 §10 | 主 agent 按 §1-14 顺序重排 |
| 风格不一致 | A 用 bullet、B 用 paragraph | 主 agent 统一为同一种（默认 paragraph） |

#### 2.2.5 何时回退到串行

| 场景 | 原因 | 替代方案 |
|------|------|----------|
| 压缩包 < 5KB | 信息量太小，无需拆分 | 单 Claude turn 直接写完 |
| 项目极简（< 20 个源文件） | 14 项用单次 turn 即可完成 | 单 turn 写完 |
| 用户明确要求"先逐项串行 review" | 阶段性人工介入 | 串行模式 |

> **取舍**：并行快 4× 但失去"边写边交叉验证"的机会。**适合本任务**（宏观建模不要求 100% 准确、要的是"先有粗模型"）；**不适合**需要严谨性的场景（如合规审查、安全审计）。

随后基于 `/tmp/video-use-overview.xml` 撰写 `analysis/overview.md`，覆盖：

| # | 必含项 | 备注 |
|---|--------|------|
| 1 | 项目定位（库/框架/应用/工具） | 一句话 |
| 2 | 技术栈（语言/框架/关键依赖） | 列表化 |
| 3 | 架构分层（入口层/业务层/基础设施层） | 用文字或简易图 |
| 4 | 项目能力（核心 feature 清单） | ≤10 条 |
| 5 | 安装方式 | 命令行步骤 |
| 6 | 配置方式（环境变量、配置文件） | 表格化 |
| 7 | 执行方式（CLI、API、库调用） | 表格化 |
| 8 | 卸载方式（清理脚本、依赖回收） | 命令行步骤 |
| 9 | 核心代码设计（关键抽象、模块边界、数据流） | 重点章节 |
| 10 | **场景化问题引入**（项目解决什么问题、谁在用、为什么需要这个项目） | v2 新增 |
| 11 | **设计哲学**（贯穿项目的设计风格） | v2 新增 |
| 12 | **核心模块清单**（按业务功能划分，1-2 句话/模块） | v2 新增 |
| 13 | **架构评价与改进建议**（架构级/设计级/工程级三层次） | v2 新增 |
| 14 | **12 维切片目录**（指向 `analysis/slices/`） | 索引 |

> 第 10-13 项源自 repo-analyzer 的"分析哲学"——避免 overview 沦为"代码说明书"。

---

## 3. 阶段二：12 维精细切片（不压缩 + XML，**并行执行**）

### 3.0 共享资源

阶段二与阶段一**共享** `IGNORE_GLOB` 全局 ignore 变量。`IGNORE_GLOB` 的完整定义见 §2；为避免复制 70+ 项 glob，在执行阶段一时**先落盘**为 `analysis/.ignore-glob.sh`：

```bash
# 由 §2 阶段一执行完 bash 后追加
cat > /mnt/d/projects/mynote/mac-projects/myIP/analysis/.ignore-glob.sh <<'EOF'
IGNORE_GLOB="**/node_modules/**,**/dist/**,**/build/**,..."   # 与 §2 完全一致
export IGNORE_GLOB
EOF
```

阶段二的所有命令通过 `source` 复用：

```bash
# 在 $REPO_DIR 内执行
source /mnt/d/projects/mynote/mac-projects/myIP/analysis/.ignore-glob.sh

# 统一命令格式
npx repomix --style xml \
  --include "<GLOB>" \
  --ignore "$IGNORE_GLOB" \
  -o "<REPO_DIR>/slices/<编号>-<slug>.xml"
```

> 12 个 Bash 调用以 `run_in_background: true` 并行下发。

### 3.1 切片清单

| # | 维度 | include glob | 价值 | 文件名 |
|---|------|--------------|------|--------|
| 01 | 前端代码 | `**/*.tsx,**/*.jsx,**/*.vue,**/*.svelte,**/*.css,**/*.scss,**/*.html` | 视觉/交互层 | `01-frontend.xml` |
| 02 | 后端代码 | `**/*.py,**/*.go,**/*.rs,**/*.java,**/*.ts,**/*.js` | 业务逻辑层 | `02-backend.xml` |
| 03 | 数据库设计 | `**/migrations/**,**/migrate/**,**/schema/**,**/*.sql,**/prisma/**,**/*.prisma,**/models/**` | 数据模型与迁移 | `03-database.xml` |
| 04 | 文档 | `**/*.md,**/*.mdx,**/*.rst,**/docs/**,**/README*` | 背景与决策 | `04-docs.xml` |
| 05 | AI Agent 配置 | `.claude/**`,`.codex/**`,`.agents/**`,`.cursor/**`,`AGENTS.md`,`CLAUDE.md`,`.cursorrules` | 工具协作契约 | `05-agent-config.xml` |
| 06 | 测试 | `**/test/**,**/tests/**,**/*test.*,**/*.spec.*,**/__tests__/**,**/fixtures/**,**/__snapshots__/**` | 行为规约与证据 | `06-tests.xml` |
| 07 | 配置与脚本 | `**/Dockerfile*`,`**/docker-compose*`,`Makefile`,`**/*.sh`,`.github/**`,`scripts/**`,`ci/**` | 构建/部署链路 | `07-config-scripts.xml` |
| 08 | 类型与接口契约 | `**/*.d.ts`,`**/*.proto`,`**/openapi*`,`**/swagger*`,`**/schema.json`,`**/schema.yaml` | 对外交互规约 | `08-interfaces.xml` |
| 09 | 第三方依赖清单 | `package.json`,`pyproject.toml`,`requirements*.txt`,`Pipfile`,`go.mod`,`Cargo.toml`,`Gemfile`,`composer.json` | 风险面与版本基线 | `09-dependencies.xml` |
| 10 | 示例与 demo | `**/examples/**`,`**/samples/**`,`**/demo/**`,`notebooks/**` | 真实使用模式 | `10-examples.xml` |
| 11 | 资源文件 | `**/i18n/**`,`**/locales/**`,`**/assets/**`,`**/public/**`,`**/templates/**`,`**/prompts/**` | 内容资产盘点 | `11-assets.xml` |
| 12 | 变更历史热点 | `git log` 聚合后写 manifest（不走 repomix） | 演进趋势 | `12-history-hotspot.txt` |

> **关键修正（与 §2 一致）**：
> - **维度 09 / 12 的例外放行规则**详见 §2 阶段一末尾"例外放行"段（锁文件 → 维度 09；不走 repomix → 维度 12）
> - 维度 02 与 01、维度 09 与 02 等存在 glob 重叠，最终 include 以 `repomix` 的去重行为为准

### 3.2 维度 12 的 git log 聚合脚本

```bash
{
  echo "# video-use 变更历史热点"
  echo
  echo "## 累计修改次数 Top50"
  git log --name-only --pretty=format: | grep -v '^$' | sort | uniq -c | sort -rn | head -50
  echo
  echo "## 最近 30 天提交"
  git log --since="30 days ago" --pretty=format:"%h | %ad | %s" --date=short
  echo
  echo "## 提交活跃度（按作者）"
  git shortlog -sn --since="6 months ago"
} > "$REPO_DIR/slices/12-history-hotspot.txt"
```

### 3.3 并行调度

- 12 条 `npx repomix` + 1 条 `git log` 聚合脚本 → 13 个 Bash 调用，全部 `run_in_background: true`
- 等待所有 slice 完成后，统一 `cp` 到 `analysis/slices/`

```bash
mkdir -p /mnt/d/projects/mynote/mac-projects/myIP/analysis/slices
cp "$REPO_DIR"/slices/*.xml "$REPO_DIR"/slices/*.txt \
   /mnt/d/projects/mynote/mac-projects/myIP/analysis/slices/
```

---

## 4. 阶段三：项目特征识别 + 自适应提问 【核心流程】

**目的**：根据阶段 0-2 的产出，识别项目类型、核心场景、用户关注点，再决定阶段四的报告结构。

### 4.1 识别项

| 维度 | 识别方法 | 输出 |
|------|----------|------|
| 项目类型 | 读 README + 入口文件 | 库/框架/应用/工具 |
| 核心场景 | 读 examples + CLI 入口 | 1-3 个具体场景 |
| 技术栈 | 读 package.json / pyproject.toml | 主语言、关键依赖 |
| 架构风格 | 读目录结构 | 单体/分层/插件化/微内核 |
| 演进健康度 | 阶段二 12 维 + 维度 12 | 提交频率、贡献者集中度 |

### 4.2 自适应提问（AskUserQuestion）

- 每轮 ≤3 个问题，多轮直到问题收敛
- 问题来源：识别项中无法自动判断的部分
- 触发时机：阶段三末，**作为阶段四的输入**

> **Q1（外部调研开关）** 就在此轮或下一轮抛出：
> - 是否启用 `analysis/03-research.md` 外部调研？
> - 选项：① 跳过 ② 启用（含 3-5 次 WebSearch + 官网遍历 + 自带文档研读，~10-15 分钟）
>
> 此开关与 §12 开关表"外部调研（§5）"项保持一致，**默认 OFF**。若用户启用，§2.2 中 E subagent（场景化引入）也自动启用，二者联动。

---

## 5. 阶段三·半：外部调研（可选层，默认 OFF）

> **触发条件**：用户在 §4.2 阶段选择"启用"。

```bash
# 调研产物
analysis/03-research.md
```

**调研内容**（参考 repo-analyzer 阶段三）：

| 调研项 | 方法 | 产出 |
|--------|------|------|
| 项目解决的核心问题 | WebSearch + 官网 | 1-3 个具体场景 |
| 3-5 个竞品 | WebSearch "X alternatives 2026" | 对比表 |
| 为什么需要单独做这个项目 | 官方公告 + 创始人博客 | 1 段叙述 |
| 组织动机 | GitHub Insights + 贡献者地理分布 | 1 段叙述 |
| 自带架构文档 | 读 docs/、CONTRIBUTING.md、AGENTS.md、ADR | 关键设计决策清单 |

> **不启用时**：阶段三半整层跳过，业务模块分析直接基于本地代码与文档进行。

---

## 6. 阶段四：动态报告结构设计

**目的**：基于阶段三-三半的输出，确定业务模块清单、叙事线、模块依赖图。

### 6.1 业务模块识别（按业务功能，不按文件）

1. **业务功能角度** — 项目提供哪些核心业务能力？
2. **数据流角度** — 数据从输入到输出经过哪些转换阶段？
3. **职责角度** — 业务需求变化时，哪些代码需要一起改？

### 6.2 叙事主线选择

| 叙事线 | 适用场景 | 本项目是否适合 |
|--------|----------|----------------|
| 数据流驱动 | Web 框架、API 网关、请求驱动系统 | 待识别 |
| 分层驱动 | 操作系统、编译器、严格分层架构 | 待识别 |
| 问题驱动 | 领域复杂的业务系统 | 待识别 |

> 选定的叙事线决定 06-模块-*.md 草稿的排列顺序与过渡句。

### 6.3 模块依赖图

绘制 Mermaid 关系图（写入 `analysis/05-modules-plan.md`），描述：
- 模块间的调用方向
- 共享状态
- 关键抽象边界

---

## 7. 阶段五：业务模块并行深度分析（subagent 团队）

> 这是 repo-analyzer 框架的**核心阶段**——把 12 维切片"原料"转译为"有观点的业务模块分析"。

> **设计原则一致性**：本阶段的 subagent 调度遵循 §2.2"按信息源切分 + 同消息并行 + 主 agent 合并"的范式（详见 §2.2.1 / §2.2.3）；冲突处理规则见 §2.2.4。与阶段一 overview 的 4+1 subagent 共享同一调度范式，但**输入材料不同**——阶段一读压缩包，本阶段读 12 维切片 XML。

### 7.1 调度策略

| 类型 | 处理方式 | Agent 数量 |
|------|----------|-----------|
| 核心模块 | 每个 → 独立 general-purpose subagent | N 个（按业务模块数） |
| 次要模块 | 合并 → 1 个 subagent 批量处理 | 1 个 |
| 全部 subagent | 同一消息中并行启动 | 一次下发 |

### 7.2 核心模块 Subagent Prompt 模板

```
你是一位资深架构师，正在对 {项目名} 的「{模块名}」模块进行深度分析。

## 背景信息
- 项目定位: {一句话}
- 整体架构: {简述}
- 项目设计哲学: {贯穿项目的核心理念}
- 该模块在系统中的位置: {与其他模块的关系}
- 叙事上下文: {前一个模块讲了什么 / 读者带着什么问题进入 / 本模块为下一个模块铺垫什么}

## 需要分析的文件
{文件路径列表 —— 从 analysis/slices/ 中读取}

## 分析结构（4 要素必含）
1. 在项目中的角色 — 为什么存在？去掉它系统会怎样？
2. 解决什么问题 — 业务背景
3. 设计思路 — 方案及理由、放弃的替代方案、核心设计模式
4. 核心数据结构 — 关键接口/类型定义（只贴理解设计必需的）
5. 核心业务流程 — Mermaid 流程图 + 自然语言解读，标注源文件路径和行号
6. 与其他模块的设计协同 — 依赖谁、谁依赖它、共享状态
7. 关键设计决策 — 1-3 个最重要决策及权衡
8. Deep Research 洞察 — 替代方案代价、业界对比
9. 亮点与问题（按层次：架构级 / 设计级 / 工程级）

## 全局视角
将模块放在项目整体语境中——设计选择如何服务整体哲学、边界为何这样划、变化会如何影响其他模块。

## 写入策略
写入 analysis/drafts/06-module-{模块名}.md。
- 大模块（>5000 行）增量写入：完成一个子系统立即 Write/Edit
- 单次写入不超过 300 行
- 草稿末尾附覆盖率明细表（文件名 | 总行数 | 已读行数 | 覆盖率% | 未读原因）

## 覆盖率要求
分析模式: 核心 80% / 次要 20%（非对称）
- 核心模块: ≥80% 覆盖率
- 未达标时必须继续阅读直到达标
```

### 7.3 次要模块批量 Subagent Prompt 模板

```
你是一位资深架构师，对 {项目名} 的次要模块进行批量分析。

## 背景信息
- 项目定位 / 整体架构 / 设计哲学

## 需要分析的次要模块
{模块列表：名称、职责假设、文件范围}

## 每个模块输出（5 项）
1. 职责（一句话）
2. 在项目整体中的角色（一句话）
3. 实现方式（一句话）
4. 特别之处（如有）
5. 涉及文件列表

写入 analysis/drafts/06-module-secondary.md
草稿末尾附覆盖率明细表（次要模块 ≥20% 覆盖率）。
```

### 7.4 Subagent 协作规范

- 只分析分配的文件，不越界
- 跨模块推断用【待主 agent 验证】标注
- 深度优先于广度
- 草稿开头用 1-2 句说明本模块与前一个模块的关系
- 草稿结尾用 1 句铺垫下一个模块

---

## 8. 阶段六：交叉验证 + 覆盖率门控

### 8.1 覆盖率门控

| 模块类型 | 最低覆盖率 | 未达标动作 |
|----------|-----------|-----------|
| 核心模块 | **80%** | 继续读 + 重写该模块草稿 |
| 次要模块 | **20%** | 继续读 + 补全 |

### 8.2 交叉验证清单

- [ ] 跨模块结论【待主 agent 验证】已全部在源码中确认
- [ ] 关键事实 spot-check：随机抽 5 个核心数据，回归源码
- [ ] 协作关系一致：模块 A 引用模块 B 的描述，双方一致
- [ ] 覆盖率明细表全部 ✅

### 8.3 产出

`analysis/08-coverage.md`：覆盖率汇总 + 验证日志。

---

## 9. 阶段七：多源融合 → 最终报告

**目的**：将原料层（12 维 repomix 切片）+ 业务模块层（subagent 草稿）+（可选）外部调研融合为单一 `ANALYSIS_REPORT.md`。

### 9.1 报告骨架

```markdown
# {项目名} 架构分析报告

> 元信息：仓库地址、分析时间、工具栈、分析模式、外部调研状态

## 0. TL;DR
- 项目定位 / 核心能力 / 主要发现（3-5 条）

## 1. 场景化问题引入
- 项目解决什么问题 / 谁在用 / 为什么需要这个项目
- 调研发现（仅当 §5 启用时）

## 2. 架构全景
- Mermaid 全景图（模块依赖图）
- 分层说明
- 设计哲学（贯穿项目的设计风格）

## 3. 核心模块详解
- 按叙事线顺序展开（数据流 / 分层 / 问题驱动）
- 每个模块四要素：数据结构 / 执行流程 / 设计决策 / 模块间依赖
- Mermaid 流程图 + 文件路径行号

## 4. 第三方依赖与版本基线
- 关键依赖（来自 09 切片）
- 风险面评估

## 5. 工程成熟度
- 测试策略（来自 06 切片）
- 可观测性、错误处理、文档完整性

## 6. 架构评价
- 亮点（架构级 / 设计级 / 实现级）
- 问题（按影响面 / 演进风险排序）
- 改进建议

## 7. 与业界对比
- 3-5 个竞品对比（仅当 §5 启用时）

## 8. 复现方法
- 链接到 PLAN.md

## 附录 A：12 维切片索引
## 附录 B：覆盖率明细
## 附录 C：参考资料
```

### 9.2 交付物总览

```
analysis/
├── 00-meta.txt                  # 阶段 0 元数据
├── PLAN.md                      # 本文件
├── .ignore-glob.sh              # 阶段 1 共享 ignore 变量（§2 创建，§2 + §3 复用）
├── overview.md                  # 阶段 1 宏观认知（4+1 subagent 并行写作，见 §2.2）
├── 03-research.md               # 【可选】阶段三半外部调研
├── 05-modules-plan.md           # 阶段 4 模块清单 + 叙事线 + 依赖图
├── 08-coverage.md               # 阶段 6 覆盖率门控
├── ANALYSIS_REPORT.md           # 阶段 7 最终报告
├── README.md                    # 索引页
├── drafts/                      # 阶段 5 业务模块草稿
│   ├── 06-module-{core-1}.md
│   ├── 06-module-{core-2}.md
│   ├── ...
│   └── 06-module-secondary.md
└── slices/                      # 阶段 2 12 维原料
    ├── 01-frontend.xml
    ├── 02-backend.xml
    ├── 03-database.xml
    ├── 04-docs.xml
    ├── 05-agent-config.xml
    ├── 06-tests.xml
    ├── 07-config-scripts.xml
    ├── 08-interfaces.xml
    ├── 09-dependencies.xml
    ├── 10-examples.xml
    ├── 11-assets.xml
    └── 12-history-hotspot.txt
```

---

## 10. 验收标准（核心 80% / 次要 20% 模式）

- [ ] 仓库成功克隆至 `/tmp/video-use-XXXXXX`，未污染工作区
- [ ] `analysis/00-meta.txt` 含元数据
- [ ] `analysis/overview.md` 覆盖 14 项内容（含 v2 新增 4 项）
- [ ] `analysis/slices/01-12-*.{xml,txt}` 全部存在
- [ ] `analysis/05-modules-plan.md` 选定叙事线 + 模块依赖图
- [ ] `analysis/drafts/06-module-*.md` 全部核心模块四要素完整
- [ ] **核心模块 ≥80% 覆盖率，次要模块 ≥20%**（写入 `08-coverage.md`）
- [ ] `analysis/ANALYSIS_REPORT.md` 含 Mermaid 全景图 + 架构评价 + 改进建议
- [ ] `analysis/README.md` 索引页可点击跳转至各产物
- [ ] `analysis/PLAN.md` 保留（作为复现手册）

---

## 11. 完整执行顺序

| # | 阶段 | 动作 | 产物 |
|---|------|------|------|
| 0 | 阶段零 | `mktemp -d` + `git clone` + 元数据采集 | `00-meta.txt` |
| 1 | 阶段一 | `npx repomix --compress` → **4+1 subagent 并行（§2.2）→ 主 agent 合并** → `overview.md` | `overview.md` |
| 2 | 阶段二 | 13 个切片并行（12 repomix + 1 git log） | `slices/*` |
| 3 | 阶段三 | 特征识别 + AskUserQuestion（含外部调研开关） | 用户决策 |
| 4 | 阶段三半 | 【可选】WebSearch + 调研 | `03-research.md` |
| 5 | 阶段四 | 模块识别 + 叙事线 + 依赖图 | `05-modules-plan.md` |
| 6 | 阶段五 | N+1 个 subagent 并行分析 | `drafts/06-*.md` |
| 7 | 阶段六 | 交叉验证 + 80%/20% 覆盖率门控 | `08-coverage.md` |
| 8 | 阶段七 | 多源融合 → 最终报告 | `ANALYSIS_REPORT.md` |
| 9 | 收尾 | 索引页 | `README.md` |

---

## 12. 开关与默认值

| 开关 | 默认 | 触发时机 | 备注 |
|------|------|----------|------|
| 外部调研（§5） | **OFF** | 阶段三末，AskUserQuestion | 启用后约 10-15 分钟额外开销；与阶段一 E subagent 联动 |
| 分析模式 | **核心 80% / 次要 20%** | 已在 §0 锁定 | 不可中途切换（避免覆盖度统计错位） |
| 维度 12 走 git log | **ON** | 阶段二 | 替代 repomix pack |
| 维度 09/12 例外放行（§2） | **ON** | 阶段二 | 锁文件 + AI Agent 配置，详见 §2 例外段 |
| 阶段一压缩（--compress） | **ON** | 阶段一 | 阶段二全部不压缩 |
| 并行调度（run_in_background） | **ON** | 阶段二、阶段五 | 减少 wall-clock |
| **阶段一 overview 4+1 subagent 并行（§2.2）** | **ON** | 阶段一末 | 4 并行 + 1 可选 E；与下方"E 启用"联动 |
| **阶段一 E subagent（场景化引入）** | **OFF** | 阶段一末 | 依赖外部调研（§5）开关；同时 ON 才生效 |
| **阶段五 subagent 并行调度（§7.1）** | **ON** | 阶段五 | N 个核心模块 + 1 个次要批量 |
| **共享 IGNORE_GLOB 落盘（.ignore-glob.sh）** | **ON** | 阶段一末创建，阶段二复用 | 避免在 §2 和 §3 各复制 70+ 项 glob |

---

## 13. 反馈记录（供未来复用）

- 用户对"分析项目"任务的偏好：先 clone 到 /tmp（动态目录），先宏观（压缩）再切片（不压缩 + XML），并行执行。
- 用户对分析深度的偏好：**核心 80% / 次要 20% 非对称模式**——核心模块重投入，次要模块轻量盘点；不属于 repo-analyzer 预设三档，是自定义组合。
- 用户对非对称取舍的偏好：把"标准 30% 次要模块预算"释放出来转投给核心（80% > 标准 60%），反映出**重视核心逻辑深度、不在次要工具上耗时**的偏好。
- 用户对外部资源的偏好：WebSearch 等外部调研为可选项，默认关闭、按需开启——避免不必要的时间开销。
- 用户在收到"先出方案再执行"工作流时的反应：直接采纳 → 在确认 Q1/Q2 后立即升级方案。
- 用户在阶段 1 三轮迭代中的偏好：**先补全 ignore（13 大类全语言）→ 再补机制解释（让人理解为什么可行）→ 再补并行 subagent 调度（提效 4×）**。反映出**重视体系自洽**的工作流——每加一个能力，都要求解释它与既有体系的契合点。
- 用户对"避免重复"的偏好：拒绝在多章节里重复同一规则（如锁文件例外、§7 与 §2.2 的范式一致性），倾向于用"详见 §X"交叉引用代替复制粘贴。
