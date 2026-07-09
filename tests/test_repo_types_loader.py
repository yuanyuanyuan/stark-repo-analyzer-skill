"""T16: RepoTypeLoader 单元测试（对应 T01/T02）。

覆盖：
- 受限 YAML 子集解析（标量 / 映射 / block 列表 / 行内流列表）
- load(repo_type) 返回与历史 SLICES 逐字节一致的切片三元组
- load_all / fallback / version / VERSION_BIND 绑定
- 未知类型回退 fallback
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from repo_types_loader import RepoTypeLoader, _parse_yaml, _split_flow  # noqa: E402


# 历史内嵌 SLICES（T02 删除前的黄金值），用于逐字节一致性断言。
EXPECTED_SLICES = {
    "web-fullstack": [
        ("01-frontend.xml", "前端代码", ["*.tsx", "*.jsx", "*.vue", "*.svelte", "*.css", "*.scss", "*.html"]),
        ("02-backend.xml", "后端代码", ["*.py", "*.go", "*.rs", "*.java", "*.ts", "*.js"]),
        ("03-database.xml", "数据库设计", ["*.sql", "*.prisma", "migrations/*", "schema/*"]),
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Dockerfile*", "docker-compose*", "Makefile", "*.sh", ".github/*", "scripts/*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pyproject.toml", "requirements*.txt", "go.mod", "Cargo.toml"]),
    ],
    "single-lang-CLI": [
        ("02-backend.xml", "代码", ["*.py", "*.go", "*.rs", "*.java", "*.ts", "*.js"]),
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Dockerfile*", "Makefile", "*.sh", "scripts/*", ".github/*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pyproject.toml", "requirements*.txt", "go.mod", "Cargo.toml"]),
        ("10-examples.xml", "示例与 demo", ["examples/*", "samples/*", "demo/*", "notebooks/*"]),
    ],
    "single-lang-lib": [
        ("02-backend.xml", "库代码", ["*.py", "*.go", "*.rs", "*.java", "*.ts", "*.js"]),
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pyproject.toml", "requirements*.txt", "go.mod", "Cargo.toml"]),
        ("10-examples.xml", "示例与 demo", ["examples/*", "samples/*", "demo/*"]),
    ],
    "multi-agent-config": [
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("05-agent-config.xml", "AI Agent 配置", [".claude/*", ".codex/*", ".cursor/*", ".agents/*", "AGENTS.md", "CLAUDE.md"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Dockerfile*", "Makefile", "*.sh", "scripts/*", ".github/*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pyproject.toml", "requirements*.txt", "go.mod", "Cargo.toml"]),
    ],
    "monorepo": [
        ("02-backend.xml", "包代码", ["*.py", "*.go", "*.rs", "*.java", "*.ts", "*.js"]),
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Dockerfile*", "Makefile", "*.sh", "scripts/*", ".github/*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pnpm-workspace.yaml", "pyproject.toml", "go.mod", "Cargo.toml"]),
    ],
    "embedded-kernel": [
        ("02-backend.xml", "系统代码", ["*.c", "*.h", "*.cc", "*.cpp", "*.rs"]),
        ("04-docs.xml", "文档", ["*.md", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Makefile", "*.sh", "CMakeLists.txt"]),
        ("09-dependencies.xml", "第三方依赖清单", ["Cargo.toml", "go.mod", "requirements*.txt"]),
    ],
}


class RepoTypeLoaderTest(unittest.TestCase):
    def setUp(self):
        self.loader = RepoTypeLoader()

    def test_default_path_points_to_config(self):
        self.assertEqual(self.loader.default_path().name, "repo-types.yaml")
        self.assertTrue(self.loader.default_path().exists())

    def test_version_binding(self):
        self.assertEqual(self.loader.VERSION_BIND, 1)
        self.assertEqual(self.loader.version(), 1)

    def test_load_returns_byte_identical_slices(self):
        for repo_type, expected in EXPECTED_SLICES.items():
            got = self.loader.load(repo_type)
            self.assertEqual(list(got), expected, f"切片不一致: {repo_type}")

    def test_load_all_covers_known_types(self):
        all_types = self.loader.load_all()
        self.assertEqual(set(all_types), set(EXPECTED_SLICES))
        for name in EXPECTED_SLICES:
            self.assertEqual(list(all_types[name]), EXPECTED_SLICES[name])

    def test_fallback_dimensions_present(self):
        fb = self.loader.fallback()
        self.assertTrue(fb, "fallback 不应为空")
        for file_name, label, patterns in fb:
            self.assertTrue(file_name.endswith(".xml"))

    def test_unknown_type_falls_back(self):
        # 未知类型应回退 fallback 且不抛异常（stdout/stderr 可含 warning）
        got = self.loader.load("does-not-exist")
        self.assertEqual(list(got), list(self.loader.fallback()))

    def test_tuple_shape(self):
        for file_name, label, patterns in self.loader.load("web-fullstack"):
            self.assertIsInstance(file_name, str)
            self.assertIsInstance(label, str)
            self.assertIsInstance(patterns, list)


class YamlSubsetParserTest(unittest.TestCase):
    def test_split_flow_respects_nested_commas(self):
        # 顶层逗号切分；引号内与方括号内的逗号不切分
        self.assertEqual(_split_flow('a, b, "c,d"'), ['a', 'b', '"c,d"'])
        self.assertEqual(_split_flow('[1, 2], [3, 4]'), ['[1, 2]', '[3, 4]'])

    def test_scalar_inline_list(self):
        data = _parse_yaml('patterns: ["*.py", "*.go"]\n')
        self.assertEqual(data["patterns"], ["*.py", "*.go"])

    def test_block_mapping_and_list(self):
        text = (
            "repo_types:\n"
            "  web:\n"
            "    dimensions:\n"
            "      - file: 01-a.xml\n"
            "        label: A\n"
            "        patterns: [\"*.ts\"]\n"
        )
        data = _parse_yaml(text)
        dims = data["repo_types"]["web"]["dimensions"]
        self.assertEqual(dims[0]["file"], "01-a.xml")
        self.assertEqual(dims[0]["patterns"], ["*.ts"])

    def test_top_level_scalar(self):
        data = _parse_yaml("version: 1\nname: foo\n")
        self.assertEqual(data["version"], 1)
        self.assertEqual(data["name"], "foo")

    def test_comments_ignored(self):
        text = (
            "# 这是注释\n"
            "version: 2  # 行尾注释\n"
            "name: bar\n"
        )
        data = _parse_yaml(text)
        self.assertEqual(data["version"], 2)
        self.assertEqual(data["name"], "bar")


if __name__ == "__main__":
    unittest.main()
