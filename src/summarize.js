import { writeFileSync } from "node:fs";
import { join } from "node:path";

import { readJson } from "./common.js";

function list(items, render) {
  return items.length > 0 ? items.map((item) => `- ${render(item)}`).join("\n") : "- 未发现候选";
}

export function summarize({ out }) {
  const map = readJson(join(out, "repo-map.json"));
  const markdown = `# Repo Map 候选摘要

> 来源：\`repo-map.json\`。以下均为确定性扫描得到的候选信号，不是架构结论。

## 语言与规模候选

${list(map.languages, (item) => `${item.language}: ${item.files} 个源码文件，约 ${item.lines} 行（来源：扩展名与文本行计数）`)}

## 模块候选

${list(map.module_candidates, (item) => `\`${item.name}\`: ${item.source_files} 个源码文件，约 ${item.lines} 行（来源：${item.signal}）`)}

## 候选入口

${list(map.entry_candidates, (item) => `\`${item.file}\`（信号：${item.signal}；来源：${item.source}）`)}

## Manifest 与依赖候选

${list(map.manifests, (item) => `\`${item}\``)}
${list(map.dependencies, (item) => `\`${item.name}\` ${item.version ?? ""}（${item.scope}；来源：\`${item.manifest}\`）`)}

## 核心文档候选

${list(map.document_candidates, (item) => `\`${item.file}\`（来源：${item.source}）`)}

## 排除范围候选

- 测试候选：${map.exclusions.test.length} 个文件
- Generated 候选：${map.exclusions.generated.length} 个文件
- Vendor 候选：${map.exclusions.vendor.length} 个文件

## 风险区域候选

${list(map.risk_candidates, (item) => `\`${item.file}\`（信号：${item.signal}；来源：${item.source}）`)}

## 待验证问题

- 哪些候选入口真正承接主要运行路径？
- 哪些模块候选应分级为 core、secondary 或 excluded，依据是什么？
- Manifest 依赖对应哪些运行时边界与设计权衡？
- 风险区域候选中哪些实际影响错误处理、配置、安全、并发或扩展机制？
- 测试、generated 与 vendor 候选是否需要调整排除范围？
`;
  writeFileSync(join(out, "repo-map.md"), markdown);
  return markdown;
}
