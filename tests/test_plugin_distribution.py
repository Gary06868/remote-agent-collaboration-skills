"""Codex Plugin distribution contract tests for Lite Skills."""

from __future__ import annotations

from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.6.0"
PLUGIN_NAME = "remote-agent-collaboration-lite"
MARKETPLACE_NAME = "remote-agent-collaboration-lite"
PLUGIN_ROOT = ROOT / "plugins" / PLUGIN_NAME
PLUGIN_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
PLUGIN_SKILLS = PLUGIN_ROOT / "skills"
PLUGIN_ASSETS = PLUGIN_ROOT / "assets"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"
CHANGELOG = ROOT / "CHANGELOG.md"
INSTALL_REPORT = ROOT / "tests" / "plugin-install" / "README.md"
AUDIT = ROOT / "docs" / "CODEX_PLUGIN_DISTRIBUTION_AUDIT.md"
INSTALL_DOC = ROOT / "docs" / "INSTALLATION.md"
PROTOCOL_DOC = ROOT / "docs" / "PROTOCOL_REFERENCE.md"
REMOTE_GIT_DOC = ROOT / "docs" / "REMOTE_GIT_MODE.md"
ROOT_SKILLS = ROOT / "skills"
LEAD_REFERENCES = ROOT_SKILLS / "team-lead-collaboration" / "references"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_contains_all(testcase: unittest.TestCase, text: str, values: list[str]) -> None:
    for value in values:
        testcase.assertIn(value, text)


