"""Contract tests for the Markdown-only collaboration protocol.

The project intentionally has no runtime service, CLI, hooks, or database.
These tests validate that the shipped Skills, templates, examples, and docs
continue to describe one coherent Lead/Member workflow.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]

README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
LEAD_SKILL = ROOT / "skills" / "team-lead-collaboration" / "SKILL.md"
MEMBER_SKILL = ROOT / "skills" / "team-member-collaboration" / "SKILL.md"
TEMPLATES = ROOT / "templates"
EXAMPLE = ROOT / "examples" / "tiny-team-project"

LOCK_FIELDS = [
    "Actor:",
    "Agent:",
    "Role:",
    "Status: reading | writing | paused",
    "Scope:",
    "Task:",
    "Started:",
    "Last Updated:",
    "Expected Finish:",
    "Notes:",
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

    def test_lead_required_mode_questions_are_protected(self) -> None:
        text = read(LEAD_SKILL)
        assert_contains_all(
            self,
            text,
            [
                "Do you want to enable Task Assignment Mode?",
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

    def test_soft_lock_shape_is_consistent_across_skills_and_template(self) -> None:
        paths = [
            LEAD_SKILL,
            MEMBER_SKILL,
            TEMPLATES / "COLLAB_LOG.md",
        ]

        for path in paths:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                assert_contains_all(self, read(path), LOCK_FIELDS)


class TemplateContractTests(unittest.TestCase):
    def test_agents_template_has_required_operational_sections(self) -> None:
        text = read(TEMPLATES / "AGENTS.md")
        assert_contains_all(
            self,
            text,
            [
                "## Project Overview",
                "## Collaboration Mode",
                "## Actor Naming",
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

    def test_collab_log_keeps_active_locks_near_top(self) -> None:
        text = read(TEMPLATES / "COLLAB_LOG.md")
        active_locks = text.index("## Active Work Locks")
        current_summary = text.index("## Current Summary")

        self.assertLess(active_locks, current_summary)
        assert_contains_all(
            self,
            text,
            [
                "## Active Work Locks",
                "## Current Summary",
                "## Active Blockers",
                "## Recent Decisions",
                "## Latest Updates",
                "## Handoffs",
                "## History / Archived Notes",
                "Current locks:",
                "- None.",
            ],
        )

    def test_task_statuses_are_shared_and_complete(self) -> None:
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
                "## Backlog",
                "## Review Queue",
                "## Done",
            ],
        )

    def test_module_ownership_template_is_optional_and_complete(self) -> None:
        text = read(TEMPLATES / "MODULE_OWNERSHIP.md")
        assert_contains_all(
            self,
            text,
            [
                "Module Ownership Mode is optional.",
                "## Modules",
                "## Owners",
                "## Allowed Paths",
                "## Avoid / Protected Paths",
                "## Interfaces",
                "## Risks",
                "## Cross-module Notes",
            ],
        )


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

    def test_tiny_team_member_lifecycle_is_demonstrated(self) -> None:
        log = read(EXAMPLE / "COLLAB_LOG.md")
        tasks = read(EXAMPLE / "TEAM_TASKS.md")

        assert_contains_all(
            self,
            log,
            [
                "Current locks:",
                "- None.",
                "Example lock used during the flow:",
                "Content Worker",
                "removed lock",
            ],
        )
        self.assertIn("| T-001 | READY_FOR_REVIEW | Content Worker | README.md |", tasks)
        self.assertIn("- T-001", tasks)


class MarkdownLinkTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
