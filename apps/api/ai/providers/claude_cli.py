"""`claude -p` on the owner's subscription (decision ⑨, ADR-0065 § 2.2).

The method of `tg-solver` (`tgsolver/llm.py`), which has run this way since
2026-11: no tools, no MCP servers, no slash commands, no settings or memory,
no saved session; the answer comes back as JSON checked against a schema.
So text a student plants in a question can change the words of the answer
but cannot make the model act — there is nothing it could act with.

The process gets a minimal environment: the database URL and the Django
secret of the worker never reach it, and neither does an `ANTHROPIC_API_KEY`
(with one present the CLI would bill the API instead of the subscription).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from typing import Any

from ai.types import AIError, Config, Usage

NAME = "claude-cli"

SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"answer": {"type": "string"}},
    "required": ["answer"],
    "additionalProperties": False,
}

#: Passed through from the worker's environment; nothing else is.
_KEEP = (
    "PATH",
    "HOME",
    "USERPROFILE",
    "APPDATA",
    "LOCALAPPDATA",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "LANG",
)


def environment(config: Config) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k in _KEEP}
    env["DISABLE_AUTOUPDATER"] = "1"
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
    if config.oauth_token:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = config.oauth_token
    return env


def command(cli: str, model: str, prompt_file: str) -> list[str]:
    return [
        cli, "-p", "--model", model,
        "--tools", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        "--disable-slash-commands", "--no-session-persistence", "--setting-sources", "",
        "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
        # A file, not an argument: Windows caps a command line at 32 767 characters.
        "--system-prompt-file", prompt_file,
        "--json-schema", json.dumps(SCHEMA),
    ]  # fmt: skip


def _result(stdout: str) -> dict[str, Any] | None:
    result = None
    for line in stdout.splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("type") == "result":
            result = obj
    return result


def complete(model: str, system: str, text: str, config: Config) -> tuple[str, Usage]:
    cli = config.cli_path or shutil.which("claude") or ""
    if not cli:
        raise AIError("unavailable", "claude CLI not found")
    message = {
        "type": "user",
        "message": {"role": "user", "content": [{"type": "text", "text": text}]},
    }
    fd, prompt_file = tempfile.mkstemp(prefix="rw_tutor_", suffix=".md")
    started = time.monotonic()
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(system)
        proc = subprocess.run(
            command(cli, model, prompt_file),
            input=json.dumps(message) + "\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=config.timeout_s,
            env=environment(config),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired:
        raise AIError("timeout", f"{model}: no answer in {config.timeout_s}s") from None
    except OSError as exc:
        raise AIError("unavailable", str(exc)) from None
    finally:
        try:
            os.remove(prompt_file)
        except OSError:
            pass
    latency = int((time.monotonic() - started) * 1000)
    result = _result(proc.stdout)
    if result is None:
        raise AIError("failed", f"{model}: no result (rc={proc.returncode}) {proc.stderr[:300]}")
    raw = result.get("usage") or {}
    usage = Usage(
        input_tokens=int(raw.get("input_tokens") or 0),
        output_tokens=int(raw.get("output_tokens") or 0),
        cache_read_tokens=int(raw.get("cache_read_input_tokens") or 0),
        cache_write_tokens=int(raw.get("cache_creation_input_tokens") or 0),
        cost_usd=float(result.get("total_cost_usd") or 0),
        latency_ms=latency,
    )
    output = result.get("structured_output")
    if result.get("is_error") or not isinstance(output, dict):
        message_text = str(result.get("result") or "")
        lowered = message_text.lower()
        if "limit" in lowered:
            code = "busy"  # the subscription's 5-hour window: «… usage limit reached …»
        elif "not logged in" in lowered or "/login" in lowered:
            code = "unavailable"  # no token in this container (measured in the `ai` image)
        else:
            code = "failed"
        raise AIError(code, f"{model}: {message_text[:300]}")
    answer = output.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise AIError("failed", f"{model}: empty answer")
    return answer.strip(), usage
