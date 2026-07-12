import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";

/** Graphify relations that act as reference/call/import edges for units.refs. */
const REFERENCE_RELATIONS = new Set([
  "calls",
  "method",
  "imports",
  "imports_from",
  "references",
  "re_exports",
  "extends",
  "inherits",
  "implements",
  "indirect_call",
]);

const STRUCTURAL_RELATIONS = new Set(["contains"]);

/**
 * Normalize a Graphify node label to a bare symbol name.
 * Examples: "getAppConfig()" -> "getAppConfig", "AppConfig" -> "AppConfig"
 */
export function normalizeGraphifySymbol(label) {
  if (!label) return "";
  let name = String(label).trim();
  // drop trailing call sig / generics-ish suffixes
  name = name.replace(/\(.*\)$/, "");
  name = name.replace(/<.*>$/, "");
  name = name.replace(/^#/, "");
  return name.trim();
}

function parseLocationLine(sourceLocation) {
  if (sourceLocation == null) return 1;
  const text = String(sourceLocation);
  const match = text.match(/L?(\d+)/i);
  return match ? Number(match[1]) : 1;
}

function normalizeRepoRel(path) {
  return String(path || "").split("\\").join("/").replace(/^\.\//, "");
}

/**
 * Load graphify-out/graph.json (if present) into an inbound-ref index keyed by
 * definition symbol + optional definition file.
 *
 * complete refs require EXTRACTED confidence (AST-backed). INFERRED stays partial.
 */
export function loadGraphifyRefIndex(repoPath, options = {}) {
  const root = resolve(repoPath);
  const candidates = [
    options.graphPath,
    join(root, "graphify-out", "graph.json"),
    join(root, "graph.json"),
  ].filter(Boolean);

  let graphPath = null;
  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      graphPath = candidate;
      break;
    }
  }
  if (!graphPath) {
    return {
      ok: false,
      path: null,
      nodes: 0,
      links: 0,
      extracted_ref_links: 0,
      by_symbol: new Map(),
      reasons: ["未找到 graphify-out/graph.json（可先在目标仓运行 graphify update .）"],
    };
  }

  let data;
  try {
    data = JSON.parse(readFileSync(graphPath, "utf8"));
  } catch (error) {
    return {
      ok: false,
      path: graphPath,
      nodes: 0,
      links: 0,
      extracted_ref_links: 0,
      by_symbol: new Map(),
      reasons: [`无法解析 graph.json: ${error.message}`],
    };
  }

  const nodes = Array.isArray(data.nodes) ? data.nodes : [];
  const links = Array.isArray(data.links) ? data.links : [];
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  /** @type {Map<string, Array<object>>} */
  const bySymbol = new Map();
  let extractedRefLinks = 0;

  for (const link of links) {
    const relation = String(link.relation || "").toLowerCase();
    if (!relation || STRUCTURAL_RELATIONS.has(relation)) continue;
    if (!REFERENCE_RELATIONS.has(relation) && relation !== "uses") continue;

    const confidence = String(link.confidence || "EXTRACTED").toUpperCase();
    const sourceNode = nodeById.get(link.source);
    const targetNode = nodeById.get(link.target);
    if (!sourceNode || !targetNode) continue;

    // For units, "refs" are inbound uses of a definition symbol.
    // link source = call/import site; link target = referenced symbol (common Graphify shape for calls/imports).
    // Also accept reverse when target is the call site (defensive).
    const siteNode = sourceNode;
    const defNode = targetNode;
    const defSymbol = normalizeGraphifySymbol(defNode.label);
    if (!defSymbol) continue;

    const siteFile = normalizeRepoRel(link.source_file || siteNode.source_file);
    const siteLine = parseLocationLine(link.source_location || siteNode.source_location);
    const defFile = normalizeRepoRel(defNode.source_file);
    const defLine = parseLocationLine(defNode.source_location);

    if (!siteFile || (siteFile === defFile && siteLine === defLine)) continue;

    const isExact = confidence === "EXTRACTED";
    if (isExact) extractedRefLinks += 1;

    const ref = {
      file: siteFile,
      line: siteLine,
      dir: "inbound",
      source: "graphify",
      confidence: isExact ? "exact" : "heuristic",
      relation,
      def_file: defFile || null,
      def_line: defLine || null,
    };

    const bucket = bySymbol.get(defSymbol) ?? [];
    bucket.push(ref);
    bySymbol.set(defSymbol, bucket);
  }

  return {
    ok: extractedRefLinks > 0 || bySymbol.size > 0,
    path: graphPath,
    nodes: nodes.length,
    links: links.length,
    extracted_ref_links: extractedRefLinks,
    by_symbol: bySymbol,
    reasons:
      extractedRefLinks > 0
        ? []
        : ["graph.json 存在但没有 EXTRACTED 级 reference/call/import 边可写入 units.refs"],
  };
}

