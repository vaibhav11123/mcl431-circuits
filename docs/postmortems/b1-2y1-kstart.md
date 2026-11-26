# B1 postmortem: 2Y1 on K_START

Wrong artifact: grinding-machine electropneumatic sheet compiled `2Y1` (feed advance) onto the start latch `K_START` / `K1`. The pneumatic drawing still looked like a 5/2 pair.

## Repro

YAML: `examples/grinding_machine/circuit.yaml`. After `apply_compile`, inspect contacts on coil `2Y1`. Illegal: `K1` (start) in that set.

## Invariant

`2y1_not_kstart` in `circuit.packs.mcl431` extra checks: `"K1" not in tags("2Y1")`. Eval owns the invariant. Drawing was never the source of truth.

## Why tests missed it

Sheet tests counted tokens (`2Y1` appears). They did not check *which contacts* drove `2Y1`. A green SVG is not an oracle.

## Fix

Compiler must not use the start latch as the feed-advance qualifier. Course pack check fails the spec. Fail-closed `draw_yaml` will not emit sheets when eval fails.

## Regression

`tests/test_eval.py::test_2y1_not_on_kstart`

Root cause: synthesizer used a convenient latch instead of the sequence sensor that actually means “feed may advance.”
