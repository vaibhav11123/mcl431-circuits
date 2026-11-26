# Mutation detection matrix

Measured by `tests/test_mutations.py` and `tests/test_planted_miscompile.py` on this VM.

| Fault class | Structural | Behavioral | Artifact |
| --- | --- | --- | --- |
| Swapped plus/minus coils | — | FAIL | no pneumatic sheet |
| Missing K1 latch | — | FAIL or INCONCLUSIVE | — |
| NC flipped to NO | — | FAIL | — |
| Deleted last transition | — | FAIL | — |
| Rewired completion sensor | — | FAIL | — |
| START dual-solenoid plant | — | FAIL | no pneumatic sheet |
| Fluid port to coil | E210 | — | — |
| Truncated mutex bound | — | INCONCLUSIVE | — |
| Dropped TIMER coil `T1_*s` | — | FAIL | — |
| Cascade `G1` present | structural | electrical PASS ≠ fluid topology | fluid topology `NOT_EVALUATED` |
| START-only `1Y1` stall | — | FAIL deadlock | no sheet |

Physical dynamics are `NOT_EVALUATED`. Pressure waits are `UNSUPPORTED`.
