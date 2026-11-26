# Semantics

Source (`spec_trace`): cylinder bits 0/1 after each sequence action. Independent copy. Do not import `compile_paths`.

Target (`env_trace`): sensors are derived from modeled actuator bits. START is pressed after rest. Coils follow L8 paths. The required sequence is not fed into the target.

`graph_trace` remains a unit-test helper that walks an explicit sensor assignment. `verify_spec` must not build those assignments from `_solenoid_for`.

Refinement: compressed `env_trace` rows equal `spec_trace` on one cycle back to rest. Not LLVM-style UB. Not physical safety. Not a proof.

Valve memory: a 5/2 double-solenoid cylinder holds its last commanded bit when both coils are off. Sensors are home iff bit 0 and end iff bit 1.

Timers: discrete coil ticks, not wall-clock. A coil named `T1_3s` must stay energized for 3 environment steps before contact `T1` is true. That is independent of `spec.sequence` except that the synthesizer emits the coil. Wall-clock seconds are not simulated.

Cascade: `meta.method: cascade` adds extra `dcv_5_2` group valves (`G1`…). Translation validation compares electrical step-memory (`env_trace`) to `spec_trace`. Group-line pneumatic topology is `NOT_EVALUATED`. Do not report cascade as a fluid-physics PASS.

Deadlock: if the environment stalls off rest with no timer charging, `verify_spec` is `FAIL` with `check: deadlock`. Exhausted step budgets stay `INCONCLUSIVE`, never `PASS`.

Pressure waits (`PS` / `PRESSURE`) stay `UNSUPPORTED`. Physics remains `NOT_EVALUATED`.

Status values: `PASS`, `FAIL`, `INCONCLUSIVE`, `UNSUPPORTED`, `NOT_EVALUATED`. Exhausted step budgets and truncated mutex are never `PASS`. Physics is always `NOT_EVALUATED`.

Mutex: START-only dual-solenoid ON is a planted miscompile. Full sensor-product enumeration that truncates the sensor set returns `INCONCLUSIVE`.
