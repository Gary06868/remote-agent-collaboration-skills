from __future__ import annotations


class CollabError(Exception):
    """Structured CLI error with a stable machine-readable code."""

    def __init__(self, code: str, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        return {"ok": False, "error": self.code, "message": self.message, "details": self.details}


ROLE_SELECTION_REQUIRED = "ROLE_SELECTION_REQUIRED"
MULTIPLE_ROLES_SELECTED = "MULTIPLE_ROLES_SELECTED"
ROLE_SESSION_CONFLICT = "ROLE_SESSION_CONFLICT"
ROLE_NOT_AUTHORIZED = "ROLE_NOT_AUTHORIZED"
SESSION_ALREADY_CLOSED = "SESSION_ALREADY_CLOSED"
SESSION_CONTEXT_MISSING = "SESSION_CONTEXT_MISSING"
PROJECT_NOT_INITIALIZED = "PROJECT_NOT_INITIALIZED"
ACTOR_NOT_REGISTERED = "ACTOR_NOT_REGISTERED"
MODULE_NOT_AUTHORIZED = "MODULE_NOT_AUTHORIZED"
PATH_NOT_AUTHORIZED = "PATH_NOT_AUTHORIZED"
STATE_TRANSITION_DENIED = "STATE_TRANSITION_DENIED"
GIT_PREFLIGHT_FAILED = "GIT_PREFLIGHT_FAILED"
CRITICAL_ANNOUNCEMENT_UNACKED = "CRITICAL_ANNOUNCEMENT_UNACKED"
