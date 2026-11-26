# Known limitations

These are product facts. Closing a tracker row does not remove them.

## Semantics

1. **One cycle.** `env_trace` presses START from rest and stops at the first return to rest. A sequence that visits rest in the middle (A+ A- then B+ B-) is not independently verified. SequenceBench-300 accept cases are filtered to one-cycle walks. SequenceBench v0 case_17 was rewritten so TIMER does not straddle an intermediate rest.
2. **TIMER is discrete.** `T1_3s` means three environment steps with the coil on, not 3.000 seconds of wall time.
3. **Cascade fluid topology is not verified.** Extra `G1`… valves are added. Electrical step-memory is checked. Group-line pneumatics are `NOT_EVALUATED`.
4. **Pressure waits are UNSUPPORTED.** `PS` / `PRESSURE` do not PASS.
5. **No physics.** Pressure drop, leakage, force, and temperature are refused or `NOT_EVALUATED`. A PASS is not a safety certificate.
6. **Mutex is bounded.** Truncation is `INCONCLUSIVE`, never PASS.

## Product

7. **Fly is not deployed.** T29 is SKIPPED_OPTIONAL.
8. **Directory plugins are not listed.** Placeholder URL `https://REPLACE_ON_DEPLOY/mcp`.
9. **SequenceBench-LLM does not call a model.** Fixtures only. `paid_api_calls` is always 0.
10. **Student study has no results.** Template only.
11. **Public workspace is the ISO pack.** Lecture crops do not ship. Course goldens remain CLI + lecture pack.
12. **No lockfile.** `pyproject.toml` uses version ranges. pip-audit was not run this audit.
13. **Clean venv on this audit VM** failed (`python3-venv` / ensurepip missing).
14. **Pyodide workspace** needs jsDelivr at runtime for the interpreter. The compiler zip is local. Offline air-gap is not claimed.
15. **MCP draw rate** is 30 draws/hour/peer in-process. Not a production SLA.

## Do not report as verified

Physics, pressure, cascade group-line flow, wall-clock timing, directory approval, Fly uptime, LLM-as-a-service quality, student learning gains.
