# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/shell.py
============
Unitary Operating System — AI-Powered Intent Shell

The UOS shell is not a command-line interpreter — it is an **intent engine**.
The user expresses *what they want* (their intent); the shell resolves the
most geodesically aligned process or filesystem operation and executes it.

This replaces the classical:
    user types: ls -la /tmp
    shell parses: command="ls", flags=["-la"], args=["/tmp"]

with:
    user expresses: "list files in the temp directory"
    intent engine resolves: Intent(action=LIST, resource="tmp", detail=True)
    manifold routes: to the HolographicFilesystem.list_files() geodesic

Shell Concepts
--------------
Intent
    A structured, language-agnostic description of what the user wants.
    Parsed from natural language or a structured command mini-language.

IntentParser
    Converts a raw string into an Intent using keyword pattern matching
    and manifold affinity scoring.

ShellCommand
    A resolved, executable shell command with a manifold address.

UOSShell
    The main shell object.  Maintains session state, history, environment
    variables, and the intent→command resolution pipeline.

CommandResult
    The result of executing a shell command.

History
    A ring buffer of the last K_CS=74 commands, stored at their manifold
    coordinates for geodesic recall.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

import re
import hashlib
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Deque, Dict, List, Optional

import numpy as np

from UOS.constants import (
    K_CS, WINDING_NUMBER, PHI_BACKGROUND, INVARIANT_RATIO, BRAIDED_SOUND_SPEED,
)

# Shell constants
HISTORY_CAPACITY: int = K_CS           # 74 commands in history ring
MAX_INTENT_TOKENS: int = 128           # max tokens per intent string
ENV_SIZE: int = K_CS * WINDING_NUMBER  # = 370 env vars max


# ===========================================================================
# Enumerations
# ===========================================================================

class IntentAction(Enum):
    """Canonical action classes recognised by the intent parser."""
    LIST        = auto()   # list files, processes, devices, languages…
    READ        = auto()   # read / cat / show a file or resource
    WRITE       = auto()   # write / create / store
    DELETE      = auto()   # remove / destroy
    EXECUTE     = auto()   # run / launch / start
    STOP        = auto()   # kill / terminate / halt
    SEARCH      = auto()   # find / grep / locate
    COMPILE     = auto()   # build / compile / transpile
    NETWORK     = auto()   # connect / ping / route / send
    SECURITY    = auto()   # verify / sign / encrypt / audit
    STATUS      = auto()   # report / stat / info / health
    HELP        = auto()   # help / man / ?
    UNKNOWN     = auto()   # could not be resolved


class IntentConfidence(Enum):
    HIGH   = "high"
    MEDIUM = "medium"
    LOW    = "low"


# ===========================================================================
# Intent
# ===========================================================================

@dataclass
class Intent:
    """A structured, resolved user intent.

    Parameters
    ----------
    raw : str
        The original raw string the user entered.
    action : IntentAction
    resource : str
        The primary resource (file path, PID, language name, etc.).
    modifiers : list of str
        Additional qualifiers (flags, options).
    confidence : IntentConfidence
    phi_coord : float
        Manifold coordinate of this intent (for history recall).
    """
    raw: str
    action: IntentAction
    resource: str = ""
    modifiers: List[str] = field(default_factory=list)
    confidence: IntentConfidence = IntentConfidence.MEDIUM
    phi_coord: float = 0.0

    def __post_init__(self) -> None:
        if self.phi_coord == 0.0:
            self.phi_coord = self._compute_phi()

    def _compute_phi(self) -> float:
        raw = self.raw.encode()
        arr = np.frombuffer(raw, dtype=np.uint8).astype(np.int64)
        return float(int(np.sum(arr ** 2)) % K_CS) / K_CS

    def is_confident(self) -> bool:
        return self.confidence == IntentConfidence.HIGH

    def __str__(self) -> str:
        return (
            f"Intent({self.action.name} '{self.resource}' "
            f"[{', '.join(self.modifiers)}] conf={self.confidence.value})"
        )


# ===========================================================================
# IntentParser
# ===========================================================================