/**
 * Cheap usability probe for doctor: graph has EXTRACTED reference-like edges.
 */
export function probeGraphifyUnitsRefs(repoPath, options = {}) {
  const index = loadGraphifyRefIndex(repoPath, options);
  return {
    usable: index.ok && index.extracted_ref_links > 0,
    graph_path: index.path,
    nodes: index.nodes,
    links: index.links,
    extracted_ref_links: index.extracted_ref_links,
    symbol_keys: index.by_symbol.size,
    reasons: index.reasons,
  };
}

/**
 * Look up inbound refs for a definition symbol; prefer same-file def when possible.
 */
export function graphifyRefsForSymbol(index, symbol, definitionFile, definitionLine) {
  if (!index?.by_symbol?.size || !symbol) return [];
  const raw = index.by_symbol.get(symbol) ?? index.by_symbol.get(normalizeGraphifySymbol(symbol)) ?? [];
  if (raw.length === 0) return [];

  const defFile = normalizeRepoRel(definitionFile);
  const defLine = Number(definitionLine) || 0;

  // Prefer refs whose graph def_file matches unit file when available.
  // ctags 与 graphify 对同一符号的定义文件/行可能不一致（类型 re-export、声明合并等），
  // 若严格同文件过滤后为空，回退到同名符号的全部 inbound 边，避免把 EXTRACTED 边误降为仅 rg partial。
  const matched = raw.filter((ref) => {
    if (!ref.def_file) return true;
    if (ref.def_file !== defFile) return false;
    if (defLine > 0 && ref.def_line > 0 && Math.abs(ref.def_line - defLine) > 80) {
      return false;
    }
    return true;
  });
  const chosen = matched.length > 0 ? matched : raw;

  const dedupe = new Map();
  for (const ref of chosen) {
    if (ref.file === defFile && ref.line === defLine) continue;
    const key = `${ref.file}:${ref.line}:${ref.dir}:${ref.source}`;
    const prev = dedupe.get(key);
    if (!prev || (prev.confidence !== "exact" && ref.confidence === "exact")) {
      dedupe.set(key, {
        file: ref.file,
        line: ref.line,
        dir: ref.dir,
        source: "graphify",
        confidence: ref.confidence,
      });
    }
  }
  return [...dedupe.values()].sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line);
}

export function mergeRefs(...lists) {
  const dedupe = new Map();
  for (const list of lists) {
    for (const ref of list || []) {
      const key = `${ref.file}:${ref.line}:${ref.dir || "inbound"}`;
      const prev = dedupe.get(key);
      // exact > heuristic; prefer graphify/ctags over rg/grep when confidence ties
      if (!prev) {
        dedupe.set(key, ref);
        continue;
      }
      const prevScore = (prev.confidence === "exact" ? 2 : 0) + (prev.source === "graphify" || prev.source === "ctags" ? 1 : 0);
      const nextScore = (ref.confidence === "exact" ? 2 : 0) + (ref.source === "graphify" || ref.source === "ctags" ? 1 : 0);
      if (nextScore > prevScore) dedupe.set(key, ref);
    }
  }
  return [...dedupe.values()].sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line);
}

export function refsStatusFor(exactRefs, heuristicRefs) {
  if ((exactRefs || []).length > 0) return "complete";
  if ((heuristicRefs || []).length > 0) return "partial";
  return "missing";
}
