# Architecture

Parse YAML → `CircuitSpec` → typecheck → synthesize (`compile_paths`) → `spec_trace` ⋈ `graph_trace` → layout → SVG.

Packs: lecture (`circuit.packs.mcl431`) vs ISO (`circuit.packs.iso_sequence`). `using_pack` sets stamp dir + hooks.

Public API: `circuit.service.draw_yaml`. CLI `draw` may still draw without eval; `--json` and MCP are fail-closed.