# Keyword → action mapping (ordered: first match wins)
_INTENT_PATTERNS: List = [
    # (action, list-of-trigger-keywords)
    (IntentAction.LIST,    ["list", "ls", "dir", "show", "enumerate", "display"]),
    (IntentAction.READ,    ["read", "cat", "open", "view", "print", "output", "get"]),
    (IntentAction.WRITE,   ["write", "save", "store", "create", "make", "touch", "put"]),
    (IntentAction.DELETE,  ["delete", "remove", "rm", "erase", "drop", "destroy", "unlink"]),
    (IntentAction.EXECUTE, ["run", "exec", "execute", "launch", "start", "boot", "invoke"]),
    (IntentAction.STOP,    ["stop", "kill", "terminate", "halt", "quit", "exit", "end"]),
    (IntentAction.SEARCH,  ["search", "find", "locate", "grep", "query", "lookup", "scan"]),
    (IntentAction.COMPILE, ["compile", "build", "make", "transpile", "assemble", "link"]),
    (IntentAction.NETWORK, ["connect", "ping", "route", "send", "receive", "socket", "network"]),
    (IntentAction.SECURITY,["verify", "sign", "encrypt", "decrypt", "auth", "audit", "secure"]),
    (IntentAction.STATUS,  ["status", "stat", "info", "health", "report", "check", "monitor"]),
    (IntentAction.HELP,    ["help", "man", "manual", "?", "howto", "explain", "what"]),
]

# Words that should be treated as resource qualifiers, not resource names
_STOP_WORDS = {"the", "a", "an", "in", "of", "for", "to", "from", "with", "at", "on", "all"}


class IntentParser:
    """Converts a raw string into a structured Intent.

    Uses keyword pattern matching and manifold affinity scoring.

    Examples
    --------
    >>> parser = IntentParser()
    >>> intent = parser.parse("list all files in the temp folder")
    >>> intent.action
    <IntentAction.LIST: 1>
    >>> intent.resource
    'files'
    """

    def parse(self, raw: str) -> Intent:
        """Parse a raw string into an Intent.

        Parameters
        ----------
        raw : str

        Returns
        -------
        Intent
        """
        tokens = raw.strip().lower().split()[:MAX_INTENT_TOKENS]
        action, confidence = self._match_action(tokens)
        resource, modifiers = self._extract_resource_and_modifiers(tokens, action)
        return Intent(
            raw=raw,
            action=action,
            resource=resource,
            modifiers=modifiers,
            confidence=confidence,
        )

    def _match_action(
        self, tokens: List[str]
    ) -> tuple:
        """Return (action, confidence) from tokens."""
        # Exact keyword match in first 3 tokens → HIGH
        for action, keywords in _INTENT_PATTERNS:
            for tok in tokens[:3]:
                if tok in keywords:
                    return action, IntentConfidence.HIGH

        # Partial match anywhere → MEDIUM
        for action, keywords in _INTENT_PATTERNS:
            for tok in tokens:
                for kw in keywords:
                    if kw in tok or tok in kw:
                        return action, IntentConfidence.MEDIUM

        return IntentAction.UNKNOWN, IntentConfidence.LOW

    @staticmethod
    def _extract_resource_and_modifiers(
        tokens: List[str], action: IntentAction
    ):
        """Extract the primary resource and modifier list."""
        # Remove action keywords and stop words to find resource
        action_kws = set()
        for act, kws in _INTENT_PATTERNS:
            if act == action:
                action_kws.update(kws)
                break

        resource_candidates = [
            t for t in tokens
            if t not in action_kws and t not in _STOP_WORDS
            and not t.startswith("-")
        ]
        resource = resource_candidates[0] if resource_candidates else ""
        modifiers = [t for t in tokens if t.startswith("-")]
        return resource, modifiers


# ===========================================================================
# ShellCommand
# ===========================================================================

@dataclass
class ShellCommand:
    """A resolved, executable shell command.

    Parameters
    ----------
    intent : Intent
    handler : callable
        A zero-argument callable that executes the command.
    description : str
    """
    intent: Intent
    handler: Callable[[], Any]
    description: str = ""

    def execute(self) -> "CommandResult":
        """Execute the command and return a CommandResult."""
        try:
            output = self.handler()
            return CommandResult(
                command=self,
                success=True,
                output=output,
                exit_code=0,
            )
        except Exception as exc:
            return CommandResult(
                command=self,
                success=False,
                output=None,
                exit_code=1,
                error=str(exc),
            )


# ===========================================================================
# CommandResult
# ===========================================================================

@dataclass
class CommandResult:
    """The result of executing a ShellCommand."""
    command: ShellCommand
    success: bool
    output: Any
    exit_code: int = 0
    error: str = ""

    def __str__(self) -> str:
        if self.success:
            return f"[OK] {self.output}"
        return f"[ERR {self.exit_code}] {self.error}"


# ===========================================================================
# UOSShell
# ===========================================================================

