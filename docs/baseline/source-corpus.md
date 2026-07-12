# 本地参考源码语料

## Purpose

将参考输出基线使用的 GitHub 项目固定到指定 commit，并保存到本机，供后续离线分析和结果复核。

## Storage

源码目录：`/Users/chuzu/projests/stark-repo-analyzer-reference-sources/`

源码目录位于当前项目之外，不纳入当前项目 Git。获取记录和校验结果应保存在本目录的 manifest 中。

## Acquisition Rule

每个项目使用默认分支的固定 commit 和浅克隆。获取完成后必须验证：

```bash
git -C <local-path> rev-parse HEAD
```

输出必须等于基线矩阵中记录的目标 commit。

## Reproducibility

本次获取记录见 [`source-corpus-manifest.json`](./source-corpus-manifest.json)。

获取命令模板：

```bash
git clone --depth 1 --branch <branch> https://github.com/<owner>/<repo>.git <local-path>
git -C <local-path> rev-parse HEAD
```

如果默认分支在获取期间发生变化，应使用目标 commit 重新获取或记录失败，不用未固定版本代替。
