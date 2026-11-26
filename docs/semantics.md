# Semantics

Source (`spec_trace`): cylinder bits 0/1 after each sequence action. Independent copy. Do not import `compile_paths`.

Target (`graph_trace`): a path coil is ON iff every contact is true. A cylinder is 1 iff its + solenoid is ON, 0 iff its − solenoid is ON, else hold.

Refinement: rows equal on the requested run. Not LLVM-style UB. Not physical safety. Not a proof.

Mutex: START-only dual-solenoid ON is a planted miscompile. Full sensor-product enumeration is bounded and may be incomplete.
