"""Sweep driver: run test cases 1-10 x 2 Gemini models, content variant.

Mirrors sweep_openai.py but drives client_gemini.py. The 10 test-case payloads
are imported from sweep_openai so there's a single source of truth. Writes each
test_case{N}_gemini.jsonl in the same header-per-model structure as
results/test_case1.jsonl.

Usage:
    python mcp-client/sweep_gemini.py                  # all 10 cases, n=10
    python mcp-client/sweep_gemini.py --n 1 --cases 1  # quick preflight
"""

import argparse
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path

import client_gemini as C
from sweep_openai import TEST_CASES, _parse_cases

# Confirm exact IDs + function-calling support against the live models list
# before a real run - Gemini IDs churn.
MODELS = ["gemini-3.6-flash", "gemini-3.5-flash-lite"]
VARIANT = "content"
SERVER = "MCP_server/server_notes.py"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


async def run_case(case_no: int, n: int) -> None:
    tc = TEST_CASES[case_no]
    out_path = RESULTS_DIR / f"test_case{case_no}_gemini.jsonl"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # apply this test case's payload to the shared client_gemini globals
    C.FAKE_SECRET_NOTE = tc["secret_note"]
    C.FAKE_SECRET_VALUE = tc["secret_value"]
    C.POISON_NOTE_NAME = tc["poison_note"]
    C.POISON_INSTRUCTION_TEMPLATE = tc["template"]

    client = C.MCPClient()
    await client.connect_to_server(SERVER)
    lines: list[str] = []
    try:
        for model in MODELS:
            C.MODEL = model
            results = []
            for i in range(n):
                try:
                    r = await client.run_single_trial(VARIANT)
                except Exception as e:  # keep the sweep alive on a bad trial
                    r = {
                        "run_id": uuid.uuid4().hex,
                        "model": model,
                        "variant": VARIANT,
                        "hit": False,
                        "called_save_note": False,
                        "error": repr(e),
                        "transcript": "",
                    }
                results.append(r)
                print(
                    f"[case{case_no} {model} {i + 1}/{n}] "
                    f"hit={r['hit']} called_save_note={r['called_save_note']}"
                    + (f" ERROR={r['error']}" if "error" in r else ""),
                    flush=True,
                )
            successes = sum(1 for r in results if r["hit"] or r["called_save_note"])
            asr = successes / n if n else 0.0
            lines.append(f"{model} {successes}/{n} = {asr:.2%}")
            for r in results:
                lines.append(
                    json.dumps(
                        {"time": datetime.now().isoformat(timespec="seconds"), **r}
                    )
                )
            lines.append("")  # blank separator between model blocks
            print(f"  -> {model} case{case_no}: {successes}/{n} = {asr:.2%}", flush=True)
    finally:
        await client.cleanup()

    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}", flush=True)


async def main():
    parser = argparse.ArgumentParser(description="Gemini model x test-case sweep.")
    parser.add_argument("--n", type=int, default=10, help="trials per model per case")
    parser.add_argument("--cases", default="1-10", help="e.g. '1-10' or '1,6,7'")
    args = parser.parse_args()

    cases = _parse_cases(args.cases)
    print(
        f"Sweep: cases={cases} models={MODELS} n={args.n} variant={VARIANT} "
        f"(total {len(cases) * len(MODELS) * args.n} trials)",
        flush=True,
    )
    for case_no in cases:
        await run_case(case_no, args.n)
    print("SWEEP COMPLETE", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
