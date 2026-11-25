# Execution plan

Status: not started. Score: 0/10 tasks, 0/39 measures. This is the plan to ship the studio as a product. Do not implement it until asked.

## Customer flow

The customer is a student who already has the lab text and does not have the sheets. They never see this repository.

1. Once, they install the plugin in ChatGPT, or they add the same URL as a connector in Claude. They do not install Python, an editor, or FluidSIM.
2. They paste the lab: the parts list and the sequence, such as clamp, then drill, then eject.
3. Their chat's model calls `list_symbols`, writes the spec, and calls `draw_spec`. The student does not write YAML and does not pick a sheet.
4. If a symbol or a contact is wrong, the chat shows one plain sentence and the model fixes the spec, at most twice. No sheet is shown until the check passes.
5. The chat then shows the pages that question needs: the power circuit, the electrical sheet and the step diagram when the lab asks for them, the written solution, and a card. A PLC lab gets the connection and the ladder. A paper that already prints the figure gets the calculation only.
6. The student hands in the sheets. A classmate can read the card from the image alone. They do not install anything.

A mechanic who only has the card can argue with the sentence. They are not asked to install. An instructor with a different symbol law points the same engine at their own pack later. The engine does not change.

## Still open, and what already exists

These sit between the customer flow and the ten tasks. The score stays 0/39 until the tasks run. The answers below are from public docs and one GPL tool. Do not copy that tool.

