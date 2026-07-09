"""Claude Code plugin distribution contract tests for Lite Skills.

Claude Code discovers a plugin from a marketplace catalog at
`.claude-plugin/marketplace.json` and a plugin manifest at
`<plugin>/.claude-plugin/plugin.json`. The plugin reuses the same bundled
Skills as the Codex plugin, so both Skills appear as the
`/team-lead-collaboration` and `/team-member-collaboration` slash commands.

The Claude plugin, like the Codex plugin, is packaging only: no hooks, no MCP
server, no custom collaboration CLI.
"""

from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.7.0"
PLUGIN_NAME = "remote-agent-collaboration-lite"
MARKETPLACE_NAME = "remote-agent-collaboration-skills"
PLUGIN_ROOT = ROOT / "plugins" / PLUGIN_NAME
CLAUDE_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_SKILLS = PLUGIN_ROOT / "skills"
SKILL_NAMES = ["team-lead-collaboration", "team-member-collaboration"]
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_contains_all(testcase: unittest.TestCase, text: str, values: list[str]) -> None:
    for value in values:
        testcase.assertIn(value, text)


class ClaudePluginManifestTests(unittest.TestCase):
    def test_claude_manifest_declares_lite_plugin(self) -> None:
        manifest = load_json(CLAUDE_MANIFEST)

        self.assertEqual(PLUGIN_NAME, manifest["name"])
        self.assertEqual(VERSION, manifest["version"])
        self.assertEqual("Remote Agent Collaboration Lite", manifest["displayName"])
        self.assertEqual("MIT", manifest["license"])
        self.assertEqual(
            "https://github.com/Gary06868/remote-agent-collaboration-skills",
            manifest["repository"],
        )
        self.assertEqual("Gary06868", manifest["author"]["name"])

    def test_claude_manifest_bundles_two_skills_by_default_scan(self) -> None:
        # The plugin relies on the default `skills/` scan, so both Skills become
        # the `/team-lead-collaboration` and `/team-member-collaboration` shortcuts.
        skill_names = sorted(path.name for path in PLUGIN_SKILLS.iterdir() if path.is_dir())
        self.assertEqual(SKILL_NAMES, skill_names)
        for skill_name in SKILL_NAMES:
            skill = PLUGIN_SKILLS / skill_name / "SKILL.md"
            self.assertTrue(skill.exists())
            self.assertIn(f"name: {skill_name}", read(skill))

    def test_claude_manifest_is_packaging_only(self) -> None:
        manifest = load_json(CLAUDE_MANIFEST)
        manifest_text = json.dumps(manifest, sort_keys=True).lower()

        for forbidden_key in ["hooks", "mcpservers", "lspservers", "monitors", "cli"]:
            self.assertNotIn(forbidden_key, {key.lower() for key in manifest.keys()})
            self.assertNotIn(f'"{forbidden_key}"', manifest_text)
        for forbidden_value in ["collabctl", "session_id", "doctor"]:
            self.assertNotIn(forbidden_value, manifest_text)

    def test_claude_manifest_coexists_with_codex_manifest(self) -> None:
        self.assertTrue((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").exists())
        self.assertTrue((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").exists())
        self.assertEqual(
            VERSION,
            load_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")["version"],
        )


class ClaudeMarketplaceTests(unittest.TestCase):
    def test_marketplace_lists_lite_plugin_from_relative_source(self) -> None:
        marketplace = load_json(CLAUDE_MARKETPLACE)

        self.assertEqual(MARKETPLACE_NAME, marketplace["name"])
        self.assertEqual("Gary06868", marketplace["owner"]["name"])
        self.assertEqual(1, len(marketplace["plugins"]))

        plugin = marketplace["plugins"][0]
        self.assertEqual(PLUGIN_NAME, plugin["name"])
        self.assertEqual(f"./plugins/{PLUGIN_NAME}", plugin["source"])
        self.assertEqual(VERSION, plugin["version"])

    def test_marketplace_relative_source_resolves_to_plugin(self) -> None:
        plugin = load_json(CLAUDE_MARKETPLACE)["plugins"][0]
        source = plugin["source"]

        self.assertTrue(source.startswith("./"))
        resolved = ROOT / source.removeprefix("./")
        self.assertEqual(PLUGIN_ROOT.resolve(), resolved.resolve())
        self.assertTrue((resolved / ".claude-plugin" / "plugin.json").exists())

    def test_marketplace_has_no_placeholders_or_private_paths(self) -> None:
        text = read(CLAUDE_MARKETPLACE)
        windows_roots = ["D:" + "\\", "C:" + "\\"]
        for forbidden in ["TODO", "<owner>", "<repo>", "example.com", *windows_roots]:
            self.assertNotIn(forbidden, text)


class ClaudeInstallDocsTests(unittest.TestCase):
    def test_readme_documents_claude_plugin_install(self) -> None:
        text = read(README)
        assert_contains_all(
            self,
            text,
            [
                "### Option 2 - Claude Code Plugin",
                "/plugin marketplace add Gary06868/remote-agent-collaboration-skills",
                f"/plugin install {PLUGIN_NAME}@{MARKETPLACE_NAME}",
                "/team-lead-collaboration",
                "/team-member-collaboration",
            ],
        )

    def test_chinese_readme_documents_claude_plugin_install(self) -> None:
        text = read(README_ZH)
        assert_contains_all(
            self,
            text,
            [
                "### Option 2 - Claude Code Plugin",
                "/plugin marketplace add Gary06868/remote-agent-collaboration-skills",
                f"/plugin install {PLUGIN_NAME}@{MARKETPLACE_NAME}",
                "/team-lead-collaboration",
                "/team-member-collaboration",
            ],
        )


class ClaudeQuickStartAssetTests(unittest.TestCase):
    GIF_REL = "docs/assets/claude-code-quickstart.gif"

    def test_quickstart_gif_exists_and_is_a_valid_gif(self) -> None:
        gif = ROOT / self.GIF_REL
        self.assertTrue(gif.exists())
        head = gif.read_bytes()[:6]
        self.assertIn(head, (b"GIF87a", b"GIF89a"))
        self.assertLess(gif.stat().st_size, 3_000_000)

    def test_readmes_reference_the_quickstart_gif(self) -> None:
        for path in [README, README_ZH]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = read(path)
                self.assertIn(f"]({self.GIF_REL})", text)
                # The test suite forbids a `demo.gif` asset name and "video demo" copy.
                self.assertNotIn("demo.gif", text)
                self.assertNotIn("video demo", text.lower())


class ClaudeDistributionFileHygieneTests(unittest.TestCase):
    def test_claude_distribution_files_are_utf8_without_bom(self) -> None:
        for path in [CLAUDE_MANIFEST, CLAUDE_MARKETPLACE]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertFalse(path.read_bytes().startswith(b"\xef\xbb\xbf"))


if __name__ == "__main__":
    unittest.main()
