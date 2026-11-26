# Verification coverage

Date: 2026-11-26 IST. Logical 0/1 traces only. Not CompCert. Not physical safety.

## Executed checks

| Property | Mechanism | Pass means | Test |
| --- | --- | --- | --- |
| Sequence 0/1 cycle | `spec_trace` ⋈ compressed `env_trace` | rows equal on one return to rest | `tests/test_refine.py`, `tests/test_sequencebench.py` |
| Dual solenoid at START | `start_dual_solenoid` | FAIL | `tests/test_planted_miscompile.py` |
| TIMER dwell | coil `Tn_Xs` must stay on for X env steps before contact `Tn` | PASS on one-cycle TIMER sequences | `tests/test_timer_cascade_deadlock.py::test_timer_sequence_verifies`; SequenceBench case_15–18 |
| Cascade electrical | `apply_cascade` then same trace refine | PASS if step-memory matches sequence | `test_cascade_two_cylinder_verifies` |
| Deadlock / stalled progress | stall off rest, no timer charging | FAIL `check: deadlock` | `test_deadlock_fail_not_pass`; SequenceBench-LLM `llm_10` |
| Invented atlas id | `valve_*_in_atlas` | reject | SequenceBench case invented; `llm_01` |
| Missing PRV | `has_prv` | reject | SequenceBench hydraulic; `llm_05` |
| Cascade >3 cylinders | `cascade_limit` | reject | case_21; `llm_06` |
| FluidSIM `.ct` | `_load_spec` | reject | `tests/test_refuse.py` |
| Pressure wait `PS`/`PRESSURE` | `verify_spec` | **UNSUPPORTED** | `test_pressure_wait_still_unsupported` |
| Exhausted env budget | `env_trace` max_steps | **INCONCLUSIVE**, never PASS | `tests/test_mutex.py` truncated bound analog |
| Physics / pressure drop | refused | **NOT_EVALUATED** | ADR-007; footer on report SVG |

## Explicitly not verified

| Property | Status | Why |
| --- | --- | --- |
| Wall-clock TIMER seconds | not verified | discrete ticks only |
| Cascade group-line pneumatics | NOT_EVALUATED | G valves are extra 5/2 components; `env_trace` does not simulate group pressure |
| Multi-cycle sequences that visit rest before the last step | not independently verified | `env_trace` stops at first rest |
| Analog pressure, flow, leakage | NOT_EVALUATED / UNSUPPORTED | no physics engine |
| Machine safety / ISO 13849 | not claimed | footer: logical checks only |
| LLM quality vs humans | fixtures only | SequenceBench-LLM does not call a model API |

## Benchmarks

```bash
python3 -m circuit bench benchmarks/sequencebench
python3 -m circuit bench --suite 300
python3 -m circuit bench --suite llm
```

SequenceBench-300 fingerprint (generator in `src/circuit/bench300.py`):

`c502bcc32db7a8803669a257821679e0a4033a36414eb6fee3a0a2226d4ec5bf`

Measured this VM: 220 accept / 80 reject, both error rates 0 and 1 respectively.

SequenceBench-LLM measured this VM: compiler caught every invalid fixture; naive YAML-parse accepted every invalid fixture (`naive_accept_invalid_rate` 1.0). That is the value of the compiler versus a wrapper. It is **not** a live-model eval.
