# Execution plan

Status: not started. This is the plan to ship the studio as a product. Do not implement it until asked. Work in order, T1 through T10, and stop on the first red test.

An agent who did not see the research can implement from this file. The shape is the one used to turn a design into agent work: each task names files, a single change, a dependency, and a command that proves it ([write-plan](https://github.com/duthaho/claudekit/blob/main/skills/write-plan/SKILL.md), [task breakdown](https://claudeskills.info/skills/addyosmani/agent-skills/planning-and-task-breakdown/)). Do not fan out. The chain is T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → T9 → T10. Stop on the first red test.

## Locked decisions

Do not relitigate these. They come from the design.

- The product is this studio. ChatGPT is the student door. The same URL is a Claude connector. No hosted model, no `/v1/chat`, no database of questions.
- Public tools are `list_symbols`, `validate_spec`, `eval_spec`, `draw_spec`. Not `rasterize`, `ingest`, or `promote`.
- `PatternId` in [src/circuit/spec.py](src/circuit/spec.py) stays a closed enum this release.
- `draw_all` in [src/circuit/draw.py](src/circuit/draw.py) keeps its sheet rules. `figure_given` writes calc plus solution. `plc` writes connection, ladder, and solution. `pneumatic_plus_electrical` and `hydraulic_plus_electrical` add the electrical sheet and the step diagram. A bare `pneumatic` or `hydraulic` domain does not add those sheets. The server instructions say which domain to set. The engine does not guess.
- Course exam behavior is preserved by moving it, not by deleting it.
- Do not commit unless the user asks. Do not edit [lecture/atlas.yaml](lecture/atlas.yaml), [exams/](exams/), or [docs/copyright.md](docs/copyright.md). Do not add a symbol id.

## Trace against the research brief

These items were in the October 2026 research brief and were missing from the first task list. They are tasks below, not leftover prose.

- `list_symbols` must return ids and ports. The task returned ids only. The model invents a port when the atlas port list is hidden. Atlas entries already have `ports`. T6 returns them.
- The sentence a person reads must not be the check name. The brief's own example of a sentence that fails is `eval check closed_center failed`. The sentence that travels is "Fixed pump, closed center, nowhere for the oil to go." [validate.py](src/circuit/validate.py) already fails a hydraulic spec that has a pump and no relief (`has_prv`, detail `PRV required on every hydraulic power unit (L3)`). T10 maps that check to the plain sentence. Do not add a new physics rule.
- The classmate forwards a card, not a chat transcript. The brief's `render_card` was dropped. T10 adds one SVG: sequence, the one sentence, footer `Checked by circuit`. No account, no install, to read it.
- The proof pack must not copy lecture slide crops. [docs/copyright.md](docs/copyright.md) allows the Wikimedia CC-BY 5/2 and 5/3 bodies (`dcv_5_2`, `dcv_5_3`). `cylinder_l10.png` is a lecture crop. T7 may copy only the two CC-BY valve stamps. Anything else the proof spec needs is drawn with [svgdraw.py](src/circuit/svgdraw.py).
- The ISO pack's own checks were thinned to "two 5/2 valves and a non-empty sequence." The brief also requires a de-energized sheet and sequence order. T7 adds those two checks.
- `circuit validate --json` and `circuit eval --json` are how a shell-only chat reads the same report. T6 adds them. They print the service dict.
- `draw_all` sheet rules for `figure_given` and `plc` have no service test. T6 adds one each, using [examples/grind_given_2022/circuit.yaml](examples/grind_given_2022/circuit.yaml) and [examples/plc_conveyor_2023/circuit.yaml](examples/plc_conveyor_2023/circuit.yaml).
- ChatGPT review needs five positive prompts and three negative prompts. T9 writes them into `plugin/REVIEW.md` and does not submit.
- [.cursor/skills/generate-circuit/SKILL.md](.cursor/skills/generate-circuit/SKILL.md) still tells a local agent to draw. T9 points it at the four tools and forbids an invented symbol. It stays instructions. It is not a second product.
- Server instructions said one retry. The brief says fix at most twice. T8 says two retries. T8 also states the 30 second timeout from the design, which the task body had dropped.

Left out on purpose, because the brief itself closed them:

- Ingest, rasterize, and promote stay off the public tools.
- `PatternId` stays a Python enum this release.
- No simulator, no FluidSIM file import, no prompt-box website, no OAuth, no Gemini-only build. Gemini can use the same URL later. No IIT market-size claim.

## Correction the design left easy to get wrong

`displacement_rows` in [src/circuit/compile_sequence.py](src/circuit/compile_sequence.py) returns `step`, `action`, and `label` only. It does not contain enabling conditions. The lines that say "enabling condition → solenoid" are literal strings inside `write_solution` for `2023_minor2_q1`, `2016_minor1_emboss`, and the 2017 drill ids. A pack with no exam id gets the sequence list already built at the top of `write_solution` (number, action, seconds, label). It does not get a fabricated contact equation. The one-sentence tool reply on a pass is the first sequence step's action and label. On a failure it is the mapped sentence in Task 6, not the raw check name.

## Files

- Create [src/circuit/pack.py](src/circuit/pack.py). Resolve a pack. Hold `root`, `atlas_path`, `stamp_dir`, and optional hooks.
- Create [src/circuit/packs/mcl431.py](src/circuit/packs/mcl431.py). The exam branches, moved verbatim.
- Create [src/circuit/packs/iso_sequence.py](src/circuit/packs/iso_sequence.py). Two checks: two `dcv_5_2` valves, and a non-empty sequence. No exam id.
- Create [src/circuit/packs/iso_sequence/atlas.yaml](src/circuit/packs/iso_sequence/atlas.yaml) and [src/circuit/packs/iso_sequence/stamps/](src/circuit/packs/iso_sequence/stamps/). Copy only `dcv_5_2.png` and `dcv_5_3.png`. Draw every other proof glyph with svgdraw. Do not copy a PDF or a lecture crop.
- Create [src/circuit/service.py](src/circuit/service.py). The four tools, in process.
- Create [src/circuit/mcp_server.py](src/circuit/mcp_server.py). Stdio and streamable HTTP.
- Create [plugin/plugin.json](plugin/plugin.json), [plugin/mcp.json](plugin/mcp.json), [plugin/PRIVACY.md](plugin/PRIVACY.md).
- Modify [src/circuit/validate.py](src/circuit/validate.py), [src/circuit/catalog.py](src/circuit/catalog.py), [src/circuit/cli.py](src/circuit/cli.py), [src/circuit/eval.py](src/circuit/eval.py), [src/circuit/compile_sequence.py](src/circuit/compile_sequence.py), [src/circuit/draw.py](src/circuit/draw.py), [src/circuit/draw_hydraulic.py](src/circuit/draw_hydraulic.py), [src/circuit/draw_pneumatic.py](src/circuit/draw_pneumatic.py), [pyproject.toml](pyproject.toml).
- Create [tests/test_pack.py](tests/test_pack.py), [tests/test_service.py](tests/test_service.py), [tests/test_iso_pack.py](tests/test_iso_pack.py), [examples/iso_sequence/circuit.yaml](examples/iso_sequence/circuit.yaml).
- Do not modify [src/circuit/ingest.py](src/circuit/ingest.py), [src/circuit/ingest_extract.py](src/circuit/ingest_extract.py), [src/circuit/ingest_index.py](src/circuit/ingest_index.py), [src/circuit/ingest_ocr_pages.py](src/circuit/ingest_ocr_pages.py), [src/circuit/ingest_promote.py](src/circuit/ingest_promote.py), [src/circuit/ingest_run.py](src/circuit/ingest_run.py), [src/circuit/rasterize.py](src/circuit/rasterize.py), [src/circuit/spec.py](src/circuit/spec.py) except if a type import is required. `PatternId` stays.

## How a pack is found

`load_atlas_ids` today reads `root / "lecture" / "atlas.yaml"` ([validate.py](src/circuit/validate.py) line 37). `Glyph.path` today reads the global `STAMPS` ([catalog.py](src/circuit/catalog.py) lines 14–27). Those two lines are why a wheel cannot draw.

`resolve_pack()` in `pack.py`:

- `--pack PATH` or env `CIRCUIT_PACK` wins.
- Else if `parents[2] / "lecture" / "atlas.yaml"` exists, that `parents[2]` directory is the pack root, atlas is `lecture/atlas.yaml`, stamps are `lecture/crops/stamps`, hooks module is `circuit.packs.mcl431`.
- Else the pack root is the installed `circuit/packs/iso_sequence` directory, atlas is `atlas.yaml` inside it, stamps are `stamps/` inside it, hooks module is `circuit.packs.iso_sequence`.

A context manager `using_pack(pack)` sets the stamp directory for the current call and restores it after. `glyph()` reads that directory instead of the module global. `draw_hydraulic` and the other drawers do not grow a new parameter in T2. CLI commands enter `using_pack` once around validate, draw, and eval.

Hook methods, all optional. Missing method means the default.

- `extra_checks(spec) -> list[Check]`
- `compile_override(spec) -> list | None`. `None` means `compile_paths` continues with the code it has after the exam branches are gone.
- `solution_extra(spec) -> list[str]`. Lines appended after the generic sequence list. Empty for the ISO pack.
- `relief_label(spec) -> str | None`. Replaces the `2023_selfstudy_b1` branch in [draw_hydraulic.py](src/circuit/draw_hydraulic.py) line 35.
- `pneumatic_overlay(spec, svg) -> None`. Replaces both `2016_minor1_emboss` branches in [draw_pneumatic.py](src/circuit/draw_pneumatic.py) lines 25 and 107. The pack function contains those two blocks.

## Task 1: pack resolution

Depends on: nothing.

Files: create `pack.py`, `packs/__init__.py`, `tests/test_pack.py`. Modify `validate.py` and `cli.py`.

What to do: `load_atlas_ids` and `load_atlas_crops` open `pack.atlas_path` instead of `root / "lecture" / "atlas.yaml"`. `validate_spec` still accepts `root` so existing callers work. `cli.py` parses `--pack` on `validate`, `draw`, and `eval`, calls `resolve_pack`, and passes that root. With no flag, behavior matches today.

Acceptance: a test loads [examples/grinding_machine/circuit.yaml](examples/grinding_machine/circuit.yaml) through `validate_spec` and gets the same ok result as before. A test points `resolve_pack` at a temp directory with an `atlas.yaml` whose only symbol id is `dcv_5_2`, and `load_atlas_ids` returns that one id.

Run: `python -m pytest tests/test_pack.py tests/test_validate.py tests/test_cli.py -q`

Expected: pass. If `test_cli` fails because `--help` output changed, update only the assertion that broke. Do not change ingest help tests' exit codes.

## Task 2: stamp directory

Depends on: T1.

Files: modify `catalog.py`. Extend `tests/test_pack.py`.

What to do: `using_pack` sets a `ContextVar` to `pack.stamp_dir`. `Glyph.path` joins that directory with `self.file`. When the var is unset, use today's `lecture/crops/stamps` so a drawer called from a test that never enters the context still finds the PNG.

Acceptance: `draw_all` on the grinding spec still writes `hydraulic_circuit.svg`. A test that enters `using_pack` with a temp stamp dir missing `cylinder_da.png` gets `FileNotFoundError` from `glyph`, not a drawn box.

Run: `python -m pytest tests/test_pack.py tests/test_draw_all.py tests/test_layout.py -q`

## Task 3: eval hooks

Depends on: T2.

Files: create `packs/mcl431.py`. Modify `eval.py`.

What to do: cut the body of `math_checks` from the `exam = spec.meta.exam_id` line through the exam branches, including `_grinding_ladder_checks`, into `mcl431.extra_checks`. Leave `math_checks` as: generic checks that are not tied to an exam id, then `pack.extra_checks(spec)`. The regen ratio check is tied to `l4_regen` and `PatternId.REGEN`. It moves with the pack. `solution_lines_for` stays in [calc.py](src/circuit/calc.py) for this task. The pack may import it.

Acceptance: `rg "exam_id ==" src/circuit/eval.py` prints nothing. `rg "2023_selfstudy_b1|2016_minor1_emboss" src/circuit/packs/mcl431.py` prints the moved lines.

Run: `python -m pytest tests/test_eval.py tests/test_calc.py -q`

## Task 4: compile hooks

Depends on: T3.

Files: modify `compile_sequence.py` and `packs/mcl431.py`.

What to do: `compile_paths` keeps the early return when `spec.electrical.paths` is already set. Next it calls `pack.compile_override(spec)`. The mcl431 override contains the two returns that today sit at lines 347–350 (`2016_minor1_emboss` → `_compile_emboss_2016`, the two drill ids → `_compile_indexing_drill`). Those functions can stay in `compile_sequence.py` and be imported by the pack. They are course ladders, not a second engine. The `dcv_5_3` heuristic, the motor-timer heuristic, and `_compile_chain` stay in `compile_paths`.

Acceptance: `rg "exam_id ==" src/circuit/compile_sequence.py` prints nothing. Drill and emboss goldens still compile the same coils.

Run: `python -m pytest tests/test_compile.py tests/test_eval.py -q`

## Task 5: solution and sheet hooks

Depends on: T4.

Files: modify `draw.py`, `draw_hydraulic.py`, `draw_pneumatic.py`, `packs/mcl431.py`.

What to do: `write_solution` keeps the title and the numbered sequence loop. The calculations header and `solution_lines_for` call move behind `pack.solution_extra`. The four `if spec.meta.exam_id` blocks in `write_solution` move into that same pack function, unchanged. `_write_plc_solution` keeps its zone table. The `solution_lines_for` call inside it also goes through `solution_extra`. `draw_hydraulic.py` line 35 becomes `label = pack.relief_label(spec)`, and the pack returns the grinding bar string for `2023_selfstudy_b1` and `None` otherwise. `draw_pneumatic.py` calls `pack.pneumatic_overlay(spec, svg)` where those two emboss blocks lived.

Acceptance: `rg "exam_id" src/circuit/draw.py src/circuit/draw_hydraulic.py src/circuit/draw_pneumatic.py src/circuit/draw_electrical.py src/circuit/draw_phase.py src/circuit/draw_plc.py` prints nothing. `draw_calc_only` may still print `spec.meta.exam_id` as a label on the calc sheet. That one string is a caption, not a branch. Leave it.

Run: `python -m pytest tests/test_draw_all.py tests/test_draw_phase.py tests/test_layout.py tests/test_eval.py tests/test_compile.py -q`

Checkpoint: do not start T6 if any of those files still branch on an exam id. The calc caption is the only allowed hit.

## Task 6: service functions

Depends on: T5.

Files: create `service.py` and `tests/test_service.py`.

What to do: four functions. They enter `using_pack`. They do not shell out.

- `list_symbols() -> dict` with `symbols`: a list of `{id, ports}` from the atlas. Ports come from each symbol entry. An entry with no ports field returns an empty list for that id. Do not invent a port.
- `validate_yaml(text) -> dict` with `ok` and `checks` (`name`, `ok`, `detail`).
- `eval_yaml(text) -> dict` with `ok`, `checks`, and `sentence`.
- `draw_yaml(text) -> dict`. Run validate, then eval. If either fails, return `ok: false`, `sentence`, and `sheets: {}`. Do not call `draw_all`. If both pass, call `draw_all` in a temp directory, read each `.svg` and `solution.txt` into `sheets`, delete the temp directory in a `finally`. Omit PNG keys.

`sentence` is looked up from the check name. `has_prv` maps to `A fixed pump needs a relief valve. This sheet has nowhere for the oil to go.` An unknown symbol maps to `That symbol is not in the pack.` Any other failure uses the check detail only when no sentence is mapped. A pass uses the first sequence step's action and label.

`circuit validate --json` and `circuit eval --json` print the same dict as `validate_yaml` and `eval_yaml`. No flag still prints today's text.

`CircuitSpec.from_yaml` today takes a path. Write the text to the temp file, then call it. Cap the text at 256 * 1024 bytes inside `draw_yaml` and return `ok: false` with sentence `spec too large` without drawing.

Acceptance: grinding YAML returns `ok: true` and a `hydraulic` sheet whose text contains `<svg`. `list_symbols` on the checkout pack includes `dcv_5_2` and its ports. A YAML whose valve type is `not_a_symbol` returns `ok: false`, empty `sheets`, and the sentence `That symbol is not in the pack.` The grind-given example returns a `calc` sheet and no `hydraulic` sheet. The PLC conveyor example returns `connection` and `ladder`. `circuit validate --json` on the grinding file exits 0 and the stdout parses as JSON.

Run: `python -m pytest tests/test_service.py tests/test_draw_all.py tests/test_cli.py -q`

## Task 7: ISO pack

Depends on: T6.

Files: create the iso pack data, `packs/iso_sequence.py`, [examples/iso_sequence/circuit.yaml](examples/iso_sequence/circuit.yaml), `tests/test_iso_pack.py`. Modify `pyproject.toml` package data so `circuit/packs/iso_sequence/**` is in the wheel.

What to do: copy [examples/emboss_2016/circuit.yaml](examples/emboss_2016/circuit.yaml) as the starting shape, then strip it. Domain `pneumatic_plus_electrical`. Patterns `ep_dac_5_2` and `sequence_double_solenoid`. Two cylinders, two `dcv_5_2` valves, a sequence of four steps in that order. Delete `exam_id`. Delete any sensor or coil the emboss pack hook required. Atlas lists only the symbol ids that spec uses. Copy only `dcv_5_2.png` and `dcv_5_3.png` from [lecture/crops/stamps](lecture/crops/stamps). Those are the CC-BY bodies named in [docs/copyright.md](docs/copyright.md). Draw the cylinder and any other glyph with [svgdraw.py](src/circuit/svgdraw.py). Do not copy `cylinder_l10.png` or any other lecture crop. Hooks: `extra_checks` asserts at least two valves of type `dcv_5_2`, a non-empty sequence in the stated order, and that the pneumatic SVG was drawn de-energized (the rest position of the 5/2, not the shifted envelope). `compile_override` returns `None`. `solution_extra` returns `[]`.

Acceptance: with `CIRCUIT_PACK` pointed at `src/circuit/packs/iso_sequence`, `validate`, `draw`, and `eval` on `examples/iso_sequence/circuit.yaml` all succeed. The ISO stamp directory does not contain `cylinder_l10.png`. `rg "exam_id ==" src/circuit/draw_pneumatic.py src/circuit/draw_hydraulic.py` still prints nothing. The solution text contains the four step labels and does not contain the string `enabling condition`.

Run: `python -m pytest tests/test_iso_pack.py tests/test_eval.py tests/test_draw_all.py -q`

Checkpoint: this is the product claim. If the ISO spec only passes because of an emboss special case, T7 is not done.

## Task 8: MCP process

Depends on: T7.

Files: create `mcp_server.py` and `tests/test_mcp_server.py`. Add `mcp` to [pyproject.toml](pyproject.toml) dependencies only if the official Python SDK import used by the test is `mcp.server.fastmcp` or the SDK's current `FastMCP`. Pin the version you import. Do not add a second HTTP framework.

What to do: four tools with the names in the locked decisions. Each calls the matching function in `service.py`. Stdio is the default when the module is run with no arguments. `--http` binds `127.0.0.1` and path `/mcp`. A draw that runs longer than 30 seconds returns an error and no sheet. Instructions string, at most 512 characters, in this order: call `list_symbols` first and use only returned ids and ports. Write YAML only. Use `pneumatic_plus_electrical` or `hydraulic_plus_electrical` when the lab asks for the electrical sheet. Use `figure_given` only when the figure is already on the paper. Use `plc` only when the paper asks for a PLC. Never invent a symbol id. Never generate an image. Call `draw_spec`. On failure, fix the YAML and call it at most two more times.

Log the tool name and the ok flag to stderr. Do not log the YAML. On HTTP, count `draw_spec` by the peer address, 30 per hour. On stdio, the same cap is per process. Over the cap, return an error the model can read, with no sheet. The test can set the limit to 1.

Acceptance: an in-process call of the tool function with the ISO YAML returns a pneumatic sheet and an electrical sheet. A second test feeds 300 KB of YAML and gets the size error. A third test asserts a log record does not contain a unique marker planted in the YAML.

Run: `python -m pytest tests/test_mcp_server.py tests/test_service.py tests/test_iso_pack.py -q`

## Task 9: plugin files

Depends on: T8.

Files: create `plugin/plugin.json`, `plugin/mcp.json`, `plugin/PRIVACY.md`, `plugin/REVIEW.md`. Modify [README.md](README.md) with a short "Use it from ChatGPT or Claude" section. Modify [.cursor/skills/generate-circuit/SKILL.md](.cursor/skills/generate-circuit/SKILL.md) so the model calls `list_symbols`, then writes YAML, then `draw_spec`, and does not invent a symbol or generate an image. Do not rewrite the rest of the README.

`plugin.json` uses `$schema` `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`, name, version `0.1.0`, MIT license. `mcp.json` uses the MCP schema and one server, `type` `streamable-http`, `url` `https://REPLACE_ON_DEPLOY/mcp`. `PRIVACY.md` says we receive the spec to draw that one call, we do not store it, and that on ChatGPT Free, Go, Plus, and Pro, OpenAI may use app content to train models when "Improve the model for everyone" is on. `REVIEW.md` has five prompts that should draw the ISO sequence and three that should refuse: an invented symbol id, a request to simulate pressure, and a request to ingest a course PDF.

Acceptance: both JSON files parse. The URL is the placeholder, not a guessed host. README mentions the four tool names and says ingest is not one of them. The skill file names `draw_spec` and does not tell the model to generate an image.

Stop. Do not submit to the OpenAI plugin portal. Do not create an Anthropic connector. Do not deploy a host. Those need an account and a public URL the user chooses. Gemini uses this same URL later. No separate Gemini build.

Run: `python -m pytest tests/test_mcp_server.py tests/test_iso_pack.py tests/test_eval.py tests/test_draw_all.py -q`

## Task 10: the card

Depends on: T9.

Files: modify `service.py` and `tests/test_service.py`. Create [examples/closed_center/circuit.yaml](examples/closed_center/circuit.yaml) by taking a small hydraulic golden and deleting `relief_valves`.

What to do: `draw_yaml` always includes a `card` sheet, including when `ok` is false. The card is an SVG built with `svgdraw`: the sequence lines, the one sentence, and the footer `Checked by circuit`. No PNG library. No account. A hydraulic spec with a pump and an empty `relief_valves` list already fails `has_prv` in [validate.py](src/circuit/validate.py). Do not add a second closed-center physics check. The card sentence for that failure is the `has_prv` sentence from T6.

Acceptance: the closed-center example returns `ok: false`, no power-circuit sheet, and a `card` SVG that contains `nowhere for the oil to go` and does not contain `has_prv`. The ISO success card contains the first step label and the footer.

Run: `python -m pytest tests/test_service.py tests/test_validate.py -q`

## Standing bar

Every task, before it is done: the command for that task exits 0. `python -m pytest tests/test_validate.py tests/test_eval.py tests/test_compile.py tests/test_calc.py tests/test_draw_all.py tests/test_terminals.py tests/test_cli.py -q` still exits 0 after T5 and after T10. An unknown symbol id still fails in `validate_spec`. No new image generator. No new `PatternId`.

## Rollback

T3 through T5 move code. If a golden fails, put the branch back in the engine file and stop. T8 can be left unrun. The CLI in this checkout must still validate, draw, and eval with no `--pack` flag after every task.
