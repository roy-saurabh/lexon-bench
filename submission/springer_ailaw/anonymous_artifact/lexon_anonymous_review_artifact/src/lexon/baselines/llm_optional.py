"""
B5 — Optional LLM Baseline (disabled by default).

This module is a STUB.  It is disabled unless both of the following are provided:
  1. CLI flag --run-llm-baseline
  2. Environment variable LEXON_LLM_API_KEY (and optionally LEXON_LLM_MODEL)

If not executed, this experiment does NOT appear in any paper-ready table or
main results file.  The execution status is written to:
  outputs/audit/llm_baseline_status.json

Rationale (§2.9 of the paper): an LLM comparison is not informative without a
fixed-prompt, fixed-model-version, fixed-temperature reproducible protocol.
A controlled LLM comparison is deferred to future work.

If you run this baseline, you accept responsibility for:
  - API costs
  - Non-determinism of LLM outputs (results will not be reproducible across runs)
  - Prompt engineering choices that affect outcomes

The module documents a minimal protocol that, if followed, produces a
comparable (though still non-deterministic) baseline.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


LLM_DISABLED_SENTINEL = "llm_baseline_not_executed"

LLM_AUDIT_PATH = Path("outputs/audit/llm_baseline_status.json")


def is_llm_enabled() -> bool:
    """Return True only if both the API key and explicit flag are provided."""
    key_set = bool(os.environ.get("LEXON_LLM_API_KEY", "").strip())
    flag_set = os.environ.get("LEXON_RUN_LLM_BASELINE", "").lower() in ("1", "true", "yes")
    return key_set and flag_set


def write_audit_status(executed: bool, notes: str = "") -> None:
    """Write LLM baseline execution status to audit file."""
    LLM_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    status = {
        "llm_baseline_executed": executed,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "notes": notes or (
            "LLM baseline was not executed. "
            "Set LEXON_LLM_API_KEY and LEXON_RUN_LLM_BASELINE=1 to enable. "
            "Results from this baseline are NOT included in any main results table."
        ),
        "status": "executed" if executed else LLM_DISABLED_SENTINEL,
    }
    with open(LLM_AUDIT_PATH, "w") as f:
        json.dump(status, f, indent=2)


def run_llm_baseline_if_enabled() -> dict:
    """
    Attempt to run the LLM baseline.

    If disabled (default), writes an audit record and returns an empty dict.
    Never raises; callers can check the returned dict for 'executed' key.
    """
    if not is_llm_enabled():
        write_audit_status(executed=False)
        return {"executed": False, "status": LLM_DISABLED_SENTINEL}

    # --- Execution path (requires LEXON_LLM_API_KEY + flag) ---
    try:
        return _execute_llm_baseline()
    except Exception as exc:
        write_audit_status(executed=False, notes=f"Execution failed: {exc}")
        return {"executed": False, "error": str(exc)}


def _execute_llm_baseline() -> dict:
    """
    Minimal reproducible LLM baseline protocol.

    Requirements for a comparable experiment:
    - Fixed prompt template (see PROMPT_TEMPLATE below)
    - Fixed model: LEXON_LLM_MODEL env var (e.g. gpt-4o-2024-08-06)
    - Fixed temperature: 0.0
    - Fixed seed: LEXON_LLM_SEED env var (default 42)
    - Batch mode to avoid rate-limit variability
    """
    import importlib.util

    if importlib.util.find_spec("openai") is None and importlib.util.find_spec("anthropic") is None:
        raise ImportError(
            "No LLM SDK found. Install openai or anthropic to run the LLM baseline."
        )

    model = os.environ.get("LEXON_LLM_MODEL", "gpt-4o-2024-08-06")
    seed = int(os.environ.get("LEXON_LLM_SEED", "42"))
    notes = f"Model={model}, seed={seed}, temperature=0.0"
    write_audit_status(executed=True, notes=notes)
    # Full implementation left to future work (§4.2 / §2.9).
    raise NotImplementedError(
        "Full LLM baseline implementation is deferred to future work. "
        "See §2.9 and §4.2 of the paper."
    )


PROMPT_TEMPLATE = """
You are an AI regulatory compliance assistant. Given an obligation description and
an AI system profile, determine whether the obligation APPLIES to the system.

Obligation:
{obligation_text}

System profile:
{profile_json}

Answer with exactly one of: APPLICABLE / NOT_APPLICABLE / UNCERTAIN
Reasoning (max 3 sentences):
"""
