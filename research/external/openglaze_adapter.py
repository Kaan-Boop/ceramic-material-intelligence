"""Optional OpenGlaze comparison adapter.

This module never supplies the production chemistry result. It runs the
downloaded OpenGlaze CLI as an explicitly labelled external reference so that
convention or implementation differences can be reviewed before an adapter is
made part of the application service.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Mapping, Sequence


class OpenGlazeReferenceError(RuntimeError):
    """Raised when the optional OpenGlaze reference cannot be executed."""


def run_umf_reference(
    ingredients: Sequence[Mapping[str, float | int | str]],
    *,
    cone: int,
    repo_root: str | Path,
    python_executable: str,
    timeout_seconds: float = 20.0,
) -> dict:
    """Run OpenGlaze's UMF CLI and return its raw JSON reference report.

    Each ingredient requires ``name`` and ``amount``. The caller must retain
    the production engine's own report beside this reference report; this
    function intentionally does not merge or reinterpret the two.
    """

    if not ingredients:
        raise OpenGlazeReferenceError("EMPTY_REFERENCE_RECIPE")
    if not isinstance(cone, int) or cone == 0:
        raise OpenGlazeReferenceError("INVALID_CONE")
    root = Path(repo_root).resolve()
    if not (root / "openglaze_cli.py").is_file():
        raise OpenGlazeReferenceError(f"OPENGLAZE_NOT_FOUND: {root}")

    parts: list[str] = []
    for row in ingredients:
        name = str(row.get("name", "")).strip()
        amount = row.get("amount")
        if not name or not isinstance(amount, (int, float)) or amount <= 0:
            raise OpenGlazeReferenceError("INVALID_REFERENCE_INGREDIENT")
        parts.append(f"{name} {amount:g}")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
    command = [
        python_executable,
        "-m",
        "openglaze_cli",
        "umf",
        "--recipe",
        ", ".join(parts),
        "--cone",
        str(cone),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise OpenGlazeReferenceError("OPENGLAZE_EXECUTION_FAILED") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip()[-500:]
        raise OpenGlazeReferenceError(f"OPENGLAZE_EXIT_{completed.returncode}: {detail}")
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise OpenGlazeReferenceError("OPENGLAZE_INVALID_JSON") from exc
    if not isinstance(report, dict):
        raise OpenGlazeReferenceError("OPENGLAZE_INVALID_REPORT")
    return {
        "evidence_kind": "CALCULATED",
        "method_kind": "DETERMINISTIC_EXTERNAL_REFERENCE",
        "source": "OpenGlaze",
        "report": report,
        "limitations": [
            "Bu çıktı Ceramic Material Intelligence çekirdek sonucu değildir.",
            "OpenGlaze convention ve malzeme analizleri ayrıca doğrulanmalıdır.",
            "Gerçek test karosu olmadan yüzey veya gıda güvenliği doğrulanmaz.",
        ],
    }
