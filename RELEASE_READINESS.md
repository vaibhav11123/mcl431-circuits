# Release readiness

Date: 2026-11-26 IST.

## Verdict

**Core compiler and zero-spend workspace: ready to use locally.**

**Public ChatGPT/Claude directory: not ready** until a human hosts a stable `https://…/mcp` origin. Local MCP is not directory eligibility.

**Fly: SKIPPED_OPTIONAL.** Not deployed. Do not list it as a completed hosting milestone.

## Phase D checks

| Check | Result | Command / path |
| --- | --- | --- |
| CLI draw fail-closed | yes | `python3 -m circuit draw examples/iso_sequence/circuit.yaml`; `--unverified` watermarks |
| Workspace ISO draw | Pyodide zip present | `web/app.js` + `web/circuit-iso.zip`; `tests/test_pyodide_bundle.py` |
| CLI ↔ workspace parity | ISO pack only | lecture goldens are CLI/course-pack; public workspace is ISO |
| Deterministic ISO graph | locked | `tests/test_pyodide_bundle.py` hash `a2db286f342329af9595cb8d933fc11ab65bdf194931b4571e3f60fb8a9c06f6` |
| Verification evidence | independent traces | `spec_trace` vs `env_trace`; `circuit verify` manifest |
| Native vs browser | zip synced this turn | `python3 scripts/sync_web_circuit.py` |
| Diagnostics | English sentences | `service.sentence_for`; dual-solenoid and deadlock FAIL not PASS |
| Supply chain | ranges, no lockfile | `pyproject.toml`; pip-audit not run |
| Docs | self-host + submission | `docs/self-hosting.md`, `plugin/SUBMISSION.md` |
| Onboarding | three commands | `README.md` |
| Zero mandatory hosting spend | yes | Fly unused; static `web/`; stdio MCP |
| UI | engineering, not a chatbot skin | `web/index.html` |

## Go / no-go

| Channel | Go? |
| --- | --- |
| GitHub repo + CLI | go |
| GitHub Pages / any static host for `web/` | go (Pyodide; jsDelivr) |
| Cursor / Claude Desktop stdio MCP | go (`plugin/mcp.stdio.json`) |
| Loopback `python -m circuit.mcp_server --http` | go |
| OpenAI plugin directory | **no-go** until public HTTPS + human submit |
| Anthropic connector directory | **no-go** until public HTTPS + paid Claude plan (human) + submit |
| “Hosted on Fly” announcement | **no-go** |
