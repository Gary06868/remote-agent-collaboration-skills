"""Contract tests for the Markdown-only collaboration protocol.

The project intentionally has no runtime service, CLI, hooks, or database.
These tests validate that the shipped Skills, templates, examples, and docs
continue to describe one coherent Lite Lead/Member workflow.
"""

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
CHANGELOG = ROOT / "CHANGELOG.md"
LEAD_SKILL = ROOT / "skills" / "team-lead-collaboration" / "SKILL.md"
MEMBER_SKILL = ROOT / "skills" / "team-member-collaboration" / "SKILL.md"
TEMPLATES = ROOT / "templates"
LEAD_REFERENCES = ROOT / "skills" / "team-lead-collaboration" / "references"
EXAMPLE = ROOT / "examples" / "tiny-team-project"
E2E_REPORT = ROOT / "tests" / "e2e" / "2026-06-24-lite-collaboration.md"

FORBIDDEN_ACTORS = [
    "Lead" + "-Setup",
    "Member" + "-Content-01",
    "Generic Lead",
    "Generic Member",
    "Content Worker",
]

IDENTITY_FIELDS = [
    "Human owner:",
    "Agent platform:",
    "Collaboration role:",
    "Functional role:",
    "Instance:",
    "Actor ID:",
    "Display name:",
]

LOCK_FIELDS = [
    "Actor ID:",
    "Display Name:",
    "Collaboration Role: Lead | Member",
    "Functional Role:",
    "Status: reading | writing | paused",
    "Scope:",
    "Task:",
    "Started:",
    "Last Updated:",
    "Expected Finish:",
    "Notes:",
]

HANDOFF_FIELDS = [
    "Handoff ID:",
    "From Actor:",
    "Target Type: actor | human-user",
    "Target Actor ID:",
    "Target Human:",
    "Task:",
    "Scope:",
    "Required Next Action:",
    "Status: open | accepted | resolved | cancelled",
    "Created:",
    "Last Updated:",
]