class PluginManifestTests(unittest.TestCase):
    def test_plugin_manifest_exists_and_declares_two_independent_skills(self) -> None:
        manifest = load_json(PLUGIN_MANIFEST)

        self.assertEqual(PLUGIN_NAME, manifest["name"])
        self.assertEqual(VERSION, manifest["version"])
        self.assertEqual("Markdown collaboration for small human and AI teams.", manifest["description"])
        self.assertEqual("https://github.com/Gary06868/remote-agent-collaboration-skills", manifest["repository"])
        self.assertEqual("MIT", manifest["license"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertEqual("Remote Agent Collaboration Lite", manifest["interface"]["displayName"])
        self.assertEqual("Gary06868", manifest["interface"]["developerName"])
        self.assertEqual("./assets/plugin-icon.png", manifest["interface"]["composerIcon"])
        self.assertEqual("./assets/plugin-icon.png", manifest["interface"]["logo"])
        self.assertEqual(
            [
                "./assets/plugin-cover-source.png",
                "./assets/plugin-demo.png",
                "./assets/plugin-architecture.png",
            ],
            manifest["interface"]["screenshots"],
        )

        skill_names = sorted(path.name for path in PLUGIN_SKILLS.iterdir() if path.is_dir())
        self.assertEqual(["team-lead-collaboration", "team-member-collaboration"], skill_names)
        for skill_name in skill_names:
            self.assertTrue((PLUGIN_SKILLS / skill_name / "SKILL.md").exists())

    def test_plugin_manifest_contains_no_runtime_enforcement_surface(self) -> None:
        manifest = load_json(PLUGIN_MANIFEST)
        manifest_text = json.dumps(manifest, sort_keys=True).lower()

        for forbidden_key in ["hooks", "mcpservers", "apps", "cli", "commands", "services"]:
            self.assertNotIn(forbidden_key, {key.lower() for key in manifest.keys()})
            self.assertNotIn(f'"{forbidden_key}"', manifest_text)

        for forbidden_value in ["collabctl", "phase 0", "session_id", "doctor"]:
            self.assertNotIn(forbidden_value, manifest_text)

    def test_plugin_skill_bundle_matches_root_skills(self) -> None:
        for skill_name in ["team-lead-collaboration", "team-member-collaboration"]:
            with self.subTest(skill=skill_name):
                self.assertEqual(
                    (ROOT_SKILLS / skill_name / "SKILL.md").read_bytes(),
                    (PLUGIN_SKILLS / skill_name / "SKILL.md").read_bytes(),
                )

        for reference in [
            "AGENTS.template.md",
            "COLLAB_LOG.template.md",
            "TEAM_TASKS.template.md",
            "MODULE_OWNERSHIP.template.md",
        ]:
            with self.subTest(reference=reference):
                self.assertEqual(
                    (LEAD_REFERENCES / reference).read_bytes(),
                    (PLUGIN_SKILLS / "team-lead-collaboration" / "references" / reference).read_bytes(),
                )

    def test_plugin_icon_is_original_png_asset(self) -> None:
        icon = PLUGIN_ASSETS / "plugin-icon.png"

        self.assertTrue(icon.exists())
        self.assertTrue(icon.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertLess(icon.stat().st_size, 200_000)

    def test_plugin_screenshots_are_packaged_png_assets(self) -> None:
        manifest = load_json(PLUGIN_MANIFEST)
        screenshots = manifest["interface"]["screenshots"]

        self.assertEqual(3, len(screenshots))
        for screenshot in screenshots:
            with self.subTest(screenshot=screenshot):
                self.assertTrue(screenshot.startswith("./assets/"))
                asset = PLUGIN_ROOT / screenshot.removeprefix("./")
                self.assertTrue(asset.exists())
                self.assertTrue(asset.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
                self.assertLess(asset.stat().st_size, 3_000_000)


class MarketplaceMetadataTests(unittest.TestCase):
    def test_marketplace_metadata_references_lite_plugin(self) -> None:
        marketplace = load_json(MARKETPLACE)

        self.assertEqual(MARKETPLACE_NAME, marketplace["name"])
        self.assertEqual("Remote Agent Collaboration Lite", marketplace["interface"]["displayName"])
        self.assertEqual(1, len(marketplace["plugins"]))

        plugin = marketplace["plugins"][0]
        self.assertEqual(PLUGIN_NAME, plugin["name"])
        self.assertEqual({"source": "local", "path": f"./plugins/{PLUGIN_NAME}"}, plugin["source"])
        self.assertEqual("AVAILABLE", plugin["policy"]["installation"])
        self.assertEqual("ON_INSTALL", plugin["policy"]["authentication"])
        self.assertEqual("Developer Tools", plugin["category"])
        self.assertNotIn("products", plugin["policy"])

        resolved = ROOT / plugin["source"]["path"].removeprefix("./")
        self.assertEqual(PLUGIN_ROOT.resolve(), resolved.resolve())
        self.assertTrue((resolved / ".codex-plugin" / "plugin.json").exists())

    def test_marketplace_metadata_has_no_placeholders_or_private_paths(self) -> None:
        text = read(MARKETPLACE)
        windows_roots = ["D:" + "\\", "C:" + "\\"]
        for forbidden in ["TODO", "<owner>", "<repo>", "example.com", *windows_roots, "collabctl"]:
            self.assertNotIn(forbidden, text)
        self.assertIn("remote-agent-collaboration-lite", text)


class InstallationDocsTests(unittest.TestCase):
    def test_readme_uses_plugin_first_install_and_distinguishes_marketplace_add(self) -> None:
        text = read(README)

        assert_contains_all(
            self,
            text,
            [
                "## Install",
                "### Option 1 - Codex Plugin (preferred)",
                "codex plugin marketplace add Gary06868/remote-agent-collaboration-skills",
                "Adding the marketplace does not install the Plugin.",
                "Open `/plugins`",
                "Install `Remote Agent Collaboration Lite`",
                "## For AI Agents: Install the Plugin and Verify Both Skills",
                "No server, no database, no hooks, and no custom collaboration CLI.",
                "Just Markdown files and optional Git.",
                "Plugin name: `remote-agent-collaboration-lite`",
                "Marketplace name: `remote-agent-collaboration-lite`",
            ],
        )
        self.assertLess(text.index("### Option 1 - Codex Plugin"), text.index("### Option 3 - Manual Copy"))
        self.assertNotIn("codex plugin add ", text)
        self.assertNotIn("local Codex CLI", text)
        self.assertNotIn("local CLI", text)
        self.assertNotIn("collabctl", text.lower())

    def test_chinese_readme_syncs_plugin_first_install(self) -> None:
        text = read(README_ZH)

        assert_contains_all(
            self,
            text,
            [
                "## Install",
                "### Option 1 - Codex Plugin（首选）",
                "codex plugin marketplace add Gary06868/remote-agent-collaboration-skills",
                "添加 marketplace 不等于已经安装 Plugin。",
                "打开 `/plugins`",
                "安装 `Remote Agent Collaboration Lite`",
                "## 给 AI Agent：安装 Plugin 并验证两个 Skill",
                "不需要服务器、不需要数据库、不需要 hooks，也不需要自定义协作 CLI。",
                "只有 Markdown 文件和可选 Git。",
            ],
        )
        self.assertLess(text.index("### Option 1 - Codex Plugin"), text.index("### Option 3 - Manual Copy"))
        self.assertNotIn("codex plugin add ", text)
        self.assertNotIn("本机 Codex CLI", text)
        self.assertNotIn("collabctl", text.lower())

    def test_manual_install_docs_use_current_agents_skill_paths(self) -> None:
        for path in [README, README_ZH, INSTALL_DOC]:
            text = read(path)
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIn(".agents/skills", text)
                self.assertNotIn(".codex/skills", text)
                self.assertNotIn(".codex\\skills", text)
                self.assertIn("Remove-Item -Recurse -Force", text)
                self.assertIn("team-lead-collaboration", text)
                self.assertIn("team-member-collaboration", text)

    def test_split_docs_and_audit_exist(self) -> None:
        for path in [AUDIT, INSTALL_DOC, PROTOCOL_DOC, REMOTE_GIT_DOC, INSTALL_REPORT]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertTrue(path.exists())
                self.assertGreater(len(read(path)), 500)

        assert_contains_all(
            self,
            read(AUDIT),
            [
                "Codex version: `codex-cli 0.130.0-alpha.5`",
                ".codex-plugin/plugin.json",
                ".agents/plugins/marketplace.json",
                "`codex plugin marketplace add` is available",
                "`codex plugin add` is not available in this local CLI",
                "Plugin is packaging only",
            ],
        )

    def test_install_report_marks_ui_only_steps_not_run(self) -> None:
        text = read(INSTALL_REPORT)
        assert_contains_all(
            self,
            text,
            [
                "Plugin install via `/plugins`: NOT RUN",
                "Non-interactive plugin install: NOT SUPPORTED by local CLI",
                "Lead Skill visible after UI install: NOT RUN",
                "Member Skill visible after UI install: NOT RUN",
                "Hooks installed: no",
                "Custom collaboration CLI installed: no",
            ],
        )


class InstallSafetySimulationTests(unittest.TestCase):
    def copy_plugin_once(self, source: Path, target_plugins: Path) -> None:
        target_plugins.mkdir(parents=True, exist_ok=True)
        target = target_plugins / PLUGIN_NAME
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)

    def test_repeated_plugin_copy_install_is_idempotent_and_preserves_other_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "plugins"
            other = target_root / "unrelated-plugin"
            other.mkdir(parents=True)
            (other / ".keep").write_text("keep", encoding="utf-8")

            self.copy_plugin_once(PLUGIN_ROOT, target_root)
            stale = target_root / PLUGIN_NAME / "stale-file.md"
            stale.write_text("stale", encoding="utf-8")
            nested = target_root / PLUGIN_NAME / PLUGIN_NAME
            nested.mkdir()

            self.copy_plugin_once(PLUGIN_ROOT, target_root)

            self.assertFalse(stale.exists())
            self.assertFalse(nested.exists())
            self.assertTrue((other / ".keep").exists())
            self.assertTrue((target_root / PLUGIN_NAME / "skills" / "team-lead-collaboration" / "references" / "AGENTS.template.md").exists())

    def test_simulated_plugin_uninstall_does_not_delete_project_collaboration_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin_target = root / "plugins"
            project = root / "project"
            project.mkdir()
            for name in ["AGENTS.md", "COLLAB_LOG.md", "TEAM_TASKS.md", "MODULE_OWNERSHIP.md"]:
                (project / name).write_text(name, encoding="utf-8")
            (project / ".collab").mkdir()
            (project / ".collab" / "README.md").write_text("state", encoding="utf-8")

            self.copy_plugin_once(PLUGIN_ROOT, plugin_target)
            shutil.rmtree(plugin_target / PLUGIN_NAME)

            for name in ["AGENTS.md", "COLLAB_LOG.md", "TEAM_TASKS.md", "MODULE_OWNERSHIP.md"]:
                self.assertTrue((project / name).exists())
            self.assertTrue((project / ".collab" / "README.md").exists())


class ArchiveAndPrivacyTests(unittest.TestCase):
    def test_release_candidate_contains_plugin_and_excludes_test_temp(self) -> None:
        names = set(
            subprocess.check_output(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                cwd=ROOT,
                text=True,
            ).splitlines()
        )

        self.assertIn(f"plugins/{PLUGIN_NAME}/.codex-plugin/plugin.json", names)
        self.assertIn(f"plugins/{PLUGIN_NAME}/skills/team-lead-collaboration/SKILL.md", names)
        self.assertIn(f"plugins/{PLUGIN_NAME}/skills/team-member-collaboration/SKILL.md", names)
        self.assertFalse(any(name.startswith("tests/temp/") for name in names))

    def test_public_distribution_files_are_utf8_without_bom(self) -> None:
        files = [
            PLUGIN_MANIFEST,
            PLUGIN_SKILLS / "team-lead-collaboration" / "SKILL.md",
            PLUGIN_SKILLS / "team-member-collaboration" / "SKILL.md",
            MARKETPLACE,
            README,
            README_ZH,
            AUDIT,
            INSTALL_REPORT,
        ]
        for path in files:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertFalse(path.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_plugin_distribution_privacy_scan(self) -> None:
        private_patterns = [
            r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]+[^\s\"'`<>|*?]+",
            r"sk-proj-[A-Za-z0-9_-]+",
            r"sk-[A-Za-z0-9]{20,}",
            r"tests/temp/" + r"remote-collab-" + r"identity-e2e",
        ]
        tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
        for relative_path in tracked:
            path = ROOT / relative_path
            if path.is_dir() or path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".py", ".ps1", ".sh", ".svg"}:
                continue
            text = read(path)
            for pattern in private_patterns:
                with self.subTest(path=relative_path, pattern=pattern):
                    self.assertIsNone(re.search(pattern, text), f"Found private pattern {pattern}")

    def test_local_markdown_links_resolve_for_new_docs(self) -> None:
        files = [README, README_ZH, AUDIT, INSTALL_DOC, PROTOCOL_DOC, REMOTE_GIT_DOC, INSTALL_REPORT]
        for path in files:
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", read(path)):
                if re.match(r"^[a-z]+://", target) or target.startswith("#"):
                    continue
                clean = target.split("#", 1)[0]
                if not clean:
                    continue
                resolved = (path.parent / clean).resolve()
                with self.subTest(source=path.relative_to(ROOT).as_posix(), target=target):
                    self.assertTrue(resolved.exists(), f"Missing local link target: {target}")


class VersionConsistencyTests(unittest.TestCase):
    def test_version_is_consistent_across_distribution_files(self) -> None:
        self.assertEqual(VERSION, load_json(PLUGIN_MANIFEST)["version"])
        for path in [README, README_ZH, CHANGELOG, INSTALL_REPORT, AUDIT]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIn(VERSION, read(path))


if __name__ == "__main__":
    unittest.main()
