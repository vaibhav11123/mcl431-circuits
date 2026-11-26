# Sequence Circuit — completion audit

Audit date: 2026-11-26 IST. Auditor: coding agent on this repository. Tracker labels in `docs/product-execution-plan.md` were **not** trusted without a command or a file.

## What this audit re-ran

| Command | Result (this VM, 2026-11-26 IST) |
| --- | --- |
| `python3 -m pytest -q` | **238 passed, 2 skipped** (this tree after merge + distribution tests) |
| `python3 -m circuit eval --goldens` | exit 0 |
| `python3 -m circuit bench benchmarks/sequencebench` | n=30, `accepted_error_rate` 0.0, `reject_invalid_rate` 1.0 |
| `python3 -m circuit bench --suite 300` | n=300, fingerprint `c502bcc32db7a8803669a257821679e0a4033a36414eb6fee3a0a2226d4ec5bf`, `accepted_error_rate` 0.0, `reject_invalid_rate` 1.0 |
| `python3 -m circuit bench --suite llm` | n=12, `compiler_match_rate` 1.0, `naive_match_rate` 0.333…, `compiler_reject_invalid_rate` 1.0, `naive_accept_invalid_rate` 1.0, `paid_api_calls` 0 |
| `python3 -m circuit draw examples/iso_sequence/circuit.yaml` | exit 0, sheets under `output/iso_sequence/` |
| `python3 -m json.tool plugin/plugin.json` and `plugin/mcp.json` | exit 0 |
| Fly deploy | **not run** |

`python3 -m venv` on this VM failed (`ensurepip` / `python3-venv` missing). No package was installed with apt. Clean-venv is an evidenced blocker, not a hidden pass. Editable install `pip install -e ".[dev]"` on this user site succeeded.

## T29 — SKIPPED_OPTIONAL (not deployed)

Fly.io was optional in the plan. It is **not** live. It is **not** a successful deploy.

Justification: CLI, SequenceBench, goldens, stdio MCP, loopback HTTP MCP, and the static Pyodide workspace in `web/` do not import Fly, `FLY_API_TOKEN`, or `fly.io`. Tests: `tests/test_fly_independence.py`. Self-host: `docs/self-hosting.md`.

Do not tell a reviewer that Sequence Circuit is hosted on Fly.

## T0–T57 vs this tree

Closed with supporting files and tests in-tree (spot-checked this turn, not every historical Inspector/Docker live row re-executed):

- Pack/hooks/ISO vectors: `src/circuit/pack.py`, `src/circuit/packs/iso_sequence/`
- Fail-closed API: `src/circuit/service.py` `draw_yaml`
- MCP: `src/circuit/mcp_server.py` + `tests/test_mcp_server.py` (titles + annotation hints this turn)
- Workspace: `web/index.html`, `web/app.js`, `web/circuit-iso.zip` (Pyodide 314; no Fly URL)
- IR + oracles: `src/circuit/ir/`, `src/circuit/semantics/spec_trace.py`, `env_trace.py`, `src/circuit/verification/refine.py`
- Status lattice: `src/circuit/verification/status.py`
- SequenceBench v0: `benchmarks/sequencebench/`
- Mutations: `tests/test_mutations.py`, `tests/test_planted_miscompile.py`

**This turn added independent TIMER ticks, deadlock FAIL, cascade electrical check (fluid topology still NOT_EVALUATED), SequenceBench-300, SequenceBench-LLM fixtures, distribution package, handover docs.**

**Not re-executed this audit:** Docker `:8766` live, MCP Inspector HTTP against a running server, Fly, ChatGPT/Claude login, directory submit, student study.

## Incomplete / not claimed

| Item | Status | Evidence |
| --- | --- | --- |
| Fly hosted URL | SKIPPED_OPTIONAL | no token; not deployed |
| ChatGPT/Claude directory | blocked | needs public HTTPS; human login |
| Live LLM SequenceBench | not run | fixtures only; `paid_api_calls` 0 |
| Student study | protocol only | `docs/user-study.md` — no fabricated n= |
| Physics / pressure | unsupported / not evaluated | `PS`/`PRESSURE` → `UNSUPPORTED`; `PHY001` never PASS |
| Cascade group-line fluid | NOT_EVALUATED | G valves structural; `env_trace` is electrical |
| Multi-cycle sequences that visit rest mid-way | not independently verified | `env_trace` stops at first return to rest |
| Clean `python3 -m venv` | blocked on this VM | `ensurepip` missing |
| pip-audit / lockfile | not present | `pyproject.toml` ranges only |

## Mandatory spend

None authorized. No Fly, no OpenAI/Anthropic API, no directory fee.
