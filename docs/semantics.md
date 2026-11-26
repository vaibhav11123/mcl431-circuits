# Semantics

Source (`spec_trace`): cylinder bits 0/1 after each sequence action. Independent copy. Do not import `compile_paths`.

Target (`env_trace`): sensors are derived from modeled actuator bits. START is pressed after rest. Coils follow L8 paths. The required sequence is not fed into the target.

`graph_trace` remains a unit-test helper that walks an explicit sensor assignment. `verify_spec` must not build those assignments from `_solenoid_for`.

Refinement: compressed `env_trace` rows equal `spec_trace` on one cycle back to rest. Not LLVM-style UB. Not physical safety. Not a proof.

Status values: `PASS`, `FAIL`, `INCONCLUSIVE`, `UNSUPPORTED`, `NOT_EVALUATED`. Exhausted step budgets and truncated mutex are never `PASS`. Physics is always `NOT_EVALUATED`.

Mutex: START-only dual-solenoid ON is a planted miscompile. Full sensor-product enumeration that truncates the sensor set returns `INCONCLUSIVE`.
