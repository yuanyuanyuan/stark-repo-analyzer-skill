import { execFileSync } from "node:child_process";
import { chmodSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

export function createFixture() {
  const root = mkdtempSync(join(tmpdir(), "repo-analyzer-v2-"));
  const repo = join(root, "repo");
  const out = join(root, "artifacts");
  const bin = join(root, "bin");
  mkdirSync(join(repo, "src"), { recursive: true });
  mkdirSync(join(repo, "test"), { recursive: true });
  mkdirSync(join(repo, "docs"), { recursive: true });
  mkdirSync(join(repo, "generated"), { recursive: true });
  mkdirSync(join(repo, "vendor"), { recursive: true });
  mkdirSync(out, { recursive: true });
  mkdirSync(bin, { recursive: true });

  writeFileSync(join(repo, "package.json"), `${JSON.stringify({ name: "fixture", dependencies: { hono: "^4.0.0" } }, null, 2)}\n`);
  writeFileSync(join(repo, "README.md"), "# Fixture\n");
  writeFileSync(join(repo, "docs", "architecture.md"), "# Architecture\n");
  writeFileSync(join(repo, "src", "index.js"), "export function main() { return serve(); }\n");
  writeFileSync(join(repo, "src", "service.js"), "export function serve() { return 'ok'; }\n");
  writeFileSync(join(repo, "test", "service.test.js"), "// test candidate\n");
  writeFileSync(join(repo, "generated", "client.js"), "// generated candidate\n");
  writeFileSync(join(repo, "vendor", "lib.js"), "// vendor candidate\n");

  execFileSync("git", ["init", "-q"], { cwd: repo });
  execFileSync("git", ["add", "."], { cwd: repo });
  execFileSync("git", ["-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "fixture"], { cwd: repo });

  const ctags = join(bin, "ctags");
  writeFileSync(
    ctags,
    `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('Universal Ctags 6.1.0'); process.exit(0); }
if (args.includes('--list-languages')) { console.log('JavaScript\\nTypeScript'); process.exit(0); }
const file = args.at(-1);
if (file?.endsWith('src/index.js')) {
  console.log(JSON.stringify({_type:'tag',name:'main',path:file,line:1,kind:'function'}));
  console.log(JSON.stringify({_type:'tag',name:'serve',path:file,line:1,kind:'function',roles:'reference'}));
}
if (file?.endsWith('src/service.js')) console.log(JSON.stringify({_type:'tag',name:'serve',path:file,line:1,kind:'function'}));
if (file?.endsWith('src/legacy.js')) console.log(JSON.stringify({_type:'tag',name:'legacy',path:file,line:8001,kind:'variable'}));
`,
  );
  chmodSync(ctags, 0o755);

  const astGrep = join(bin, "ast-grep");
  writeFileSync(
    astGrep,
    `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('ast-grep 0.40.0'); process.exit(0); }
const file = args.at(-1);
const pattern = args[args.indexOf('--pattern') + 1] ?? '';
if (pattern.startsWith('function') && file?.endsWith('src/index.js')) console.log(JSON.stringify({metaVariables:{single:{NAME:{text:'main'}}},range:{start:{line:0}}}));
if (pattern.startsWith('function') && file?.endsWith('src/service.js')) console.log(JSON.stringify({metaVariables:{single:{NAME:{text:'serve'}}},range:{start:{line:0}}}));
`,
  );
  chmodSync(astGrep, 0o755);

  const graphify = join(bin, "graphify");
  writeFileSync(
    graphify,
    `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('graphify 0.1.0-fixture'); process.exit(0); }
console.log(JSON.stringify({ ok: true, query: args.join(' ') }));
`,
  );
  chmodSync(graphify, 0o755);

  return { root, repo, out, ctags, astGrep, graphify };
}

/** standard-only: baseline tools; enhanced missing */
export function standardOnlyEnv(fixture) {
  return {
    REPO_ANALYZER_CTAGS: "/missing/ctags",
    REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
    REPO_ANALYZER_GRAPHIFY: "/missing/graphify",
  };
}

/** enhanced present but deep still needs graph capabilities; ctags alone is not deep-complete */
export function ctagsOnlyEnv(fixture) {
  return {
    REPO_ANALYZER_CTAGS: fixture.ctags,
    REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
    REPO_ANALYZER_GRAPHIFY: "/missing/graphify",
  };
}

/** Graphify-qualified deep environment (fixture mock) */
export function deepGraphifyEnv(fixture) {
  return {
    REPO_ANALYZER_CTAGS: fixture.ctags,
    REPO_ANALYZER_AST_GREP: "/missing/ast-grep",
    REPO_ANALYZER_GRAPHIFY: fixture.graphify,
    REPO_ANALYZER_GRAPHIFY_CAPABILITIES: "graph-queries,symbol-enumeration,reference-edges",
  };
}

export function cli(command, { repo, out, env = {}, options = {}, flags = [] }) {
  const entry = new URL("../bin/repo-analyzer.js", import.meta.url);
  const optionArgs = Object.entries(options).flatMap(([key, value]) => [`--${key}`, String(value)]);
  try {
    const stdout = execFileSync(process.execPath, [entry.pathname, command, "--repo", repo, "--out", out, ...optionArgs, ...flags], {
      encoding: "utf8",
      env: { ...process.env, ...env },
      stdio: ["ignore", "pipe", "pipe"],
    });
    return { status: 0, stdout, stderr: "" };
  } catch (error) {
    return {
      status: error.status,
      stdout: error.stdout?.toString() ?? "",
      stderr: error.stderr?.toString() ?? "",
    };
  }
}
