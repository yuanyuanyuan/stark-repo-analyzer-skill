# 阶段 3/4：规模评估与分析计划

## 分析对象

- 远程仓库：`https://github.com/yuanyuanyuan/Long_screenshot_splitting_tool`
- 本地源码：`/tmp/Long_screenshot_splitting_tool`
- 分析模式：标准分析
- 输出目录：`/Users/chuzu/projests/stark-repo-analyzer-skill/测试证据/v1.2`

## 规模统计

使用命令：

```bash
find /tmp/Long_screenshot_splitting_tool -path '*/node_modules' -prune -o -path '*/dist' -prune -o -path '*/.git' -prune -o -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.css' -o -name '*.md' \) -print | xargs wc -l | tail -1
```

结果：约 `62,354` 行。该数字包含文档、脚本、样式和测试证据，不作为质量门，只用于估算项目规模。

## 分析策略

v1.2 继续采用 Evidence Anchor First：不追求行覆盖率，而是围绕核心业务问题读取必要源码，并要求每个关键判断带 `文件:行号` 锚点。

核心问题：

- 长截图如何从 File 进入后台处理流水线？
- Worker 与算法层如何分离，为什么能避免主线程卡顿？
- 内容感知切割失败时如何安全回退？
- 状态层如何处理异步切片、资源释放和导出选择？
- 路由守卫如何避免刷新、错页、处理未完成时白屏？
- 导出系统如何保证页序和空选择防御？
- SEO/shared-components 等外围系统是否过度工程？

## 模式选择说明

目标仓库规模不大，但噪音模块多。标准分析足够覆盖核心模块；深度分析会被 SEO、shared-components、部署脚本分散注意力，不符合「重点深入，次要简略」原则。
