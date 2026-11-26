# Next milestones

Not this release. Do not stub them as PASS.

## P0 — keep fail-closed

| Milestone | Outcome | Notes |
| --- | --- | --- |
| Multi-cycle traces | Independently verify sequences that visit rest more than once | Requires an env that is still sequence-independent, or an explicit UNSUPPORTED for mid-rest |
| Cascade fluid topology | Independent group-line check or keep NOT_EVALUATED | Do not paint G valves as a physics PASS |
| TIMER wall-clock | Out of scope unless a real-time model is specified | Discrete ticks stay the executed semantics |

## P1 — evidence

| Milestone | Outcome |
| --- | --- |
| SequenceBench-300 on CI | Already generated in-process; add the command to `.github/workflows/ci.yml` if the job stays under budget |
| SequenceBench-LLM live models | Only if someone else brings API credits. Keep `paid_api_calls` honest. This repo must still score the **compiler**, not the model |
| Mutation / adversarial expansion | More coil drops, sensor inversion, counterexample minimization |
| Dependency pin + pip-audit | Lockfile; fail CI on known vulnerable pins |

## P2 — external

| Milestone | Outcome |
| --- | --- |
| Student study | Faculty/TA runs `docs/user-study.md`. No invented n= |
| Public HTTPS MCP | Human hosts origin; then directory submit from `plugin/SUBMISSION.md` |
| Skills-only OpenAI path | If you refuse to host HTTP |

## Deferred research

Physics and pressure simulation. FluidSIM `.ct`. CompCert/SMT completeness. Paid Fly as a requirement.

## What would make this impressive (status)

| Claim | Status this audit |
| --- | --- |
| Core compiler and workspace | present; pytest 229 passed, 2 skipped; goldens exit 0 |
| Independent completion audit | this file set; not a rubber stamp of T0–T57 |
| Public distribution | GitHub + CLI + static workspace + Pages workflow in-repo; ChatGPT/Claude directory still pending human HTTPS + login |
| Full temporal and cascade verification | TIMER discrete ticks PASS; cascade electrical PASS; fluid cascade NOT_EVALUATED; multi-cycle rest UNSUPPORTED-by-oracle |
| 300-case reproducible benchmark | yes, fingerprint above, error rates 0 / 1 |
| External engineering validation | pending (study + directory + live models) |