- **A public URL.** ChatGPT will not review a localhost or a tunnel that changes every restart. People ship this as a stable HTTPS host: a named Cloudflare Tunnel on a machine you already have, a Vercel app, or a small VM with automatic TLS. One example serves the MCP path and the privacy and terms pages from the same host (`https://mcp.companydossier.lol/mcp` plus `/privacy` and `/terms`). Domain check is a plain-text token at `https://<host>/.well-known/openai-apps-challenge`, described in [Submit plugins](https://developers.openai.com/plugins/deploy/submission). A markdown file in this repo does not satisfy the form. The logo, the category, and a verified OpenAI identity are form fields, not code.
- **The enabling condition.** [FluidPyPLC](https://github.com/mrlostintheinternet/fluidpyplc) (GPL-3) takes `A+/B+/B-/A-`, splits it into cascade groups, draws the phase diagram, and emits PLC structured text. The method itself is the NUS cascade note: no letter repeats inside a group, and each step's input is the previous limit switch plus the group line. Do not import FluidPyPLC. The contacts for a step are already built inside `compile_paths` in [src/circuit/compile_sequence.py](src/circuit/compile_sequence.py). A later task can print those contacts. Task 7 still forbids inventing a sentence that the ladder does not contain.
- **The card saying "closed center."** No library detects that fault. The spec already has valve type `dcv_4_3_spring_centered` and `relief_valves`. The sentence may say "closed center" only when that valve type is present and the relief list is empty. A pump with no relief and no closed-center valve gets the relief sentence only.
- **The model inventing YAML.** The published fix is a strict input schema plus one example on the tool, not a longer system prompt. Invalid arguments are rejected before the handler runs, and the model reads the error ([MCP tools](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/servers/tools.md), [tool descriptions](https://docs.unique.ai/administrators/mcp/the-mcp-hub/writing-effective-mcp-tool-definitions)). `CircuitSpec` can emit that schema. Put one short legal YAML in the `draw_spec` description.
- **Annotations.** FastMCP sets them on the decorator. The defaults are the wrong way around: `readOnlyHint` defaults to false, `destructiveHint` defaults to true, `openWorldHint` defaults to true ([FastMCP tools](https://gofastmcp.com/servers/tools)). Set all three on every tool or the review treats a lookup as a destructive call to the open web.
- **A free chat, and the shell card.** The pricing table already says plugins are on Free. No public write-up here shows a free account completing a call, so that check stays a human step on a free login. The card for a shell user is a `circuit card` command. Nothing online supplies it.

## How a step is marked

A step is not done because the code looks finished. It is done when every measure under it has Actual filled in and Pass set to pass. That is the usual close-out: a definition of done is a checklist, and an evidence log records the command, the expected result, and the actual result ([definition of done](https://microsoft.github.io/code-with-engineering-playbook/agile-development/team-agreements/definition-of-done/), [evidence log](https://github.com/kerberosmansour/hulumi/blob/main/docs/slo/templates/runbook-template_v_4_template.md)).

- Status on the tracker is `not started`, `ongoing`, or `done`. Set it to ongoing when the task starts. Set it to done only when that task's pass count equals its measure count.
- Leave Actual and Pass blank until the command has been run. Write the exit code, or the first failing line, in Actual. Pass is only `pass` or `fail`.
- A task score is passes over measures, for example `2/3`. The plan score is done tasks over 10.
- Do not start the next task while the current one is short of its count. `rg` with no matches exits 1. For those rows, pass means the output is empty, not that the exit code is 0.
- Tick the tracker box only at done.

Tracker:

- [ ] T1 pack resolution — 0/3 — not started
- [ ] T2 stamp directory — 0/3 — not started
- [ ] T3 eval hooks — 0/3 — not started
- [ ] T4 compile hooks — 0/3 — not started
- [ ] T5 solution hooks — 0/3 — not started
- [ ] T6 service functions — 0/7 — not started
- [ ] T7 ISO pack — 0/4 — not started
- [ ] T8 MCP process — 0/4 — not started
- [ ] T9 plugin files — 0/5 — not started
- [ ] T10 card — 0/4 — not started

## Official guidance for this plugin

OpenAI and Anthropic both publish the build path. This plan follows it. The pages to use, in order:

- ChatGPT and Codex: start at [Plugins](https://developers.openai.com/plugins). Package with [Package your plugin](https://developers.openai.com/plugins/build/plugins): root `plugin.json` on the agent-plugins schema, plus `mcp.json` with `type: streamable-http`. Publish with [Submit plugins](https://developers.openai.com/plugins/deploy/submission) and [Plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines). The form itself is described at [Submit plugins on ChatGPT Learn](https://learn.chatgpt.com/docs/submit-plugins).
- Claude: build with [Build an MCP server for Claude](https://claude.com/docs/connectors/building). A student can add the URL as a custom connector with no review. A directory listing is a later, optional submit at [Submit a connector](https://claude.com/docs/connectors/building/submission). Local `.mcpb` bundles are no longer accepted in that directory.

What those pages require that this repo does not have yet, and that a human does at submit time, not in T1–T8:

- A public HTTPS URL for the server, plus a public privacy policy URL, terms URL, and support URL. A markdown file in the repo is not enough for the form.
- Verified developer identity on the OpenAI side. Any paid Claude plan can submit a directory listing. Neither is a code change.
- Tool annotations on every tool: `readOnlyHint`, and `destructiveHint` where it applies. OpenAI also asks for `openWorldHint`. `list_symbols`, `validate_spec`, and `eval_spec` are read-only. `draw_spec` is not, because it runs the draw. None of them are destructive, and none of them call the open web.
- Domain check: host the token they give you at `/.well-known/openai-apps-challenge` on the MCP hostname.
- Five positive test cases and three negative ones, starter prompts, a logo, and a category. T9 writes the prompts. The logo and the live URL wait until there is a host.
- After the first publish, MCP tool changes are read from the server. A new ZIP is only for metadata and skills.

No authentication in v1, so the review does not need a demo login. Both guides reject a server that demands MFA or a private network.

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

If `test_cli` fails because `--help` output changed, update only the assertion that broke. Do not change ingest help tests' exit codes.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M1.1 | `python -m pytest tests/test_pack.py tests/test_validate.py tests/test_cli.py -q` | exit 0 | | |
| M1.2 | `resolve_pack` on a temp atlas whose only id is `dcv_5_2` | `load_atlas_ids` equals `{dcv_5_2}` | | |
| M1.3 | validate [examples/grinding_machine/circuit.yaml](examples/grinding_machine/circuit.yaml) with no `--pack` | every check ok | | |

## Task 2: stamp directory

Depends on: T1.

Files: modify `catalog.py`. Extend `tests/test_pack.py`.

What to do: `using_pack` sets a `ContextVar` to `pack.stamp_dir`. `Glyph.path` joins that directory with `self.file`. When the var is unset, use today's `lecture/crops/stamps` so a drawer called from a test that never enters the context still finds the PNG.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M2.1 | `python -m pytest tests/test_pack.py tests/test_draw_all.py tests/test_layout.py -q` | exit 0 | | |
| M2.2 | `draw_all` on the grinding spec | writes `hydraulic_circuit.svg` and the file contains `<svg` | | |
| M2.3 | `using_pack` with a stamp dir missing `cylinder_da.png` | `glyph` raises `FileNotFoundError` and the message contains `cylinder_da.png` | | |

## Task 3: eval hooks

Depends on: T2.

Files: create `packs/mcl431.py`. Modify `eval.py`.

What to do: cut the body of `math_checks` from the `exam = spec.meta.exam_id` line through the exam branches, including `_grinding_ladder_checks`, into `mcl431.extra_checks`. Leave `math_checks` as: generic checks that are not tied to an exam id, then `pack.extra_checks(spec)`. The regen ratio check is tied to `l4_regen` and `PatternId.REGEN`. It moves with the pack. `solution_lines_for` stays in [calc.py](src/circuit/calc.py) for this task. The pack may import it.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M3.1 | `python -m pytest tests/test_eval.py tests/test_calc.py -q` | exit 0 | | |
| M3.2 | `rg "exam_id ==" src/circuit/eval.py` | no lines | | |
| M3.3 | `rg "2023_selfstudy_b1\|2016_minor1_emboss" src/circuit/packs/mcl431.py` | at least one line | | |

## Task 4: compile hooks

Depends on: T3.

Files: modify `compile_sequence.py` and `packs/mcl431.py`.

What to do: `compile_paths` keeps the early return when `spec.electrical.paths` is already set. Next it calls `pack.compile_override(spec)`. The mcl431 override contains the two returns that today sit at lines 347–350 (`2016_minor1_emboss` → `_compile_emboss_2016`, the two drill ids → `_compile_indexing_drill`). Those functions can stay in `compile_sequence.py` and be imported by the pack. They are course ladders, not a second engine. The `dcv_5_3` heuristic, the motor-timer heuristic, and `_compile_chain` stay in `compile_paths`.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M4.1 | `python -m pytest tests/test_compile.py tests/test_eval.py -q` | exit 0 | | |
| M4.2 | `rg "exam_id ==" src/circuit/compile_sequence.py` | no lines | | |
| M4.3 | `rg "2016_minor1_emboss\|Fall17-Minor2" src/circuit/packs/mcl431.py` | at least one line | | |

## Task 5: solution and sheet hooks

Depends on: T4.

Files: modify `draw.py`, `draw_hydraulic.py`, `draw_pneumatic.py`, `packs/mcl431.py`.

What to do: `write_solution` keeps the title and the numbered sequence loop. The calculations header and `solution_lines_for` call move behind `pack.solution_extra`. The four `if spec.meta.exam_id` blocks in `write_solution` move into that same pack function, unchanged. `_write_plc_solution` keeps its zone table. The `solution_lines_for` call inside it also goes through `solution_extra`. `draw_hydraulic.py` line 35 becomes `label = pack.relief_label(spec)`, and the pack returns the grinding bar string for `2023_selfstudy_b1` and `None` otherwise. `draw_pneumatic.py` calls `pack.pneumatic_overlay(spec, svg)` where those two emboss blocks lived.

`draw_calc_only` may still print `spec.meta.exam_id` as a caption. That is not a branch. Leave it. Do not start T6 while M5.2 is fail.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M5.1 | `python -m pytest tests/test_draw_all.py tests/test_draw_phase.py tests/test_layout.py tests/test_eval.py tests/test_compile.py -q` | exit 0 | | |
| M5.2 | `rg "exam_id ==" src/circuit/draw.py src/circuit/draw_hydraulic.py src/circuit/draw_pneumatic.py src/circuit/draw_electrical.py src/circuit/draw_phase.py src/circuit/draw_plc.py` | no lines | | |
| M5.3 | `python -m pytest tests/test_validate.py tests/test_eval.py tests/test_compile.py tests/test_calc.py tests/test_draw_all.py tests/test_terminals.py tests/test_cli.py -q` | exit 0 | | |

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

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M6.1 | `python -m pytest tests/test_service.py tests/test_draw_all.py tests/test_cli.py -q` | exit 0 | | |
| M6.2 | `draw_yaml` on the grinding spec | `ok` true, `sheets.hydraulic` contains `<svg` | | |
| M6.3 | valve type `not_a_symbol` | `ok` false, `sheets` empty, sentence exactly `That symbol is not in the pack.` | | |
| M6.4 | [examples/grind_given_2022/circuit.yaml](examples/grind_given_2022/circuit.yaml) | `sheets` has `calc` and does not have `hydraulic` | | |
| M6.5 | [examples/plc_conveyor_2023/circuit.yaml](examples/plc_conveyor_2023/circuit.yaml) | `sheets` has `connection` and `ladder` | | |
| M6.6 | `list_symbols` on the checkout pack | an entry with id `dcv_5_2` and a non-empty `ports` list | | |
| M6.7 | `python -m circuit validate --json examples/grinding_machine/circuit.yaml` | exit 0, stdout parses as JSON | | |

## Task 7: ISO pack

Depends on: T6.

Files: create the iso pack data, `packs/iso_sequence.py`, [examples/iso_sequence/circuit.yaml](examples/iso_sequence/circuit.yaml), `tests/test_iso_pack.py`. Modify `pyproject.toml` package data so `circuit/packs/iso_sequence/**` is in the wheel.

What to do: copy [examples/emboss_2016/circuit.yaml](examples/emboss_2016/circuit.yaml) as the starting shape, then strip it. Domain `pneumatic_plus_electrical`. Patterns `ep_dac_5_2` and `sequence_double_solenoid`. Two cylinders, two `dcv_5_2` valves, a sequence of four steps in that order. Delete `exam_id`. Delete any sensor or coil the emboss pack hook required. Atlas lists only the symbol ids that spec uses. Copy only `dcv_5_2.png` and `dcv_5_3.png` from [lecture/crops/stamps](lecture/crops/stamps). Those are the CC-BY bodies named in [docs/copyright.md](docs/copyright.md). Draw the cylinder and any other glyph with [svgdraw.py](src/circuit/svgdraw.py). Do not copy `cylinder_l10.png` or any other lecture crop. Hooks: `extra_checks` asserts at least two valves of type `dcv_5_2`, a non-empty sequence in the stated order, and that the pneumatic SVG was drawn de-energized (the rest position of the 5/2, not the shifted envelope). `compile_override` returns `None`. `solution_extra` returns `[]`.

If the ISO spec only passes because of an emboss special case, M7.1 is fail.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M7.1 | `CIRCUIT_PACK=src/circuit/packs/iso_sequence python -m pytest tests/test_iso_pack.py tests/test_eval.py tests/test_draw_all.py -q` | exit 0 | | |
| M7.2 | list `src/circuit/packs/iso_sequence/stamps` | contains `dcv_5_2.png`, does not contain `cylinder_l10.png` | | |
| M7.3 | `rg "exam_id ==" src/circuit/draw_pneumatic.py src/circuit/draw_hydraulic.py` | no lines | | |
| M7.4 | ISO `solution.txt` | contains the four step labels, does not contain `enabling condition` | | |

## Task 8: MCP process

Depends on: T7.

Files: create `mcp_server.py` and `tests/test_mcp_server.py`. Add `mcp` to [pyproject.toml](pyproject.toml) dependencies only if the official Python SDK import used by the test is `mcp.server.fastmcp` or the SDK's current `FastMCP`. Pin the version you import. Do not add a second HTTP framework.

What to do: four tools with the names in the locked decisions. Each calls the matching function in `service.py`. Set `readOnlyHint` true on `list_symbols`, `validate_spec`, and `eval_spec`. Set it false on `draw_spec`. Set `destructiveHint` false and `openWorldHint` false on all four. OpenAI and Claude both reject a tool that is missing these. Stdio is the default when the module is run with no arguments. `--http` binds `127.0.0.1` and path `/mcp`. A draw that runs longer than 30 seconds returns an error and no sheet. Instructions string, at most 512 characters, in this order: call `list_symbols` first and use only returned ids and ports. Write YAML only. Use `pneumatic_plus_electrical` or `hydraulic_plus_electrical` when the lab asks for the electrical sheet. Use `figure_given` only when the figure is already on the paper. Use `plc` only when the paper asks for a PLC. Never invent a symbol id. Never generate an image. Call `draw_spec`. On failure, fix the YAML and call it at most two more times.

Log the tool name and the ok flag to stderr. Do not log the YAML. On HTTP, count `draw_spec` by the peer address, 30 per hour. On stdio, the same cap is per process. Over the cap, return an error the model can read, with no sheet. The test can set the limit to 1.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M8.1 | `python -m pytest tests/test_mcp_server.py tests/test_service.py tests/test_iso_pack.py -q` | exit 0 | | |
| M8.2 | in-process tool call with the ISO YAML | result has a pneumatic sheet and an electrical sheet | | |
| M8.3 | YAML of 300 KB | size error, no sheet | | |
| M8.4 | log capture of a call whose YAML contains the marker `MARKER-do-not-log` | captured log does not contain that marker | | |

## Task 9: plugin files

Depends on: T8.

Files: create `plugin/plugin.json`, `plugin/mcp.json`, `plugin/PRIVACY.md`, `plugin/REVIEW.md`. Modify [README.md](README.md) with a short "Use it from ChatGPT or Claude" section. Modify [.cursor/skills/generate-circuit/SKILL.md](.cursor/skills/generate-circuit/SKILL.md) so the model calls `list_symbols`, then writes YAML, then `draw_spec`, and does not invent a symbol or generate an image. Do not rewrite the rest of the README.

`plugin.json` uses `$schema` `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`, name, version `0.1.0`, MIT license. `mcp.json` uses the MCP schema and one server, `type` `streamable-http`, `url` `https://REPLACE_ON_DEPLOY/mcp`. `PRIVACY.md` says we receive the spec to draw that one call, we do not store it, and that on ChatGPT Free, Go, Plus, and Pro, OpenAI may use app content to train models when "Improve the model for everyone" is on. `REVIEW.md` has five prompts that should draw the ISO sequence and three that should refuse: an invented symbol id, a request to simulate pressure, and a request to ingest a course PDF.

Stop after these measures. Do not submit to the OpenAI plugin portal. Do not create an Anthropic connector. Do not deploy a host. Gemini uses this same URL later. No separate Gemini build.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M9.1 | `python -m json.tool plugin/plugin.json` and `python -m json.tool plugin/mcp.json` | both exit 0 | | |
| M9.2 | `mcp.json` server url | exactly `https://REPLACE_ON_DEPLOY/mcp` | | |
| M9.3 | `plugin/REVIEW.md` | 5 prompts that should draw, 3 that should refuse | | |
| M9.4 | `.cursor/skills/generate-circuit/SKILL.md` | contains `draw_spec` and `Never generate an image` | | |
| M9.5 | `python -m pytest tests/test_mcp_server.py tests/test_iso_pack.py tests/test_eval.py tests/test_draw_all.py -q` | exit 0 | | |

## Task 10: the card

Depends on: T9.

Files: modify `service.py` and `tests/test_service.py`. Create [examples/closed_center/circuit.yaml](examples/closed_center/circuit.yaml) by taking a small hydraulic golden and deleting `relief_valves`.

What to do: `draw_yaml` always includes a `card` sheet, including when `ok` is false. The card is an SVG built with `svgdraw`: the sequence lines, the one sentence, and the footer `Checked by circuit`. No PNG library. No account. A hydraulic spec with a pump and an empty `relief_valves` list already fails `has_prv` in [validate.py](src/circuit/validate.py). Do not add a second closed-center physics check. The card sentence for that failure is the `has_prv` sentence from T6.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M10.1 | `python -m pytest tests/test_service.py tests/test_validate.py -q` | exit 0 | | |
| M10.2 | `draw_yaml` on [examples/closed_center/circuit.yaml](examples/closed_center/circuit.yaml) | `ok` false, no hydraulic sheet | | |
| M10.3 | that same card SVG | contains `nowhere for the oil to go`, does not contain `has_prv` | | |
| M10.4 | ISO success card | contains the first step label and `Checked by circuit` | | |

## Standing bar

M5.3 and a rerun of that same command after M10.4 are the regression measures. An unknown symbol id still fails in `validate_spec` (M6.3). No new image generator. No new `PatternId`. The plan is done at 10/10 tasks and 39/39 measures, with every Actual cell filled from a command that was actually run.

## Rollback

T3 through T5 move code. If a golden fails, put the branch back in the engine file and stop. T8 can be left unrun. The CLI in this checkout must still validate, draw, and eval with no `--pack` flag after every task.
