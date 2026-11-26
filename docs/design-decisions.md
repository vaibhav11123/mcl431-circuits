# Design decisions

## 1. Correctness over generation

The model proposes YAML. The compiler authorizes artifacts. Flipped if a proof assistant is in-tree (it will not be).

## 2. YAML IR

`CircuitSpec` is the typed IR. Coordinates are not in the spec. Flipped if a customer requires native FluidSIM files — we still would not emit `.ct`.

## 3. Refuse physics

No pressure simulation. Sequence explorer is 0/1 actuator bits. Flipped only with a licensed hydraulics solver and a new eval gate.

## 4. PNG ImageContent in chat

SVG-in-JSON overflows context. Chat gets a preview PNG; `get_sheet` redraws from full YAML. Flipped if hosts accept native SVG attachments under 100k.

## 5. Fail-closed CLI

`python -m circuit draw` goes through `draw_yaml`. `--unverified` watermarks sheets. Flipped only if a maintainer is debugging layout and accepts an unverified SVG.

## 6. Independent environment

Target sensors come from modeled actuator bits (`env_trace`). The required sequence is not an input to the target interpreter. Flipped only if a second, independently written simulator is added.

## 7. Hooks from the pack root

`eval_spec(spec, root)` uses `pack_from_root(root)`, not leftover `CIRCUIT_PACK`. Flipped if multi-pack threads become first-class.

Owned failure: B1 `2Y1` on `K_START` was a compiler bug, not a drawing bug. The ladder checks live in `packs/mcl431.py`.