TASK_STATUSES = {
    "BACKLOG",
    "ASSIGNED",
    "IN_PROGRESS",
    "BLOCKED",
    "READY_FOR_REVIEW",
    "CHANGES_REQUESTED",
    "DONE",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_contains_all(testcase: unittest.TestCase, text: str, values: list[str]) -> None:
    for value in values:
        testcase.assertIn(value, text)


def section(text: str, heading: str) -> str:
    start = text.index(heading)
    match = re.search(r"\n## ", text[start + len(heading) :])
    if not match:
        return text[start:]
    return text[start : start + len(heading) + match.start()]


class ProductBoundaryTests(unittest.TestCase):
    def test_readmes_preserve_lite_product_boundary(self) -> None:
        english = read(README)
        chinese = read(README_ZH)

        assert_contains_all(
            self,
            english,
            [
                "Remote Agent Collaboration Lite",
                "No server, no database, no CLI, no hooks.",
                "It does not try to enforce permissions.",
                "soft locks",
                "team-lead-collaboration",
                "team-member-collaboration",
                "Advanced local protocol experiments are preserved on the `standard-local-protocol` branch.",
            ],
        )
        assert_contains_all(
            self,
            chinese,
            [
                "Remote Agent Collaboration Lite",
                "不需要服务器、不需要数据库、不需要 CLI、不需要 hooks。",
                "它不是权限系统。",
                "软锁",
                "team-lead-collaboration",
                "team-member-collaboration",
            ],
        )

    def test_main_branch_docs_do_not_reintroduce_standard_runtime(self) -> None:
        texts = {
            path.relative_to(ROOT).as_posix(): read(path)
            for path in [
                README,
                README_ZH,
                LEAD_SKILL,
                MEMBER_SKILL,
                TEMPLATES / "AGENTS.md",
                TEMPLATES / "COLLAB_LOG.md",
                TEMPLATES / "TEAM_TASKS.md",
            ]
        }

        for name, text in texts.items():
            lowered = text.lower()
            with self.subTest(path=name):
                self.assertNotIn("collabctl", lowered)
                self.assertNotIn("phase 0", lowered)
                self.assertNotIn("session_id", lowered)
                self.assertNotIn("doctor", lowered)

    def test_contributing_keeps_main_branch_lightweight(self) -> None:
        text = read(CONTRIBUTING)
        assert_contains_all(
            self,
            text,
            [
                "main` branch is intentionally lightweight",
                "Markdown Skills",
                "Project collaboration templates",
                "Avoid adding infrastructure to `main`",
            ],
        )


class SkillContractTests(unittest.TestCase):
    def test_lead_skill_is_explicit_and_non_enforcing(self) -> None:
        text = read(LEAD_SKILL)
        assert_contains_all(
            self,
            text,
            [
                "name: team-lead-collaboration",
                "Use only when the user explicitly selects $team-lead-collaboration",
                "Do not use this Skill implicitly.",
                "Do not claim hard permission enforcement, role locks, hooks, a CLI, or a server.",
                "Do not use this Skill when the user wants you to act only as a task executor",
            ],
        )

    def test_member_skill_is_explicit_and_non_enforcing(self) -> None:
        text = read(MEMBER_SKILL)
        assert_contains_all(
            self,
            text,
            [
                "name: team-member-collaboration",
                "Use only when the user explicitly selects $team-member-collaboration",
                "Do not use this Skill implicitly.",
                "Do not claim hard permission enforcement, role locks, hooks, a CLI, or a server.",
                "Do not use this Skill when the user asks you to initialize collaboration rules",
            ],
        )

    def test_lead_and_member_define_complete_identity_bootstrap(self) -> None:
        lead = read(LEAD_SKILL)
        member = read(MEMBER_SKILL)

        for path, text, fixed_role in [
            (LEAD_SKILL, lead, "Collaboration role: Lead"),
            (MEMBER_SKILL, member, "Collaboration role: Member"),
        ]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                assert_contains_all(self, text, IDENTITY_FIELDS)
                assert_contains_all(
                    self,
                    text,
                    [
                        fixed_role,
                        "Do not ask again whether the actor is Lead or Member.",
                        "If the human owner is unknown, ask the user.",
                        "If the agent platform cannot be determined reliably, ask the user.",
                        "If the functional role is unclear, ask the user.",
                        "Do not use a task name as actor identity.",
                    ],
                )

    def test_lead_required_mode_questions_are_protected(self) -> None:
        text = read(LEAD_SKILL)
        assert_contains_all(
            self,
            text,
            [
                "Do you want to enable Task Assignment Mode?",
                "Who may mark tasks DONE?",
                "Only create `TEAM_TASKS.md` after the user chooses task mode.",
                "Do you want to define module boundaries and owners now?",
                "If no, do not create it.",
                "## What Not To Force",
                "Every project needs module ownership.",
                "Every project needs task management.",
            ],
        )

    def test_member_startup_handles_optional_and_missing_files(self) -> None:
        text = read(MEMBER_SKILL)
        assert_contains_all(
            self,
            text,
            [
                "1. Read `AGENTS.md`.",
                "2. Read `COLLAB_LOG.md`.",
                "3. Check Active Work Locks.",
                "If Task Assignment Mode is enabled and `TEAM_TASKS.md` exists, read your task",
                "If optional files do not exist, continue in Casual Coordination Mode.",
                "If `TEAM_TASKS.md` exists but `AGENTS.md` says Task Assignment Mode is disabled",
                "If `AGENTS.md` or `COLLAB_LOG.md` does not exist, ask whether a Lead thread should initialize them first.",
                "Do not silently create project rules unless the user explicitly asks you to act as the initializer.",
            ],
        )

    def test_lead_and_member_responsibilities_are_separated(self) -> None:
        lead = read(LEAD_SKILL)
        member = read(MEMBER_SKILL)

        assert_contains_all(
            self,
            lead,
            [
                "project owner, maintainer, or coordination thread",
                "Do not use this Skill when the user wants you to act only as a task executor",
                "Assign task owners.",
                "Review member output when needed.",
            ],
        )
        assert_contains_all(
            self,
            member,
            [
                "contributor, implementer, module developer, AI worker",
                "Do not take over Lead responsibilities.",
                "Do not enable Task Assignment Mode yourself.",
                "Do not declare the whole project complete.",
            ],
        )

    def test_soft_lock_shape_is_consistent_across_docs_skills_and_template(self) -> None:
        paths = [
            README,
            README_ZH,
            LEAD_SKILL,
            MEMBER_SKILL,
            TEMPLATES / "COLLAB_LOG.md",
        ]

        for path in paths:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                assert_contains_all(self, read(path), LOCK_FIELDS)

    def test_reading_writing_paused_conflict_semantics_are_consistent(self) -> None:
        required = [
            "reading with reading does not conflict by default",
            "writing with overlapping writing is a conflict",
            "reading with overlapping writing requires a warning",
            "paused still reserves the scope",
            "stale threshold: 2 hours",
            "Do not remove another actor's stale lock without user or Lead confirmation.",
            "double-check Active Work Locks after writing your own lock",
        ]
        for path in [README, LEAD_SKILL, MEMBER_SKILL, TEMPLATES / "AGENTS.md"]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                assert_contains_all(self, read(path), required)

    def test_final_reconciliation_is_required_for_both_skills(self) -> None:
        required = [
            "## Final Reconciliation",
            "Active Work Locks match the real state",
            "TEAM_TASKS.md status matches the real state",
            "Current Snapshot reflects the latest work",
            "Open Handoffs only contain unresolved items",
            "actor_id is consistent across AGENTS.md, COLLAB_LOG.md, TEAM_TASKS.md, and MODULE_OWNERSHIP.md",
        ]
        for path in [LEAD_SKILL, MEMBER_SKILL]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                assert_contains_all(self, read(path), required)


class TemplateContractTests(unittest.TestCase):
    def test_agents_template_has_actor_registry_and_operational_sections(self) -> None:
        text = read(TEMPLATES / "AGENTS.md")
        assert_contains_all(
            self,
            text,
            [
                "## Project Overview",
                "## Collaboration Mode",
                "## Project Time",
                "Project timezone:",
                "Timestamp format: ISO 8601 with UTC offset",
                "## Actor Registry",
                "### <actor-id>",
                "Display name:",
                "Human owner:",
                "Agent platform:",
                "Collaboration role: Lead | Member",
                "Functional role:",
                "Instance:",
                "Status: active | paused | retired",
                "Current scope:",
                "Registered at:",
                "Last seen:",
                "## Completion Policy",
                "Who may mark tasks DONE:",
                "## Startup Checklist",
                "## Active Work Lock Rules",
                "## Git Rules",
                "## File Organization Rules",
                "## Logging Rules",
                "## Conflict Handling",
                "## Completion / Handoff Rules",
                "## When To Ask The User",
                "Task Assignment Mode: disabled by default",
                "Module Ownership Mode: disabled by default",
            ],
        )

    def test_collab_log_uses_current_snapshot_and_open_handoffs(self) -> None:
        text = read(TEMPLATES / "COLLAB_LOG.md")
        active_locks = text.index("## Active Work Locks")
        current_snapshot = text.index("## Current Snapshot")
        open_handoffs = text.index("## Open Handoffs")
        history = text.index("## History / Archived Notes")

        self.assertLess(active_locks, current_snapshot)
        self.assertLess(open_handoffs, history)
        self.assertNotIn("## Current Summary", text)
        self.assertNotIn("## Handoffs\n", text)
        assert_contains_all(
            self,
            text,
            [
                "## Active Work Locks",
                "## Current Snapshot",
                "Stage:",
                "Current focus:",
                "Active work:",
                "Next action:",
                "Last updated:",
                "Updated by:",
                "## Active Blockers",
                "## Open Handoffs",
                "## Recent Decisions",
                "## Latest Updates",
                "## History / Archived Notes",
                "Current locks:",
                "- None.",
            ],
        )
        assert_contains_all(self, text, HANDOFF_FIELDS)

    def test_task_statuses_and_owner_identity_are_shared_and_complete(self) -> None:
        text = read(TEMPLATES / "TEAM_TASKS.md")
        found = set(re.findall(r"- `([A-Z_]+)`:", text))

        self.assertEqual(TASK_STATUSES, found)
        assert_contains_all(
            self,
            text,
            [
                "Task Assignment Mode is optional.",
                "Default Member completion status is `READY_FOR_REVIEW` unless",
                "## Current Tasks",
                "## TASK-001",
                "Owner ID:",
                "Owner Display:",
                "Next Action:",
                "## Backlog",
                "## Review Queue",
                "## Done",
            ],
        )

    def test_module_ownership_template_is_optional_and_identity_aware(self) -> None:
        text = read(TEMPLATES / "MODULE_OWNERSHIP.md")
        assert_contains_all(
            self,
            text,
            [
                "Module Ownership Mode is optional.",
                "## Modules",
                "## Owners",
                "Actor ID:",
                "Display Name:",
                "## Allowed Paths",
                "## Avoid / Protected Paths",
                "## Interfaces",
                "## Risks",
                "## Cross-module Notes",
            ],
        )

    def test_lead_skill_carries_self_contained_templates(self) -> None:
        expected = {
            "AGENTS.template.md": TEMPLATES / "AGENTS.md",
            "COLLAB_LOG.template.md": TEMPLATES / "COLLAB_LOG.md",
            "TEAM_TASKS.template.md": TEMPLATES / "TEAM_TASKS.md",
            "MODULE_OWNERSHIP.template.md": TEMPLATES / "MODULE_OWNERSHIP.md",
        }

        for reference_name, root_template in expected.items():
            reference = LEAD_REFERENCES / reference_name
            with self.subTest(reference=reference_name):
                self.assertTrue(reference.exists())
                self.assertEqual(read(root_template), read(reference))

    def test_copying_only_skill_directories_keeps_required_lead_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            shutil.copytree(ROOT / "skills" / "team-lead-collaboration", target / "team-lead-collaboration")
            shutil.copytree(ROOT / "skills" / "team-member-collaboration", target / "team-member-collaboration")

            for name in [
                "AGENTS.template.md",
                "COLLAB_LOG.template.md",
                "TEAM_TASKS.template.md",
                "MODULE_OWNERSHIP.template.md",
            ]:
                self.assertTrue((target / "team-lead-collaboration" / "references" / name).exists())


class ExampleConsistencyTests(unittest.TestCase):
    def test_tiny_team_example_mode_choices_are_consistent(self) -> None:
        readme = read(EXAMPLE / "README.md")
        agents = read(EXAMPLE / "AGENTS.md")
        tasks = read(EXAMPLE / "TEAM_TASKS.md")
        log = read(EXAMPLE / "COLLAB_LOG.md")

        assert_contains_all(
            self,
            readme,
            [
                "Task Assignment Mode enabled.",
                "Module Ownership Mode not enabled yet.",
                "The Lead creates `TEAM_TASKS.md`.",
                "The Member reads `AGENTS.md`, `COLLAB_LOG.md`, and `TEAM_TASKS.md`.",
            ],
        )
        assert_contains_all(
            self,
            agents,
            [
                "Task Assignment Mode: enabled.",
                "Module Ownership Mode: not enabled yet.",
                "Who may mark tasks DONE: Lead review.",
            ],
        )
        self.assertIn("Task Assignment Mode is enabled", tasks)
        assert_contains_all(
            self,
            log,
            [
                "Task Assignment Mode is enabled.",
                "Module Ownership Mode is not enabled yet.",
            ],
        )
        self.assertFalse((EXAMPLE / "MODULE_OWNERSHIP.md").exists())

    def test_tiny_team_actor_registry_uses_unique_stable_actor_ids(self) -> None:
        agents = read(EXAMPLE / "AGENTS.md")
        actor_ids = re.findall(r"^### ([a-z0-9-]+)$", agents, flags=re.MULTILINE)

        self.assertEqual(len(actor_ids), len(set(actor_ids)))
        self.assertEqual(
            {
                "alex-codex-lead-coordinator-01",
                "morgan-claude-member-content-01",
                "alex-codex-member-test-02",
            },
            set(actor_ids),
        )
        assert_contains_all(
            self,
            agents,
            [
                "Alex's Codex #01 (Lead - Project Coordinator)",
                "Morgan's Claude #01 (Member - Content Developer)",
                "Alex's Codex #02 (Member - Test Engineer)",
                "Human owner: Alex",
                "Human owner: Morgan",
                "Agent platform: Codex",
                "Agent platform: Claude",
                "Instance: 01",
                "Instance: 02",
            ],
        )

    def test_tiny_team_example_has_no_temporary_actor_names(self) -> None:
        combined = "\n".join(
            read(path)
            for path in [
                EXAMPLE / "AGENTS.md",
                EXAMPLE / "COLLAB_LOG.md",
                EXAMPLE / "TEAM_TASKS.md",
                EXAMPLE / "README.md",
            ]
        )
        for value in FORBIDDEN_ACTORS:
            self.assertNotIn(value, combined)

    def test_tiny_team_ready_for_review_state_is_semantically_consistent(self) -> None:
        log = read(EXAMPLE / "COLLAB_LOG.md")
        tasks = read(EXAMPLE / "TEAM_TASKS.md")

        current_locks = section(log, "## Active Work Locks")
        current_snapshot = section(log, "## Current Snapshot")
        open_handoffs = section(log, "## Open Handoffs")
        history = section(log, "## History / Archived Notes")

        assert_contains_all(
            self,
            current_locks,
            [
                "Current locks:",
                "- None.",
            ],
        )
        self.assertNotIn("Status: writing", current_locks)
        assert_contains_all(
            self,
            current_snapshot,
            [
                "Stage: Review.",
                "Active work: TASK-001 is ready for review; no active write lock remains.",
                "Next action: alex-codex-lead-coordinator-01 reviews TASK-001.",
                "Updated by: morgan-claude-member-content-01",
            ],
        )
        assert_contains_all(
            self,
            tasks,
            [
                "## TASK-001",
                "Status: READY_FOR_REVIEW",
                "Owner ID: morgan-claude-member-content-01",
                "Owner Display: Morgan's Claude #01 (Member - Content Developer)",
                "Next Action: alex-codex-lead-coordinator-01 reviews TASK-001.",
            ],
        )
        assert_contains_all(
            self,
            open_handoffs,
            [
                "Handoff ID: H-002",
                "From Actor: morgan-claude-member-content-01",
                "Target Type: actor",
                "Target Actor ID: alex-codex-lead-coordinator-01",
                "Task: TASK-001",
                "Status: open",
            ],
        )
        self.assertNotIn("Lead -> Member", open_handoffs)
        self.assertNotIn("take TASK-001", open_handoffs)
        assert_contains_all(
            self,
            history,
            [
                "Handoff ID: H-001",
                "Status: resolved",
                "Morgan accepted and completed TASK-001.",
            ],
        )

    def test_tiny_team_conflict_stop_is_demonstrated_without_business_edits(self) -> None:
        log = read(EXAMPLE / "COLLAB_LOG.md")
        assert_contains_all(
            self,
            log,
            [
                "alex-codex-member-test-02 detected overlap with morgan-claude-member-content-01 on `README.md`",
                "stopped before editing business files",
                "writing with overlapping writing is a conflict",
            ],
        )

    def test_timestamps_include_utc_offsets(self) -> None:
        combined = "\n".join(
            read(path)
            for path in [
                EXAMPLE / "AGENTS.md",
                EXAMPLE / "COLLAB_LOG.md",
                EXAMPLE / "TEAM_TASKS.md",
            ]
        )
        timestamps = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", combined)
        self.assertGreaterEqual(len(timestamps), 8)


class InstallDocsTests(unittest.TestCase):
    def test_readme_has_tested_sixty_second_install_without_codex_marketplace_claims(self) -> None:
        text = read(README)
        assert_contains_all(
            self,
            text,
            [
                "## 60-Second Install",
                "Copy-paste prompt for an AI Agent",
                "Project-level install",
                "Windows PowerShell",
                "macOS/Linux shell",
                "Installed directory shape",
                "Verify both Skills are visible",
                "Install both Skills. Use one role per thread.",
            ],
        )
        self.assertNotIn("codex plugin marketplace add", text)
        self.assertNotIn("codex plugin add", text)

    def test_chinese_readme_has_matching_agent_install_section(self) -> None:
        text = read(README_ZH)
        assert_contains_all(
            self,
            text,
            [
                "## 60 秒安装",
                "给 AI Agent 的可复制安装 Prompt",
                "项目级安装",
                "Windows PowerShell",
                "macOS/Linux shell",
                "安装后的目录结构",
                "验证两个 Skill 都可见",
                "同时安装两个 Skill。每个 thread 只使用一个角色。",
            ],
        )

    def test_readme_uses_mermaid_instead_of_heavy_hero_asset(self) -> None:
        text = read(README)
        self.assertIn("```mermaid", text)
        self.assertNotIn("hero.svg", text)
        self.assertNotIn("demo.gif", text)


class E2EReportTests(unittest.TestCase):
    def test_e2e_report_records_sanitized_lite_scenarios(self) -> None:
        text = read(E2E_REPORT)
        assert_contains_all(
            self,
            text,
            [
                "Scenario A",
                "Scenario B",
                "Scenario C",
                "Conflict modification blocked: yes",
                "Actor Registry correct: yes",
                "Current Snapshot correct: yes",
                "Open Handoffs correct: yes",
                "No stale instruction: yes",
                "No temporary actor names: yes",
            ],
        )
        self.assertNotRegex(text, r"[A-Za-z]:\\")
        self.assertNotIn("sk-", text)


class MarkdownLinkAndPrivacyTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self) -> None:
        files = [
            README,
            README_ZH,
            CONTRIBUTING,
            EXAMPLE / "README.md",
        ]

        for path in files:
            text = read(path)
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if re.match(r"^[a-z]+://", target) or target.startswith("#"):
                    continue
                clean_target = target.split("#", 1)[0]
                if not clean_target:
                    continue
                resolved = (path.parent / clean_target).resolve()
                with self.subTest(source=path.relative_to(ROOT).as_posix(), target=target):
                    self.assertTrue(resolved.exists(), f"Missing local link target: {target}")

    def test_public_files_do_not_leak_local_paths_or_private_source_terms(self) -> None:
        patterns = [
            r"[A-Za-z]:\\",
            "MetaAgent" + "_devel",
            "meta_agent" + "_platform",
            "b9877" + "e3c",
            "359914" + "ac",
            "Lead" + "-Setup",
            "Member" + "-Content-01",
        ]
        tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
        for relative_path in tracked:
            path = ROOT / relative_path
            if path.is_dir():
                continue
            if path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".py", ".ps1", ".sh", ".svg"}:
                continue
            text = read(path)
            for pattern in patterns:
                with self.subTest(path=path.relative_to(ROOT).as_posix(), pattern=pattern):
                    self.assertIsNone(re.search(pattern, text), f"Found private pattern {pattern}")

    def test_version_is_updated_for_identity_protocol(self) -> None:
        assert_contains_all(
            self,
            read(CHANGELOG),
            [
                "## 0.4.0",
                "Remote Git Mode",
                "Shared Workspace Mode",
                "Actor Identity Protocol",
                "Current Snapshot",
                "Open Handoffs",
            ],
        )


if __name__ == "__main__":
    unittest.main()
