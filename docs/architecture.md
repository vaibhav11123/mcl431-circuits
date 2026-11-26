# Architecture

Parse YAML → `CircuitSpec` → typecheck → synthesize (`compile_paths` or pack `compile_override`) → `spec_trace` ⋈ `env_trace` → seal `VerifiedCircuit` → layout → SVG.

`graph_trace` is a unit-test helper that walks explicit sensor assignments. `verify_spec` must not feed the required sequence into the target.

Packs: lecture (`circuit.packs.mcl431`) vs ISO (`circuit.packs.iso_sequence`). `using_pack` sets stamp dir + hooks. The ISO pack cannot resolve `lecture/crops`.

Public API: `circuit.service.draw_yaml`. CLI `draw` calls it. `--unverified` watermarks sheets.
