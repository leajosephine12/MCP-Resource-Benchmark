# MCP Resource Injection Benchmark

A full, local end-to-end setup to evaluate the attack surface of **MCP servers**
through **resource injection**, which indirect prompt injection delivered via an MCP
server's resource *content* and *metadata*.

A poisoned resource instructs the model to exfiltrate a planted (fake) secret to
a local canary listener. A trial counts as a **hit** when the model actually
makes that call. Everything runs locally on fake data, so no real secrets, and no
external targets.

## Models / clients

| Provider | Client |
|---|---|
| Anthropic (Claude) | `mcp-client/client_anthropic.py` |
| OpenAI (GPT) | `mcp-client/client_openai.py` |
| Google (Gemini, via OpenAI-compatible endpoint) | `mcp-client/client_gemini.py` |
| Mistral AI (Mistral, via OpenAI-compatible endpoint) | `mcp-client/client_mistral.py` |

## Injection channels

- **`content`** — payload in the note/resource body
- **`description`** — payload in the resource description (metadata)
- **`mimetype`** — payload in the resource `mimeType` (metadata)

## Layout

- `MCP_server/` — the notes MCP server under test
- `mcp-client/` — model clients + sweep drivers (`sweep_*.py`, `test_cases_sweep.py`)
- `listener/` — Flask canary listener that records exfiltration hits
- `research_tools/` — test-case definitions and the proof-of-concept
- `results/` — per-test-case trial logs (JSONL)

## Quick start

```bash
# 0. install dependencies
pip install -r requirements.txt

# 1. put your API keys in mcp-client/.env
#    ANTHROPIC_API_KEY=... / OPENAI_API_KEY=... / GEMINI_API_KEY=... / MISTRAL_API_KEY=...

# 2. start the canary listener (from inside listener/)
cd listener && python flask_listener.py

# 3. run a single client for example openai 
python mcp-client/client_openai.py MCP_server/server_notes.py --variant content --n 10
```

## Sweeps

A sweep runs all 10 test cases across every model for one provider and writes
`results/test_case{N}_{provider}.jsonl`. Run from the repo root with the listener
up and the provider's API key in `mcp-client/.env`:

```bash
python mcp-client/sweep_openai.py                 # all 10 cases, n=10
python mcp-client/sweep_gemini.py
python mcp-client/sweep_mistral.py

python mcp-client/sweep_mistral.py --n 1 --cases 1     # quick preflight
python mcp-client/sweep_mistral.py --cases 1,6,7       # subset of cases
```

Edit the `MODELS` list at the top of each `sweep_*.py` to pick which models to
run (some models require a paid provider tier).

---
*Work in progress: sections on methodology, metrics (ASR), and results to follow.*
