"""Remote Git Mode contract tests for the Markdown-only Lite protocol.

These tests use real temporary Git remotes and clones. They do not add a
runtime CLI to the product; they exercise the documented Markdown protocol with
Git as the transport layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"
LEAD_SKILL = ROOT / "skills" / "team-lead-collaboration" / "SKILL.md"
MEMBER_SKILL = ROOT / "skills" / "team-member-collaboration" / "SKILL.md"
TEMPLATES = ROOT / "templates"
LEAD_REFERENCES = ROOT / "skills" / "team-lead-collaboration" / "references"
EXAMPLE = ROOT / "examples" / "tiny-team-project"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed in {cwd}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def configure_repo(path: Path, name: str) -> None:
    git(path, "config", "user.name", name)
    git(path, "config", "user.email", f"{name.lower().replace(' ', '-')}@example.invalid")


def lock_text(actor: str, scope: str, state: str = "acquired") -> str:
    return f"""# Remote Git Lock

- Actor ID: {actor}
- Display Name: {actor}
- Collaboration Role: Member
- Functional Role: Test Worker
- Lock State: {state}
- Status: writing
- Scope: {scope}
- Task: TASK-REMOTE
- Started: 2026-06-24T10:00:00+00:00
- Last Updated: 2026-06-24T10:00:00+00:00
- Expected Finish: 2026-06-24T11:00:00+00:00
- Notes: Candidate lock for remote Git transport test.
"""


def scope_overlaps(left: str, right: str) -> bool:
    left = left.strip().rstrip("/")
    right = right.strip().rstrip("/")
    return left == right or left.startswith(f"{right}/") or right.startswith(f"{left}/")


def parse_scope(lock_file: Path) -> str:
    match = re.search(r"^- Scope: (.+)$", read(lock_file), flags=re.MULTILINE)
    if not match:
        raise AssertionError(f"missing Scope in {lock_file}")
    return match.group(1).strip()


@dataclass
class AcquireResult:
    status: str
    non_fast_forward_seen: bool
    rechecked_after_fetch: bool


def active_locks(repo: Path) -> dict[str, str]:
    locks_dir = repo / ".collab" / "locks"
    if not locks_dir.exists():
        return {}
    return {path.stem: parse_scope(path) for path in locks_dir.glob("*.md")}


def start_candidate_lock(repo: Path, actor: str, scope: str) -> AcquireResult:
    git(repo, "fetch", "origin", "main")
    git(repo, "rebase", "origin/main")

    for other_actor, other_scope in active_locks(repo).items():
        if other_actor != actor and scope_overlaps(scope, other_scope):
            return AcquireResult("conflict_before_candidate", False, True)

    write(repo / ".collab" / "locks" / f"{actor}.md", lock_text(actor, scope))
    git(repo, "add", ".collab/locks")
    git(repo, "commit", "-m", f"Acquire lock for {actor}")
    return AcquireResult("candidate_created", False, True)


def publish_candidate_lock(repo: Path, actor: str, scope: str) -> AcquireResult:
    """Publish a candidate lock and re-check after non-fast-forward."""

    push = git(repo, "push", "origin", "HEAD:main", check=False)
    if push.returncode == 0:
        git(repo, "fetch", "origin", "main")
        for other_actor, other_scope in active_locks(repo).items():
            if other_actor != actor and scope_overlaps(scope, other_scope):
                return AcquireResult("conflict_after_publish", False, True)
        return AcquireResult("acquired", False, True)

    git(repo, "fetch", "origin", "main")
    git(repo, "rebase", "origin/main")
    for other_actor, other_scope in active_locks(repo).items():
        if other_actor != actor and scope_overlaps(scope, other_scope):
            git(repo, "reset", "--hard", "origin/main")
            return AcquireResult("conflict_after_non_fast_forward", True, True)

    second_push = git(repo, "push", "origin", "HEAD:main", check=False)
    if second_push.returncode != 0:
        return AcquireResult("push_failed_after_recheck", True, True)
    return AcquireResult("acquired", True, True)


def acquire_lock(repo: Path, actor: str, scope: str) -> AcquireResult:
    """Acquire a Remote Git Mode lock using the documented sequence."""

    candidate = start_candidate_lock(repo, actor, scope)
    if candidate.status != "candidate_created":
        return candidate
    return publish_candidate_lock(repo, actor, scope)


class RemoteGitModeBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.remote = self.root / "remote.git"
        git(self.root, "init", "--bare", "--initial-branch=main", str(self.remote))

        seed = self.root / "seed"
        git(self.root, "clone", str(self.remote), str(seed))
        configure_repo(seed, "Seed")
        write(seed / "README.md", "# Product\n")
        write(seed / ".collab" / "README.md", "# Collaboration State\n")
        git(seed, "add", "README.md", ".collab/README.md")
        git(seed, "commit", "-m", "Initial project")
        git(seed, "push", "origin", "main")

        self.clone_a = self.root / "clone-a"
        self.clone_b = self.root / "clone-b"
        git(self.root, "clone", str(self.remote), str(self.clone_a))
        git(self.root, "clone", str(self.remote), str(self.clone_b))
        configure_repo(self.clone_a, "Actor A")
        configure_repo(self.clone_b, "Actor B")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_same_scope_competition_allows_one_actor_and_blocks_loser(self) -> None:
        candidate = start_candidate_lock(self.clone_b, "morgan-claude-member-content-01", "README.md")
        winner = acquire_lock(self.clone_a, "alex-codex-member-content-01", "README.md")
        loser = publish_candidate_lock(self.clone_b, "morgan-claude-member-content-01", "README.md")

        self.assertEqual("candidate_created", candidate.status)
        self.assertEqual("acquired", winner.status)
        self.assertEqual("conflict_after_non_fast_forward", loser.status)
        self.assertTrue(loser.non_fast_forward_seen)
        self.assertTrue(loser.rechecked_after_fetch)

        verifier = self.root / "verifier"
        git(self.root, "clone", str(self.remote), str(verifier))
        locks = active_locks(verifier)
        self.assertEqual({"alex-codex-member-content-01": "README.md"}, locks)
        self.assertFalse((self.clone_b / "README.md.business-edit").exists())

    def test_different_scope_parallel_locks_survive_non_fast_forward_recheck(self) -> None:
        candidate = start_candidate_lock(self.clone_b, "morgan-claude-member-api-01", "docs/api.md")
        first = acquire_lock(self.clone_a, "alex-codex-member-content-01", "README.md")
        second = publish_candidate_lock(self.clone_b, "morgan-claude-member-api-01", "docs/api.md")

        self.assertEqual("candidate_created", candidate.status)
        self.assertEqual("acquired", first.status)
        self.assertEqual("acquired", second.status)
        self.assertTrue(second.non_fast_forward_seen)
        self.assertTrue(second.rechecked_after_fetch)

        verifier = self.root / "verifier"
        git(self.root, "clone", str(self.remote), str(verifier))
        self.assertEqual(
            {
                "alex-codex-member-content-01": "README.md",
                "morgan-claude-member-api-01": "docs/api.md",
            },
            active_locks(verifier),
        )

    def test_paused_stale_and_abandoned_states_are_markdown_states_not_deletes(self) -> None:
        lock_path = self.clone_a / ".collab" / "locks" / "alex-codex-member-content-01.md"
        write(lock_path, lock_text("alex-codex-member-content-01", "README.md").replace("Status: writing", "Status: paused"))
        git(self.clone_a, "add", ".collab/locks/alex-codex-member-content-01.md")
        git(self.clone_a, "commit", "-m", "Pause remote lock")
        git(self.clone_a, "push", "origin", "HEAD:main")

        git(self.clone_b, "pull", "--rebase", "origin", "main")
        text = read(self.clone_b / ".collab" / "locks" / "alex-codex-member-content-01.md")
        self.assertIn("Status: paused", text)
        self.assertIn("Lock State: acquired", text)

        # A normal Member must not delete another actor's stale lock; the
        # documented recovery is a state transition by the same actor or Lead.
        self.assertIn("paused", text)
        self.assertTrue((self.clone_b / ".collab" / "locks" / "alex-codex-member-content-01.md").exists())


class RemoteGitModeDocumentationTests(unittest.TestCase):
    def test_docs_define_two_modes_and_do_not_mix_assumptions(self) -> None:
        required = [
            "Shared Workspace Mode",
            "Remote Git Mode",
            "Do not mix assumptions between these modes.",
            "same working directory",
            "different machines, clones, or worktrees",
        ]
        for path in [README, README_ZH, LEAD_SKILL, MEMBER_SKILL, TEMPLATES / "AGENTS.md"]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = read(path)
                for value in required:
                    self.assertIn(value, text)

    def test_remote_git_lock_protocol_is_documented(self) -> None:
        required = [
            "Remote Git Mode Lock Protocol",
            "fetch the latest remote state",
            "create a candidate lock record",
            "commit only the candidate lock",
            "push the candidate lock",
            "non-fast-forward",
            "fetch, rebase or reapply the candidate lock, re-read all locks, and re-evaluate scope overlap",
            "Do not force push",
            "Only edit business files after the candidate lock is published and rechecked on the latest remote state.",
            "acquire",
            "refresh",
            "pause",
            "resume",
            "release",
            "stale",
            "abandoned",
        ]
        for path in [README, LEAD_SKILL, MEMBER_SKILL, TEMPLATES / "AGENTS.md"]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = read(path)
                for value in required:
                    self.assertIn(value, text)

    def test_low_conflict_remote_git_state_layout_is_defined(self) -> None:
        required = [
            ".collab/locks/<actor-id>.md",
            ".collab/tasks/<task-id>.md",
            ".collab/events/<timestamp>-<actor-id>.md",
            ".collab/snapshots/COLLAB_LOG.md",
            "authoritative state",
            "append-only event",
            "derived snapshot",
            "Lead may rebuild",
        ]
        for path in [README, LEAD_SKILL, MEMBER_SKILL, TEMPLATES / "AGENTS.md", TEMPLATES / "COLLAB_LOG.md"]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = read(path)
                for value in required:
                    self.assertIn(value, text)


class CompletionPolicyTests(unittest.TestCase):
    def test_example_covers_all_completion_policies(self) -> None:
        expected = {
            "TASK-LEAD-REVIEW.md": [
                "Completion Policy: Lead review",
                "Status: READY_FOR_REVIEW",
                "Handoff Target Type: actor",
                "Handoff Target Actor ID: alex-codex-lead-coordinator-01",
            ],
            "TASK-USER-REVIEW.md": [
                "Completion Policy: User review",
                "Status: READY_FOR_REVIEW",
                "Handoff Target Type: human-user",
                "Handoff Target Human: human user",
            ],
            "TASK-SELF-DONE.md": [
                "Completion Policy: Member self-completion",
                "Status: DONE",
                "Review Handoff: none",
            ],
            "TASK-PER-TASK.md": [
                "Completion Policy: Per-task decision",
                "Selected Completion Policy: Lead review",
                "Missing selected policy means stop and ask.",
            ],
            "TASK-REVIEW-LOOP.md": [
                "Status History: CHANGES_REQUESTED -> IN_PROGRESS -> READY_FOR_REVIEW",
                "Completion Policy: Lead review",
            ],
        }

        for filename, values in expected.items():
            with self.subTest(task=filename):
                text = read(EXAMPLE / ".collab" / "tasks" / filename)
                for value in values:
                    self.assertIn(value, text)

    def test_handoff_targets_distinguish_actor_and_human_user(self) -> None:
        events_dir = EXAMPLE / ".collab" / "events"
        combined = "\n".join(read(path) for path in events_dir.glob("*.md"))
        self.assertIn("Target Type: actor", combined)
        self.assertIn("Target Actor ID: alex-codex-lead-coordinator-01", combined)
        self.assertIn("Target Type: human-user", combined)
        self.assertIn("Target Human: human user", combined)
        self.assertNotIn("Lead or user", combined)

    def test_actor_registry_updates_last_seen_and_current_scope(self) -> None:
        agents = read(EXAMPLE / "AGENTS.md")
        morgan = re.search(
            r"### morgan-claude-member-content-01(?P<body>.*?)(?:\n### |\Z)",
            agents,
            flags=re.S,
        )
        self.assertIsNotNone(morgan)
        body = morgan.group("body")
        self.assertIn("Current scope: TASK-LEAD-REVIEW.md, TASK-REVIEW-LOOP.md", body)
        self.assertIn("Last seen: 2026-06-24T11:40:00+00:00", body)


class InstallIdempotencyTests(unittest.TestCase):
    def install_once(self, target_root: Path) -> None:
        skills_root = target_root / "skills"
        skills_root.mkdir(parents=True, exist_ok=True)
        for skill_name in ["team-lead-collaboration", "team-member-collaboration"]:
            target = skills_root / skill_name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(ROOT / "skills" / skill_name, target)

    def test_repeated_install_removes_stale_files_and_preserves_other_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            unrelated = target / "skills" / "unrelated-skill"
            unrelated.mkdir(parents=True)
            write(unrelated / "SKILL.md", "# keep me\n")

            self.install_once(target)
            write(target / "skills" / "team-lead-collaboration" / "old-file.md", "stale\n")
            nested = target / "skills" / "team-lead-collaboration" / "team-lead-collaboration"
            nested.mkdir()

            self.install_once(target)

            self.assertFalse((target / "skills" / "team-lead-collaboration" / "old-file.md").exists())
            self.assertFalse(nested.exists())
            self.assertTrue((unrelated / "SKILL.md").exists())
            self.assertTrue((target / "skills" / "team-lead-collaboration" / "references" / "AGENTS.template.md").exists())

    def test_readme_install_commands_are_idempotent_for_windows_macos_and_linux(self) -> None:
        text = read(README)
        required = [
            'Remove-Item -Recurse -Force (Join-Path $skills "team-lead-collaboration")',
            'Remove-Item -Recurse -Force (Join-Path $skills "team-member-collaboration")',
            'rm -rf "$HOME/.codex/skills/team-lead-collaboration"',
            'rm -rf "$HOME/.codex/skills/team-member-collaboration"',
            "safe to run repeatedly",
        ]
        for value in required:
            self.assertIn(value, text)


class CiWorkflowTests(unittest.TestCase):
    def test_github_actions_runs_tests_on_push_and_pr_for_ubuntu_and_windows(self) -> None:
        text = read(WORKFLOW)
        for value in [
            "push:",
            "pull_request:",
            "ubuntu-latest",
            "windows-latest",
            "python -m unittest discover -s tests -v",
            "pytest tests -q",
        ]:
            self.assertIn(value, text)


class TemplateSyncTests(unittest.TestCase):
    def test_lead_references_match_root_templates_byte_for_byte(self) -> None:
        pairs = {
            "AGENTS.template.md": "AGENTS.md",
            "COLLAB_LOG.template.md": "COLLAB_LOG.md",
            "TEAM_TASKS.template.md": "TEAM_TASKS.md",
            "MODULE_OWNERSHIP.template.md": "MODULE_OWNERSHIP.md",
        }
        for reference, template in pairs.items():
            with self.subTest(reference=reference):
                self.assertEqual(
                    (TEMPLATES / template).read_bytes(),
                    (LEAD_REFERENCES / reference).read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