class UOSShell:
    """The UOS AI-powered intent shell.

    Maintains session state, environment variables, command history, and
    the intent→command pipeline.

    Parameters
    ----------
    session_id : str
    pid : int
        PID of the shell process.

    Examples
    --------
    >>> shell = UOSShell(session_id="tty0", pid=1)
    >>> shell.setenv("HOME", "/manifold/home/root")
    >>> result = shell.eval("list all files")
    >>> result.success
    True
    >>> shell.history_entries()[-1].action
    <IntentAction.LIST: 1>
    """

    def __init__(self, session_id: str = "tty0", pid: int = 1) -> None:
        self.session_id = session_id
        self.pid = pid
        self.parser = IntentParser()
        self._env: Dict[str, str] = {
            "SHELL": "uos-shell",
            "TERM": "manifold-256color",
            "HOME": f"/manifold/home/{session_id}",
            "PATH": "/manifold/bin:/manifold/usr/bin",
            "PS1": f"UOS[{session_id}]$ ",
            "WINDING_NUMBER": str(WINDING_NUMBER),
            "K_CS": str(K_CS),
            "PHI_BACKGROUND": str(PHI_BACKGROUND),
        }
        self._history: Deque[Intent] = deque(maxlen=HISTORY_CAPACITY)
        self._handlers: Dict[IntentAction, Callable] = {}
        self._tick: int = 0
        self._register_default_handlers()

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------

    def setenv(self, key: str, value: str) -> None:
        """Set an environment variable."""
        if len(self._env) >= ENV_SIZE:
            raise OverflowError("Environment variable limit reached.")
        self._env[key] = value

    def getenv(self, key: str, default: str = "") -> str:
        """Get an environment variable."""
        return self._env.get(key, default)

    def unsetenv(self, key: str) -> None:
        """Unset an environment variable."""
        self._env.pop(key, None)

    def env(self) -> Dict[str, str]:
        """Return a copy of the current environment."""
        return dict(self._env)

    # ------------------------------------------------------------------
    # Intent evaluation
    # ------------------------------------------------------------------

    def eval(self, raw: str) -> CommandResult:
        """Parse, resolve, and execute a raw intent string.

        Parameters
        ----------
        raw : str

        Returns
        -------
        CommandResult
        """
        intent = self.parser.parse(raw)
        self._history.append(intent)
        self._tick += 1

        handler = self._handlers.get(intent.action)
        if handler is None:
            return CommandResult(
                command=ShellCommand(intent=intent, handler=lambda: None,
                                     description="(no handler)"),
                success=False,
                output=None,
                exit_code=127,
                error=f"No handler for action {intent.action.name}.",
            )
        cmd = ShellCommand(
            intent=intent,
            handler=lambda h=handler, i=intent: h(i),
            description=f"Handler for {intent.action.name}",
        )
        return cmd.execute()

    # ------------------------------------------------------------------
    # Handler registration
    # ------------------------------------------------------------------

    def register_handler(
        self, action: IntentAction, handler: Callable[[Intent], Any]
    ) -> None:
        """Register a custom handler for an intent action.

        Parameters
        ----------
        action : IntentAction
        handler : callable
            Called with the Intent as the sole argument.
        """
        self._handlers[action] = handler

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def history_entries(self) -> List[Intent]:
        """Return the history as a list (oldest first)."""
        return list(self._history)

    def recall(self, n: int = 1) -> Optional[Intent]:
        """Return the n-th most recent intent (1 = last)."""
        hist = list(self._history)
        if n < 1 or n > len(hist):
            return None
        return hist[-n]

    def geodesic_recall(self, phi_target: float, tol: float = 0.1) -> List[Intent]:
        """Return all history entries near ``phi_target`` on the manifold."""
        return [i for i in self._history if abs(i.phi_coord - phi_target) < tol]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def stats(self) -> Dict:
        return {
            "session_id": self.session_id,
            "pid": self.pid,
            "tick": self._tick,
            "history_depth": len(self._history),
            "env_vars": len(self._env),
            "registered_handlers": len(self._handlers),
        }

    # ------------------------------------------------------------------
    # Default handlers
    # ------------------------------------------------------------------

    def _register_default_handlers(self) -> None:
        self._handlers[IntentAction.STATUS] = lambda i: {
            "session": self.session_id,
            "tick": self._tick,
            "env_vars": len(self._env),
            "history": len(self._history),
        }
        self._handlers[IntentAction.HELP] = lambda i: (
            "UOS Intent Shell — express what you want, the manifold will resolve it.\n"
            "Actions: " + ", ".join(a.name for a in IntentAction if a != IntentAction.UNKNOWN)
        )
        self._handlers[IntentAction.LIST] = lambda i: list(self._env.keys())
        self._handlers[IntentAction.UNKNOWN] = lambda i: (
            f"Intent '{i.raw}' could not be resolved. Try: help"
        )
