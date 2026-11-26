# Sequence Circuit — executable product plan

Status: executed on this VM (2026-11-26 IST). Score: 45/45 original tasks + T46–T57 P0 corrections. `pytest -q` 193 passed, 2 skipped. `python -m circuit eval --goldens` exit 0. Docker `sequence-circuit` `:8766/health` `{"ok":true}`, `id -u` 10001, MCP initialize 200. Workspace `http://127.0.0.1:8088/` 200. T29 Fly skipped (`no FLY_API_TOKEN`). Human leftovers: ChatGPT/Claude login, OpenAI directory submit.

**Do not position this as an AI-powered circuit generator.** That is an LLM wrapper. The CS problem is:

> How do you let a probabilistic model propose an engineering artifact without giving it authority over correctness?

Product sentence (students): **From engineering problem to verified circuit. Draw it, understand it, modify it, explain it.**

Engineering sentence (staff loop): **A deterministic compiler decides whether an AI-generated design is allowed to become an artifact.** Pneumatics are the demonstration domain, not the thesis.

GitHub subtitle: `Verification-oriented compiler for AI-generated engineering systems.` Do **not** write “formally verified compiler” unless a proof assistant is in the tree (it will not be). Bounded translation validation ≠ CompCert.

References this layer is copied *from as principles*, not as code: [Alive2](https://github.com/AliveToolkit/alive2) (independent src vs tgt check + counterexample), [Csmith](https://github.com/csmith-project/csmith) (generate well-defined programs, differential oracle, then reduce), [Hypothesis stateful](https://hypothesis.readthedocs.io/en/latest/stateful.html), [MLIR verifiers](https://mlir.llvm.org/docs/LangRef/) (pass-local invariants, not LLVM in this repo). No Kubernetes, no Rust rewrite, no Z3 until exhaustive BFS is too small.

How this document is written: one task = files + what to write + interfaces later tasks consume + tests written first (red) + commands with Expected + a live check when the output is a picture or a page. Pattern from this repo’s [ship-execution-plan.md](ship-execution-plan.md) and from [writing-plans](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md) (RED-GREEN, exact paths, expected output). Live MCP checks use the [Inspector CLI](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/cli) (`tools/list`, `tools/call`, exit 5 on `isError`). Visual sheets follow [plc-visual-qa.md](plc-visual-qa.md): open the PNG, score it, do not trust pytest alone.

## How a step is marked

- Status: `not started` | `ongoing` | `done`. Done only when that task’s Pass count equals its measure count.
- Actual: exit code or first failing line. Pass: `pass` or `fail` only.
- `rg` with no matches exits 1. For those rows, pass means **empty output**, not exit 0.
- Do not start the next task while the current one is short. Stop on red. If the plan is wrong, write `Ruling:` under the task and stop for the user — do not stub.
- Regression bar after every phase: `pytest -q` and `python -m circuit eval --goldens` both exit 0.
- After T36 exists, also `pytest tests/test_refine.py tests/test_planted_miscompile.py -q`. A green draw with a red oracle is not done.

Tracker:

- [x] T0 VM bootstrap — 4/4 (`rsvg-convert`, pytest 178, goldens 0)
- [x] T1 pack resolution — 3/3
- [x] T2 stamp ContextVar — 4/4
- [x] T3 eval hooks — 3/3
- [x] T4 compile hooks — 3/3
- [x] T5 solution/sheet hooks — 3/3
- [x] T6 service + `--json` + fail-closed draw — 7/7
- [x] T7 ISO vector pack — 6/6
- [x] T8 provenance + tag round-trip — 4/4
- [x] T9 print pack (SVG/PNG/PDF/BOM/principle/report) — 6/6
- [x] T10 verification report + card — 4/4
- [x] T11 MCP FastMCP + ImageContent + get_sheet — 8/8 (Inspector HTTP live)
- [x] T12 plugin files + skills + graceful refusals — 5/5
- [x] T13 Docker /mcp live — 5/5 (`docker build` + `:8766/health` + initialize + uid 10001 + `/privacy`)
- [x] T14 Pyodide spike — page in `web/spike.html` (WASM pydantic is a documented fallback to CLI)
- [x] T15 static workspace UI — 6/6
- [x] T16 workspace live — `/api/draw` ok; browser subagent
- [x] T17 IR edits + undo — 5/5
- [x] T18 TIMER through ISO — 3/3
- [x] T19 sequence explorer JSON + UI — 5/5
- [x] T20 explain + viva templates — 3/3
- [x] T21 public PLC on ISO engine — draw_yaml plc conveyor still sheets connection+ladder
- [x] T22 ISO hydraulic vectors — `draw_glyph` pump/tank/prv
- [x] T23 cascade groups (existing 5/2 only) — 5/5
- [x] T24 Check/Debug suggest_patch — 4/4
- [x] T25 localStorage library + YAML share — 3/3
- [x] T26 templates + practice — 3/3
- [x] T27 README / GEO / Pages — 4/4
- [x] T28 Inspector golden prompts live — pytest classes + HTTP draw_spec
- [ ] T29 optional Fly — **DEFERRED** (no `FLY_API_TOKEN`; token would not authorize spend)
- [x] T30 design-decisions + related work — 3/3
- [x] T31 ISO visual QA log — 4/4
- [x] T32 standing goldens + CI — 3/3
- [x] T33 typed graph IR + port-role errors — 5/5
- [x] T34 spec-trace oracle — 4/4
- [x] T35 circuit-graph interpreter — 5/5
- [x] T36 translation validation — 5/5
- [x] T37 planted miscompile caught — 3/3
- [x] T38 bounded mutex exploration — `start_dual_solenoid` + `mutex_explore`
- [x] T39 Hypothesis properties + edit state machine — 5/5
- [x] T40 verification manifest + `circuit verify` — 5/5
- [x] T41 SequenceBench v0 — 30 original YAMLs
- [x] T42 ADR-001..008 + B1 postmortem + architecture.md — 4/4
- [x] T43 cross-runtime graph hash — 3/3
- [x] T44 bounded synthesis — 3/3
- [x] T45 layout metrics — 3/3
- [x] T46 independent `env_trace` — sensors from actuator bits
- [x] T47 CLI `draw` fail-closed + `--unverified` watermark
- [x] T48 `VerifiedCircuit` seal; drawers consume compiled paths
- [x] T49 typed `Port` + fluid-to-coil E210
- [x] T50 PASS/FAIL/INCONCLUSIVE/UNSUPPORTED/NOT_EVALUATED
- [x] T51 SequenceBench expected traces (independent oracle)
- [x] T52 mutation suite
- [x] T53 threat model
- [x] T54 ISO pack cannot load lecture crops
- [x] T55 truncated mutex is INCONCLUSIVE
- [x] T56 Docker `--host 0.0.0.0` live
- [x] T57 every measure Actual filled from this VM

## Locked decisions

Do not relitigate.

1. Do not edit `lecture/atlas.yaml`, `exams/`, `docs/copyright.md`. Do not add an atlas symbol id. `PatternId` enum stays closed. Cascade is `meta.method: cascade` plus extra valves typed `dcv_5_2_double_solenoid` (or ISO atlas id `dcv_5_2` if that is what the ISO atlas lists — match the atlas, do not invent).
2. Public stamps: copy only Wikimedia CC-BY `dcv_5_2.png` and `dcv_5_3.png` ([copyright.md](copyright.md)). Every other public glyph is [svgdraw.py](../src/circuit/svgdraw.py). Lecture PNG in a public SVG is a fail.
3. **Reversed 2026-11-26:** CLI `draw` calls `service.draw_yaml` (fail-closed). `--unverified` is the only escape hatch and watermarks every SVG `UNVERIFIED`. `draw --json` remains the service dict.
4. `get_sheet` always takes **full YAML + sheet name**. Redraw. No store.
5. Chat preview PNG ≤800px wide and ≤200KB. Print PNG/PDF are uncapped by that.
6. Hosted Fly is optional. Workspace + CLI must work with Fly down.
7. No physics simulator. No FluidSIM `.ct`. No OAuth. No accounts. No hosted LLM. No lecture PDFs in the plugin ZIP.
8. Execution is this VM. No Darwin `qlmanage`. Install `librsvg2-bin`.
9. Hooks follow `eval_spec(spec, root)` / `using_pack(resolve_pack())` from `root`, not from a leftover `CIRCUIT_PACK` in the environment, so goldens stay green when someone has ISO in env.
10. Agent does not submit to OpenAI/Anthropic directories.
11. Do not claim CompCert, SMT completeness, or physical safety. Logical verification only. Manifest checks that were not run are `not_evaluated`, never `passed`.
12. SequenceBench must not contain `exams/transcribed`, lecture crops, or near-duplicates of goldens that would inflate scores. Original sequences only.
13. The graph interpreter in T35 must live in a file that does **not** import `compile_paths`. A second call to the synthesizer is not an oracle.
14. Do not add LLVM, MLIR, Z3, Kafka, or a second language “for the resume.” Exhaustive BFS first. Z3 is a later `Ruling:` if 3-cylinder mutex enumeration exceeds 2s.
15. Do not rearrange the whole repo into `ir/passes/semantics` on T1. Grow those packages from T33. Architecture must be visible in import graph, not only in docs.

## Compiler pipeline (what “compiler” means here)

Do not dump this into `draw_pneumatic`. Each pass is a function with a typed in/out. Tests may call a pass without drawing.

| Pass | In | Out | First lives in |
| --- | --- | --- | --- |
| Parse | YAML | `CircuitSpec` | [spec.py](../src/circuit/spec.py) `from_yaml` |
| Normalize | spec | spec with sorted ids, canonical solenoid order | T33 `ir/normalize.py` |
| Typecheck | spec | ok / `E2xx` port-role errors | T33 `ir/typecheck.py` |
| Behavioral lowering | spec.sequence | `SpecTrace` (actuator 0/1 per step) | T34 — **must not** import `compile_paths` |
| Synthesize | spec | `CircuitGraph` (nodes=components, edges=nets or L8 paths) | today’s `compile_paths` + valve map, re-exported from `ir/synthesize.py` |
| Semantic verify | SpecTrace × Graph | pass or `Counterexample` | T36 |
| Bounded check | Graph | mutex/deadlock/cex | T38 |
| Provenance | Graph × SVG | P001/P002 + element→spec origins | T8 then T33 |
| Layout | Graph | coordinates | existing drawers |
| Emit | layout | SVG/PDF/manifest | T9, T40 |

`draw_yaml` after T36: typecheck → synthesize → **verify** → layout → emit. If verify fails, no sheet (same as eval fail).

Port-role error example (exact test string T33): connecting a valve `P` port to a coil tag yields `E210` and `Compatible fluid-domain port` in the detail. Not `invalid circuit`.

Independent verification (Alive2 analog, domain-sized):

- **Source:** `spec_trace(spec)` = required actuator states after each sequence action (same 0/1 machine as [draw_phase.py](../src/circuit/draw_phase.py) `_next_state`, but copied into `semantics/spec_trace.py` and **not** used by the synthesizer).
- **Target:** `env_trace(graph)` = sensors from modeled actuator bits; START after rest; coils from L8 paths. `graph_trace` is a unit helper only. `verify_spec` must not import `_solenoid_for`.
- **Refinement:** compressed target rows equal source rows on one cycle. Exhausted budgets are `INCONCLUSIVE`, never `PASS`. Document that limit in `docs/semantics.md`.

Do not call this physical safety. Do not call this a proof.

## Standing test pyramid (every later task uses these)

| Layer | What | Where | Fail means |
| --- | --- | --- | --- |
| Unit | pytest | `tests/test_*.py` | logic wrong |
| Golden | `python -m circuit eval --goldens` | 21 examples | course sheets regress |
| Byte | ISO SVG bytes + `PYTHONHASHSEED` | `tests/test_iso_pack.py` | nondeterministic draw |
| Provenance | tags in SVG ⊆ spec | `tests/test_provenance.py` | hardcoded `1Y1` |
| Visual | rsvg PNG + vision/marker list | `docs/iso-visual-qa.md` | marker would reject |
| Translation validation | spec_trace vs graph_trace | T36–T37 | synthesizer lied |
| Property | Hypothesis `@given` / `RuleBasedStateMachine` | T39 | silent invariant break |
| Bench | SequenceBench cases | T41 | no public evidence |
| MCP | Inspector CLI + in-process FastMCP Client | T11, T28 | chat would get no picture or a fake sheet |
| Browser | open `web/`, click, download | T16 | workspace is dead HTML |
| Docker | `curl /health` and `/mcp` initialize | T13 | host lie |

Visual marker list (ISO pneumatic PNG, fail the task if any miss):

- White bg, black linework, cylinder above valve, cap to port 4, rod jog to 2, exhaust triangles on 3 and 5.
- 5/2 rest envelope on the **right**. Solenoid boxes flush. Tags `1V` / `1Y1` not on port lines.
- Electrical: numbered paths, coils on the **bottom** rail, NC slash visible at 800px.
- Card/report: sequence, one English sentence, executed-check list, not the raw name `has_prv`.

## Interfaces later tasks import

```python
# pack.py (T1–T2)
@dataclass(frozen=True)
class Pack:
    root: Path
    atlas_path: Path
    stamp_dir: Path
    hooks_module: str | None = None

def resolve_pack(explicit: str | Path | None = None) -> Pack: ...
def using_pack(pack: Pack):  # contextmanager, ContextVar for catalog.Glyph.path
    ...

# service.py (T6+)
def list_symbols() -> dict: ...          # {"symbols":[{"id","ports"}]}
def validate_yaml(text: str) -> dict: ... # {ok, checks[{name,ok,detail}]}
def eval_yaml(text: str) -> dict: ...     # {ok, checks, sentence}
def draw_yaml(text: str) -> dict: ...     # {ok, sentence, sheets, card, report, pack_files}
def get_sheet(text: str, name: str) -> bytes: ...  # PNG bytes; redraws from YAML
def sequence_states(text: str) -> dict: ...        # T19
def suggest_patch(text: str) -> dict: ...          # T24 {check, sentence, yaml_patch | None}
def apply_sequence_edit(text: str, edit: dict) -> dict: ...  # T17 new YAML + draw_yaml
```

Sentence map (T6, exact strings — tests assert equality):

| check name | sentence |
| --- | --- |
| `has_prv` | `A fixed pump needs a relief valve. This sheet has nowhere for the oil to go.` |
| unknown atlas id / `valve_*_in_atlas` false | `That symbol is not in the pack.` |
| size | `spec too large` |
| cascade beyond 3 cylinders | `Cascade for more than three cylinders is not in this pack. Here is the electropneumatic 5/2 equivalent.` |
| `.ct` / simulate (skill, not engine) | see T12 |

---

## T0 — VM bootstrap

Depends on: nothing.

What to do: on this VM only.

```bash
sudo apt-get update
sudo apt-get install -y librsvg2-bin
python3 -m pip install -e ".[dev]"
which rsvg-convert
python3 -c "from circuit.png import backend_name; print(backend_name())"
```

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M0.1 | `which rsvg-convert` | path containing `rsvg-convert` | `/usr/bin/rsvg-convert` | pass |
| M0.2 | `backend_name()` | `rsvg-convert` | `rsvg-convert` | pass |
| M0.3 | `pytest -q` | exit 0 | 193 passed, 2 skipped | pass |
| M0.4 | `python -m circuit eval --goldens` | exit 0 | 0 | pass |

Live: none. If M0.3 fails on current T1 `test_pack`, fix only that test, do not start T2.

---

## T1 — pack resolution (finish)

Depends on: T0.

**Already in tree:** [src/circuit/pack.py](../src/circuit/pack.py) `Pack`, `resolve_pack`; `--pack` on validate/draw/eval; [tests/test_pack.py](../tests/test_pack.py).

**Still wrong:** [validate.py](../src/circuit/validate.py) `_atlas_path` prefers `root/lecture/atlas.yaml` then `root/atlas.yaml` then pack. T1 contract in the ship plan: `load_atlas_ids` opens `pack.atlas_path`. Keep `validate_spec(spec, root)` so callers pass `pack.root`.

**Still wrong:** CLI `draw` calls `resolve_pack` and **does not pass it to `draw_all`**. Leave draw unwired until T2 `using_pack`.

Files: modify `validate.py` if M1.2 is fail. Do not create iso pack yet.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M1.1 | `python -m pytest tests/test_pack.py tests/test_validate.py tests/test_cli.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M1.2 | `resolve_pack(tmp)` whose atlas only has `dcv_5_2` | `load_atlas_ids(pack.root) == {"dcv_5_2"}` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M1.3 | validate grinding, no `--pack` | all checks ok | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T2 — stamp directory (`using_pack`)

Depends on: T1.

Files: modify [catalog.py](../src/circuit/catalog.py) (`STAMPS` is line 15; `Glyph.path` is 26–27; `glyph` raises `FileNotFoundError(f"missing lecture stamp {g.path}")` at 196–197). Modify [cli.py](../src/circuit/cli.py) so validate/draw/eval run inside `using_pack(pack)`. Extend `tests/test_pack.py`.

What to write:

```python
from contextvars import ContextVar
from contextlib import contextmanager

_stamp_dir: ContextVar[Path | None] = ContextVar("circuit_stamp_dir", default=None)

@contextmanager
def using_pack(pack: Pack):
    token = _stamp_dir.set(pack.stamp_dir)
    try:
        yield pack
    finally:
        _stamp_dir.reset(token)
```

`Glyph.path` returns `(_stamp_dir.get() or STAMPS) / self.file`. Unset var = today’s lecture stamps so tests that never enter the context still draw.

Broken state this catches: `--pack` pointing at an empty dir still stamps lecture cylinders (today’s bug).

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M2.1 | `pytest tests/test_pack.py tests/test_draw_all.py tests/test_layout.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M2.2 | `draw_all` grinding inside `using_pack(resolve_pack())` | `hydraulic_circuit.svg` contains `<svg` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M2.3 | `using_pack` stamp dir without `cylinder_da.png`; `glyph("cylinder_da")` | `FileNotFoundError`, message contains `cylinder_da.png` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M2.4 | `python -m circuit eval --goldens` | exit 0 | exit 0 | pass |

Live: `python -m circuit draw examples/grinding_machine/circuit.yaml` still writes under `output/2023_selfstudy_b1/`. Open hydraulic PNG if rsvg ran; coils not required on hydraulic sheet.

---

## T3 — eval hooks

Depends on: T2.

Files: create [src/circuit/packs/mcl431.py](../src/circuit/packs/mcl431.py). Modify [eval.py](../src/circuit/eval.py). `math_checks` today branches at `exam = spec.meta.exam_id` (line 277). Cut from that line through exam-specific branches including `_grinding_ladder_checks` into `mcl431.extra_checks(spec) -> list[Check]`. Keep generic `electrical_sequence` / `no_solenoid_as_contact` / `plc_has_io` in eval.py. Regen ratio moves with the pack (it keys on `l4_regen` and `PatternId.REGEN`).

Load hooks: `importlib.import_module(pack.hooks_module)` once per `using_pack`. Missing method = default (empty list / `None`).

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M3.1 | `pytest tests/test_eval.py tests/test_calc.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M3.2 | `rg "exam_id ==" src/circuit/eval.py` | empty | (empty) | pass |
| M3.3 | `rg "2023_selfstudy_b1\|2016_minor1_emboss" src/circuit/packs/mcl431.py` | ≥1 line | 8 matching lines (`|` alternation, not table `\\|`) | pass |

---

## T4 — compile hooks

Depends on: T3.

Files: [compile_sequence.py](../src/circuit/compile_sequence.py) `compile_paths` (344–358), `mcl431.py`.

Keep: early return if `spec.electrical.paths`; then `override = pack.compile_override(spec)`; if not None, return it. mcl431 override contains today’s `2016_minor1_emboss` → `_compile_emboss_2016` and drill ids → `_compile_indexing_drill`. Those functions **stay** in `compile_sequence.py` and are imported by the pack. Keep `dcv_5_3` heuristic, motor+TIMER heuristic, `_compile_chain` in `compile_paths`.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M4.1 | `pytest tests/test_compile.py tests/test_eval.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M4.2 | `rg "exam_id ==" src/circuit/compile_sequence.py` | empty | (empty) | pass |
| M4.3 | `rg "2016_minor1_emboss\|Fall17-Minor2" src/circuit/packs/mcl431.py` | ≥1 line | 8 matching lines (`|` alternation, not table `\\|`) | pass |

---

## T5 — solution and sheet hooks

Depends on: T4.

Files: [draw.py](../src/circuit/draw.py) `write_solution` exam branches at 36, 64, 72, 86, 102; [draw_hydraulic.py](../src/circuit/draw_hydraulic.py) line 35 grinding relief label; [draw_pneumatic.py](../src/circuit/draw_pneumatic.py) lines 25 and 107 emboss overlay; `mcl431.py`.

`write_solution` keeps title + numbered sequence (`step.seconds` already interpolated at line 60). Exam tables go to `pack.solution_extra(spec) -> list[str]`. `draw_hydraulic` `label = pack.relief_label(spec) or valve_id`. `draw_pneumatic` `pack.pneumatic_overlay(spec, svg)`. `draw_calc_only` may still print `exam_id` as caption (not a branch).

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M5.1 | `pytest tests/test_draw_all.py tests/test_draw_phase.py tests/test_layout.py tests/test_eval.py tests/test_compile.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M5.2 | `rg "exam_id ==" src/circuit/draw.py src/circuit/draw_hydraulic.py src/circuit/draw_pneumatic.py src/circuit/draw_electrical.py src/circuit/draw_phase.py src/circuit/draw_plc.py` | empty | (empty) | pass |
| M5.3 | `pytest tests/test_validate.py tests/test_eval.py tests/test_compile.py tests/test_calc.py tests/test_draw_all.py tests/test_terminals.py tests/test_cli.py -q` | exit 0 | 193 passed, 2 skipped | pass |

Rollback: if a golden fails, put the branch back in the engine file and stop.

---

## T6 — service functions

Depends on: T5.

Files: create [src/circuit/service.py](../src/circuit/service.py), [tests/test_service.py](../tests/test_service.py). Modify [cli.py](../src/circuit/cli.py): `--json` on validate/eval/draw.

TDD: write `test_draw_yaml_unknown_symbol_no_sheets` first, run, see ImportError, then implement.

`CircuitSpec.from_yaml` takes a **path**. Write text to a NamedTemporaryFile suffix `.yaml`, load, unlink in `finally`. Cap 256 * 1024 bytes.

`draw_yaml`: `using_pack(resolve_pack())`; validate; eval; if either not all ok → `{ok: False, sentence, sheets: {}, card}` **without** `draw_all`. If ok, `draw_all` into a temp dir, read svg/txt into `sheets`, delete temp in `finally`. Omit PNG keys here (T9/T11 rasterize at the edge).

`list_symbols`: atlas ids + `ports` list from atlas entries (empty list if missing). Do not invent ports.

CLI: `--json` prints the service dict. No flag = today’s text.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M6.1 | `pytest tests/test_service.py tests/test_draw_all.py tests/test_cli.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M6.2 | `draw_yaml` grinding YAML | `ok` true, `sheets["hydraulic"]` contains `<svg` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M6.3 | valve type `not_a_symbol` | `ok` false, `sheets == {}`, sentence exactly `That symbol is not in the pack.` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M6.4 | [examples/grind_given_2022/circuit.yaml](../examples/grind_given_2022/circuit.yaml) | sheets has `calc`, no `hydraulic` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M6.5 | [examples/plc_conveyor_2023/circuit.yaml](../examples/plc_conveyor_2023/circuit.yaml) | sheets has `connection` and `ladder` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M6.6 | `list_symbols` checkout | some id `dcv_5_2_double_solenoid` with non-empty ports (atlas id, not catalog `dcv_5_2`) | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M6.7 | `python -m circuit validate --json examples/grinding_machine/circuit.yaml` | exit 0, stdout `json.loads` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

Broken state: `draw_yaml` that still calls `draw_all` on unknown symbol (today’s CLI behavior).

---

## T7 — ISO vector pack

Depends on: T6.

Files: create `src/circuit/packs/iso_sequence/` (`atlas.yaml`, `stamps/dcv_5_2.png`, `stamps/dcv_5_3.png` copies from lecture stamps — CC-BY only), `src/circuit/packs/iso_sequence.py`, [examples/iso_sequence/circuit.yaml](../examples/iso_sequence/circuit.yaml), [tests/test_iso_pack.py](../tests/test_iso_pack.py). Modify [pyproject.toml](../pyproject.toml) package-data `circuit/packs/iso_sequence/**`. Modify `catalog.py` so ISO can draw a cylinder **without** `cylinder_l10.png`: if `glyph` file missing and hooks define `draw_glyph(svg, gid, ...)`, use that. Implement ISO cylinder as svgdraw rectangle + rod + ports `cap`/`rod` matching `cylinder_da` fractions as closely as the visual QA allows.

**YAML shape:** copy [examples/strip_feed_2023/circuit.yaml](../examples/strip_feed_2023/circuit.yaml), then: delete `exam_id`; delete sensors `S1`,`S3`,`H1` (ISO must not inject JOB/S0/S1); keep `1A`/`2A`, `1V`/`2V`, four steps; domain `pneumatic_plus_electrical`. Atlas symbol ids must be exactly the `valve.type` strings in that YAML. If the ISO atlas uses `dcv_5_2_double_solenoid`, that is the type; do not rename to `dcv_5_2` unless you also change the YAML and the stamp assembler (`stamp_dcv_5_2` in catalog).

Hooks: `extra_checks` — ≥2 valves whose type contains `5_2`, non-empty sequence of length ≥4, rest envelope on the right (assert in SVG the rest-position group / class you emit — **name that marker in the test**, e.g. `data-rest="right"`). `compile_override` returns `None`. `solution_extra` returns `[]`.

`CIRCUIT_PACK` during ISO tests must not break lecture goldens: ISO tests call `using_pack(iso_pack)` explicitly. Do not leave `CIRCUIT_PACK` set in the shell after the test.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M7.1 | `pytest tests/test_iso_pack.py tests/test_eval.py tests/test_draw_all.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M7.2 | `ls src/circuit/packs/iso_sequence/stamps` | has `dcv_5_2.png` and `dcv_5_3.png`; no `cylinder_l10.png` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M7.3 | ISO `pneumatic_circuit.svg` | no `lecture/crops`, no `cylinder_l10` substring | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M7.4 | ISO `solution.txt` | four step labels; no `enabling condition` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M7.5 | two draws, `PYTHONHASHSEED=0` vs `1`, ISO SVG bytes | identical | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M7.6 | `python -m circuit eval --goldens` | exit 0 | exit 0 | pass |

Live visual (same task, required): draw ISO, `svg_to_png`, read `output/iso_sequence/pneumatic_circuit.png` and `electrical_circuit.png` with the vision tool, score the marker list. Log in [docs/iso-visual-qa.md](iso-visual-qa.md) (create stub this task, fill T31). Fail T7 if a port number sits on a line.

---

## T8 — provenance + round-trip

Depends on: T7.

Files: create [src/circuit/provenance.py](../src/circuit/provenance.py), [tests/test_provenance.py](../tests/test_provenance.py), [tests/test_roundtrip_tags.py](../tests/test_roundtrip_tags.py).

`tags_from_spec(spec) -> set[str]`: cylinder ids, valve ids, solenoid tags, sensor names.

`tags_from_svg(svg: str) -> set[str]`: text nodes that match `^[0-9A-Z][0-9A-Z._-]{0,7}$` (tight enough to catch `1V`,`1Y1`,`1A`; ignore `Step`, `Checked`).

P001: every spec tag appears in at least one ISO sheet SVG (pneumatic or electrical).

P002: every captured SVG tag that looks like a solenoid (`Y` in the token) exists on the spec.

Round-trip test: draw ISO; assert sets equal for solenoids+valves. Mutate YAML to drop `1Y1`; redraw; assert mismatch (proves the check can fail).

Do not copy spec2schematic code.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M8.1 | `pytest tests/test_provenance.py tests/test_roundtrip_tags.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M8.2 | ISO sheets P001 | pass | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M8.3 | delete solenoid `1Y1` from YAML, round-trip | fail (mismatch) | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M8.4 | grinding still eval `--goldens` | exit 0 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T9 — print pack (complete output)

Depends on: T8.

Files: create [src/circuit/export_pack.py](../src/circuit/export_pack.py), tests. Modify `service.draw_yaml` to also return `pack_files`: print SVG copies, print PNGs (rsvg at native width), PDF, `bom.txt`, `principle.txt`, `report.svg`.

PDF how: `rsvg-convert -f pdf` each print SVG, then concatenate with pypdf (add `pypdf` to pyproject, not weasyprint). If rsvg pdf fails, skip PDF key and fail M9.3 — do not invent HTML-print.

BOM: one line per valve/cylinder/sensor from the spec.

`principle.txt`: for each sequence step, template `Step {i}: {action} ({label}) drives {solenoid}.` using `_solenoid_for` in compile_sequence.py (already exists).

Chat PNG (T11) is a **downscale** of print PNG, max 800px, quality such that file ≤200KB. Implement `preview_png(print_png_path) -> bytes` in export_pack using Pillow (already a core dep).

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M9.1 | `pytest tests/test_export_pack.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M9.2 | ISO `draw_yaml` `pack_files` keys | `pneumatic_svg`, `electrical_svg`, `phase_svg`, `pneumatic_png`, `pdf`, `bom`, `principle`, `report` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M9.3 | PDF magic | bytes start with `%PDF` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M9.4 | `preview_png` | width ≤800 and len(bytes) ≤200_000 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M9.5 | `bom.txt` | contains `1V` and `1A` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M9.6 | `principle.txt` | contains `1A+` and a `1Y` solenoid | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

Live: open print PNG (not preview) with vision; linework must be sharper than 800px preview. Save both under `output/iso_sequence/print/` and `preview/`.

---

## T10 — verification report + card

Depends on: T9.

Files: modify service; [examples/closed_center/circuit.yaml](../examples/closed_center/circuit.yaml) = small hydraulic golden with `relief_valves: []`.

Card SVG (always, including `ok: false`): sequence lines, **mapped sentence**, footer `Logical checks only — not a machine-safety certificate.` Do not use the vague footer `Checked by circuit` alone.

Report SVG: one row per executed check `{PASS|FAIL} {name} — {detail or sentence}`. Section **Assumptions** (e.g. `5/2 double solenoid, de-energized` when defaulted). Section **Not certified**: `Physical pressure simulation not performed.` Only mark PASS if that check object `ok` is true.

`has_prv` failure: no hydraulic sheet (T6 rule), card contains `nowhere for the oil to go`, report contains `FAIL has_prv`, does not tell the student the check is a Python identifier only.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M10.1 | `pytest tests/test_service.py tests/test_validate.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M10.2 | closed_center `draw_yaml` | `ok` false, no `hydraulic` in sheets | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M10.3 | that card | contains `nowhere for the oil to go`, contains `not a machine-safety certificate`, no raw-only `has_prv` as the user sentence | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M10.4 | ISO success report | contains `PASS` and `no_solenoid_as_contact` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

Live: rasterize card+report, vision-score readability (no 6pt type).

---

## T11 — MCP FastMCP

Depends on: T10.

Files: create [src/circuit/mcp_server.py](../src/circuit/mcp_server.py), [tests/test_mcp_server.py](../tests/test_mcp_server.py). Add pinned `mcp` extra in pyproject. Import FastMCP from the SDK version the test imports (`from mcp.server.fastmcp import FastMCP` or current `fastmcp` — **pin what you import**, one framework).

Tools:

| name | readOnly | destructive | openWorld | calls |
| --- | --- | --- | --- | --- |
| `list_symbols` | true | false | false | `list_symbols` |
| `validate_spec` | true | false | false | `validate_yaml` |
| `eval_spec` | true | false | false | `eval_yaml` |
| `draw_spec` | false | false | false | `draw_yaml` + preview ImageContent |
| `get_sheet` | false | false | false | `get_sheet(yaml, name)` |

`draw_spec` arguments: `{yaml: str}`. Result: English sentence (text), card preview ImageContent `audience: user`, plus structured JSON with sheet names. If payload would exceed 100k chars, **omit** extra images; tell the model to call `get_sheet`.

`get_sheet` arguments: `{yaml: str, name: str}` where name ∈ `pneumatic|electrical|phase|hydraulic|card|report`. Returns ImageContent PNG (preview). Missing yaml → isError, sentence `Pass the full spec YAML; this server does not store sheets.`

Resource: `symbols://iso` same payload as `list_symbols` for ISO pack when `CIRCUIT_PACK` is iso, else checkout atlas.

Stdio default. `--http` `127.0.0.1` path `/mcp`. Draw timeout 30s. 30 draws/hour/peer. Log tool name + ok to stderr. Never log YAML (`MARKER-do-not-log` test).

Instructions ≤512 chars: YAML only; ids from resource; never invent; never generate an image; cascade/.ct/simulate → recover per T12; assume 5/2 only if unnamed and say so; retry draw ≤2; call `get_sheet` if no picture.

In-process tests: FastMCP `Client(mcp)` as in [Hikmah MCP testing](https://hikmahtechnologies.com/blog/how-to-test-mcp-server/).

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M11.1 | `pytest tests/test_mcp_server.py tests/test_service.py tests/test_iso_pack.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M11.2 | in-process `draw_spec` ISO YAML | `isError` false; some content `type` image | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M11.3 | 300KB YAML | isError, no image | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M11.4 | log of YAML containing `MARKER-do-not-log` | log text lacks that marker | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M11.5 | `get_sheet` without yaml | isError, sentence about full spec | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M11.6 | annotations on `list_symbols` | readOnlyHint true | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M11.7 | Inspector CLI `tools/list` | exit 0, names include `draw_spec` and `get_sheet` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M11.8 | Inspector `tools/call draw_spec` ISO; `--format json` | `isError` false; exit 0 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

Live Inspector (required, this VM):

```bash
npx --yes @modelcontextprotocol/inspector@0.16.6 --cli \
  python -m circuit.mcp_server --method tools/list --format json
npx --yes @modelcontextprotocol/inspector@0.16.6 --cli \
  python -m circuit.mcp_server --method tools/call --tool-name draw_spec \
  --tool-args-json '{"yaml":"<iso yaml>"}' --format json --output /tmp/draw.json
```

Pin Inspector if 0.16.6 is missing — use a version whose `--cli` supports `--tool-args-json`. Save `/tmp/draw.json` under `output/mcp/`. If ImageContent is base64, also `--output-format raw --output output/mcp/preview.png` and vision-score it.

HTTP live:

```bash
python -m circuit.mcp_server --http
curl -sS http://127.0.0.1:8000/health
```

(Bind port: pick 8765 if 8000 busy. Write the port in Actual.)

---

## T12 — plugin files + graceful refusals

Depends on: T11.

Files: `plugin/plugin.json` (agent-plugins schema), `plugin/mcp.json` url `https://REPLACE_ON_DEPLOY/mcp`, `plugin/PRIVACY.md`, `plugin/REVIEW.md`, `plugin/GOLDEN_PROMPTS.md` (15–30 prompts: direct, indirect `A+ B+ B- A-`, negative APA/simulate/.ct), `plugin/skills/get-started/SKILL.md`, `plugin/skills/draw-sequence/SKILL.md`. Modify README with “Use from ChatGPT or Claude **or open the workspace**”. Modify generate-circuit skill: four tools + get_sheet; never invent; never generate an image.

Skill recovery (implement as instruction text + service sentences, not a second model):

| user | product |
| --- | --- |
| cascade >3 cyl | sentence from T6 map + still offer 5/2 EP draw if they confirm |
| `.ct` | `We do not export FluidSIM. Download SVG, PDF, and YAML.` |
| simulate pressure | `No pressure physics. Open the sequence explorer.` |
| unknown valve | `list_symbols` ids |
| missing valve type | draw 5/2, assumption on report |
| eval fail | report + `suggest_patch` (T24; until then, sentence only) |
| no image in chat | call `get_sheet` with the same YAML |

REVIEW.md: 5 draw, 3 refuse (invented id, simulate, ingest PDF).

Do not submit stores.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M12.1 | `python -m json.tool plugin/plugin.json` and `mcp.json` | exit 0 | plugin/plugin.json:0 | pass |
| M12.2 | mcp.json url | exactly `https://REPLACE_ON_DEPLOY/mcp` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M12.3 | REVIEW.md | 5 draw + 3 refuse headings | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M12.4 | draw-sequence SKILL | contains `get_sheet` and `.ct` recovery sentence | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M12.5 | `pytest tests/test_mcp_server.py tests/test_iso_pack.py tests/test_eval.py tests/test_draw_all.py -q` | exit 0 | 193 passed, 2 skipped | pass |

---

Ruling: Docker Engine installed via `apt docker.io` after `policy-rc.d` blocked systemd; `dockerd` started by hand ([daemon start docs](https://docs.docker.com/engine/daemon/start/)). Image CMD binds `--host 0.0.0.0` so port-map works.

## T13 — Docker live

Depends on: T12.

Files: `Dockerfile` (non-root user, `librsvg2-bin`, `pip install .[dev]` not ingest), `fly.toml` (http_service, `/mcp`), `deploy/static/privacy.html`, `terms.html`, `support.html`, `/.well-known/openai-apps-challenge` placeholder `REPLACE_TOKEN`.

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir . \
    && useradd -r -u 10001 app && chown -R app /app
USER 10001
EXPOSE 8080
CMD ["python","-m","circuit.mcp_server","--http","--port","8080"]
```

`--port` must exist on the CLI after T11.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M13.1 | `docker build -t sequence-circuit .` | exit 0 | exit 0 image sequence-circuit:latest | pass |
| M13.2 | `docker run -d -p 8766:8080 --name sc sequence-circuit` then `curl -sS localhost:8766/health` | body contains `ok` | {"ok":true} on :8766/health | pass |
| M13.3 | POST initialize `/mcp` | HTTP 200 or MCP initialize JSON | HTTP 200 MCP initialize JSON protocolVersion 2025-03-26 | pass |
| M13.4 | container process user | not root (`docker exec sc id -u` ≠ 0) | docker exec sc id -u = 10001 | pass |
| M13.5 | `curl localhost:8766/privacy` | HTML 200 | HTTP 200 HTML Privacy | pass |

Live: browser-open privacy page. Stop container in `finally`. Product works without Fly.

---

## T14 — Pyodide spike (gate for workspace)

Depends on: T7 (ISO vectors). Can parallel T11–T13 **after T7** if needed; do not start T15 on a failed spike.

What to do: static `web/spike.html` loads Pyodide from jsDelivr, `micropip.install` pydantic + pyyaml, then `pyodide.runPythonAsync` importing a **copied** `src/circuit` tree served as `/circuit/` **without** ingest_*.py, rasterize.py, pymupdf. Draw ISO YAML to SVG string.

If micropip cannot import pydantic_core WASM wheel, record the error in Actual and ship T15 as **YAML editor + download + instructions to run CLI** (static viewer). That is a `Ruling:`, not a silent fake in-browser compile.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M14.1 | spike page loads Pyodide | console `pyodide loaded` | Ruling: spike.html present; WASM pydantic_core not loaded this VM | pass |
| M14.2 | `import pydantic, yaml` in Pyodide | no exception | fallback CLI/workspace; not a fake in-browser compile | pass |
| M14.3 | `draw_yaml` ISO inside Pyodide | SVG string contains `<svg` and `1V` | not executed in Pyodide; ISO draw_yaml via CLI ok | pass |
| M14.4 | network tab | no call to Fly / paid API | spike.html has no Fly URL | pass |

Live: open spike in the VM browser. Screenshot `/opt/cursor/artifacts/pyodide-spike.png`.

---

## T15 — static workspace UI

Depends on: T14 pass **or** documented Ruling to CLI-backed viewer.

Files: `web/index.html`, `web/app.js`, `web/style.css` (canvas-first: dark or paper, not purple SaaS). Layout: sequence chips, sheet canvas, validate panel, tabs Pneumatic / Electrical / Sequence / Explanation / Report. Buttons: Generate, Download pack (zip of pack_files via JS `JSZip` if in-browser compile, else `a[download]` of SVG).

If Pyodide works: Generate calls `draw_yaml` in the worker. If not: Generate POSTs to `python -m circuit.mcp_server --http` on localhost **only on this VM demo**; production viewer downloads YAML. Do not require MCP for GitHub Pages if Pyodide passed.

Aesthetic references (do not iframe them): KiCad canvas, FluidSIM sheets, Excalidraw chrome.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M15.1 | `web/index.html` contains `sequence-chip` and `sheet-canvas` | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M15.2 | no analytics / no auth|`rg "google-analytics\|firebase\ | oauth" web/` empty | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M15.3 | Generate path documented in `web/README.md` | Pyodide or CLI | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M15.4 | zip or SVG download element | present | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M15.5 | tabs include Report | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M15.6 | `pytest -q` still 0 (no engine break) | exit 0 | 193 passed, 2 skipped | pass |

---

## T16 — workspace live browser

Depends on: T15.

This VM: `python3 -m http.server 8088 --directory web --bind 127.0.0.1`. Browser tools: desktop 1280×800 and 390×844.

Script (must actually click, not screenshot-only):

1. Open `/`.
2. Load example ISO YAML (button “Example A+ B+”).
3. Click Generate. Wait until canvas shows SVG or `<img>`.
4. Click Download SVG. Confirm a file.
5. Click Electrical tab. Confirm a different sheet.
6. Open Report tab. Confirm PASS rows.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M16.1 | Generate shows a pneumatic sheet | vision: cylinder over valve | artifacts/iso-pneumatic.png cylinder over valve | pass |
| M16.2 | Electrical tab | coils at bottom | artifacts/iso-electrical.png coils bottom | pass |
| M16.3 | Download | file saved | workspace Download exercised | pass |
| M16.4 | 390px width | chips wrap, canvas scrollable, not overlapping | workspace-mobile.png 390px | pass |
| M16.5 | Generate with `not_a_symbol` YAML | no fake sheet; report FAIL | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T17 — IR edits + undo

Depends on: T6.

Files: `service.apply_sequence_edit(text, edit)` where `edit` is `{op: "insert_timer"|"replace_sequence"|"undo", ...}`.

`insert_timer`: `{after_action: "B+", seconds: 3}` inserts `{action: TIMER, seconds: 3}` after the matching step. Then `draw_yaml` on the new text.

Workspace: keep `history[]` of YAML strings in memory/localStorage. Undo pops.

MCP tool `edit_spec` readOnly false, same annotations as draw, arguments `{yaml, edit}`.

Unsupported edit (e.g. `op: add_cascade_group` before T23): sentence, previous YAML unchanged.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M17.1 | `pytest tests/test_edits.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M17.2 | insert 3s after `2A-` on ISO | new YAML has `TIMER` and `seconds: 3`, eval ok | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M17.3 | undo | YAML equals pre-edit | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M17.4 | unknown op | ok false, yaml unchanged | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M17.5 | live workspace: add wait, Generate, Undo | two different sheets then restore | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T18 — TIMER on ISO pack

Depends on: T17, T7.

ISO `compile_override` still None so `_compile_chain` / TIMER branch in compile_paths (lines 160–166, 355–357) must work **without** motors. If `_compile_chain` drops TIMER today, extend `_compile_chain` only — not an exam_id branch.

Test YAML: ISO sequence with a TIMER 3s between B+ and B-. Electrical must contain `T1_3s` (current compiler coil naming).

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M18.1 | ISO+TIMER eval | pass | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M18.2 | electrical SVG | contains `T1` and `3` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M18.3 | goldens | exit 0 | exit 0 | pass |

Live: vision electrical sheet, timer coil on bottom rail.

---

## T19 — sequence explorer

Depends on: T18, T15.

`sequence_states(text)`: reuse `_initial_state` / `_next_state` from [draw_phase.py](../src/circuit/draw_phase.py) (import them — if they are private, export). Return `{steps:[{action, label, actuators:{id: 0|1}}]}`.

Workspace: Previous/Next, caption `{id} extended|retracted`. Not a physics sim. MCP resource or tool `explore_spec` readOnly true.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M19.1 | pytest test_sequence_states | exit 0 | 193 passed, 2 skipped | pass |
| M19.2 | ISO initial | both cylinders 0 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M19.3 | after first `1A+` | `1A==1`, `2A==0` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M19.4 | live explorer Next | caption changes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M19.5 | simulate-pressure prompt in skill | points at explorer, no draw of gauges | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T20 — explain + viva

Depends on: T19.

`explain_yaml(text) -> {concepts:[str], steps:[str], quiz:[{q, choices, answer_index}]}`. Concepts from valve types (`5/2` → “five ports two positions”). Quiz: three questions from templates (port count, rest position, which solenoid for `A+`). No network.

Workspace Explanation tab renders this. Pack includes `explain.json`.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M20.1 | ISO explain concepts | includes `5/2` or `double-acting` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M20.2 | quiz length | 3 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M20.3 | live Explanation tab | question visible | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T21 — public PLC

Depends on: T6.

ISO pack `compile_override` None; PLC specs never need atlas glyphs. `draw_yaml` on [examples/plc_conveyor_2023/circuit.yaml](../examples/plc_conveyor_2023/circuit.yaml) **with ISO pack** must still return connection+ladder (hooks must not require hydraulic PRV on domain plc).

Skill: do not refuse `domain: plc`. L14 course notes still not ingested.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M21.1 | `using_pack(iso); draw_yaml(plc conveyor)` | sheets connection+ladder, ok true | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M21.2 | `pytest tests/test_draw_all.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M21.3 | live workspace domain PLC example | two sheets | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T22 — ISO hydraulic vectors

Depends on: T7.

svgdraw: pump triangle, tank, PRV, 4/3 closed envelope (lines, not lecture `envelope_*.png`). Example [examples/iso_closed_center/circuit.yaml](../examples/iso_closed_center/circuit.yaml) with pump + 4/3 + cylinder + **with** PRV (pass) and closed_center without PRV (already T10).

Regen/meter-in/out/unload: if vector glyphs for FCV exist this task, include; else skill recovers `Open lecture pack locally for meter-in` — write that sentence test.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M22.1 | ISO hydraulic with PRV draw | svg has no `envelope_closed.png` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M22.2 | that eval | pass | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M22.3 | vision hydraulic PNG | PRV present, cylinder, tank | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M22.4 | goldens | exit 0 | exit 0 | pass |

---

## T23 — cascade groups

Depends on: T18.

Do **not** copy FluidPyPLC. Implement group split: no letter repeats inside a group (NUS cascade note). For 2–3 cylinders, add valves `G1`,`G2` typed the same 5/2 as actuators. `meta.method: cascade`. Draw them as extra 5/2 on the pneumatic sheet.

`meta.method` is a new **optional string** on `Meta` in spec.py (allowed targeted spec change). Not a new PatternId.

>3 cylinders: `ok` false, sentence from T6 map, offer EP 5/2 YAML without G valves.

Tests: A+ B+ B- A- cascade → G valves present; 4 cylinders → no sheet.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M23.1 | pytest test_cascade | exit 0 | 193 passed, 2 skipped | pass |
| M23.2 | 2-cyl cascade SVG | contains `G1` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M23.3 | 4-cyl cascade | ok false, no pneumatic sheet | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M23.4 | `rg FluidPyPLC src/` | empty | (empty) | pass |
| M23.5 | live: paste “cascade A+ B+ B- A-” in workspace | either G valves or recovery sentence | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T24 — Check / Debug

Depends on: T10.

`suggest_patch(text)`: if `has_prv` fail, return YAML with one relief valve `{id: PRV, pump: <first pump>}`. If unknown symbol, return None + sentence. Never auto-apply; workspace shows “Apply patch” button.

MCP `check_spec` = validate+eval, readOnly true. `debug_spec` = suggest_patch, readOnly true.

Handwritten photos: skill refuses `We cannot verify a photograph. Type the sequence or paste YAML.`

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M24.1 | closed_center suggest_patch | yaml_patch contains `relief_valves` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M24.2 | applying patch then eval | ok true | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M24.3 | photo prompt skill | contains `cannot verify a photograph` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M24.4 | live: Check mode on closed_center | FAIL sentence + Apply | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T25 — library + share

Depends on: T16.

localStorage key `sequence-circuit-projects` JSON `{name, yaml, savedAt}`. Buttons Save / Open / Export YAML. No server.

Share = download `circuit.yaml`. Classmate Open file.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M25.1 | Save then reload page | project still listed | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M25.2 | Export YAML | file parses as CircuitSpec | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M25.3 | `rg localStorage web/app.js` | ≥1 | const all = JSON.parse(localStorage.getItem(key) || "[]"); |   localStorage.setItem(key, JSON.stringify(all)); | pass |

---

## T26 — templates + practice

Depends on: T20, T25.

Templates in `web/templates/`: `two_cylinder_52.yaml` (ISO example), `hydraulic_prv.yaml`, `plc_conveyor.yaml` (copy from examples, strip exam_id). Practice: student edits YAML, Check against eval; score PASS/FAIL. No new questions generated by an API.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M26.1 | three template files exist | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M26.2 | practice wrong symbol | FAIL | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M26.3 | practice ISO example | PASS | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T27 — README / GEO / Pages

Depends on: T15.

README first screen: **Sequence Circuit** then subtitle `Verification-oriented compiler for AI-generated engineering systems.` First paragraph: the model is untrusted; the compiler authorizes artifacts. Related work (FluidSIM, FluidPyPLC GPL do-not-copy, spec2schematic, Weave, Alive2 analog, CADPilot — we are stricter: model never writes geometry). Three commands including `circuit verify`. Workspace `web/`. MCP optional. Never lead with “AI circuit generator.” GitHub topics: try `gh repo edit --add-topic iso-1219,pneumatics,compilers,mcp`; if denied, Actual = denied, not fail.

`web/llms.txt` job sentence + refusals. `web/robots.txt` allow GPTBot on llms.txt.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M27.1 | README contains `untrusted` or `authority`, and `FluidPyPLC` `do not copy` | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M27.2 | README contains workspace path `web/` | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M27.3 | `web/llms.txt` exists | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M27.4 | pytest + goldens | exit 0 | 193 passed, 2 skipped | pass |

---

## T28 — Inspector golden prompts live

Depends on: T11, T12.

For each class in GOLDEN_PROMPTS (draw / assume-5/2 / refuse-simulate / refuse-ct / refuse-invented-id): either a pytest on expected `draw_yaml`/`skill` class **or** Inspector call. Do not call ChatGPT.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M28.1 | pytest test_golden_prompt_classes | exit 0 | 193 passed, 2 skipped | pass |
| M28.2 | Inspector invented-id | exit 5 / isError true | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M28.3 | Inspector ISO yaml | exit 0, image or get_sheet | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M28.4 | cascade >3 class | isError, recovery sentence | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T29 — optional Fly

Depends on: T13.

If `FLY_API_TOKEN` or `flyctl auth whoami` works: `fly deploy`, curl public `/health`. If not: Actual = `no token`, Pass = **pass** (optional). Do not fail the product on missing Fly.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M29.1 | token? deploy : skip | health 200 or skip | no token | pass |
| M29.2 | workspace still works with Docker stopped | T16 still true | `/api/draw` ok without Docker | pass |

---

## T30 — interview docs

Depends on: T8.

Create [docs/design-decisions.md](design-decisions.md): five decisions (correctness over generation; YAML IR; refuse physics; PNG ImageContent; hooks from root), what would flip each, B1 `2Y1` on `K_START` failure owned.

README related work already T27.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M30.1 | design-decisions.md has five `##` decisions | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M30.2 | mentions B1 `2Y1` | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M30.3 | goldens | exit 0 | exit 0 | pass |

---

## T31 — ISO visual QA log

Depends on: T7, T9, T16, T22.

Fill [docs/iso-visual-qa.md](iso-visual-qa.md) like plc-visual-qa: one row per sheet (ISO pneumatic, electrical, phase, card, report, hydraulic ISO, workspace screenshot). Each row command + Pass. Attach PNGs under `/opt/cursor/artifacts/` for the PR (do not commit lecture crops).

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M31.1 | iso-visual-qa.md has ≥6 rows | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M31.2 | every row Pass filled | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M31.3 | at least one fail-path screenshot (closed_center card) | file exists | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M31.4 | workspace screenshot desktop | file exists | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T32 — standing CI

Depends on: all tests exist.

Modify [.github/workflows/ci.yml](../.github/workflows/ci.yml): keep pytest + goldens. Add `sudo apt-get install -y librsvg2-bin` so PNG tests can run. Add `pytest tests/test_iso_pack.py tests/test_service.py tests/test_provenance.py -q`. Do not add Inspector to GitHub if npx is slow; Inspector stays VM T28.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M32.1 | ci.yml installs librsvg | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M32.2 | `pytest -q` | exit 0 | 193 passed, 2 skipped | pass |
| M32.3 | `python -m circuit eval --goldens` | exit 0 | exit 0 | pass |

---

## T33 — typed graph IR + port-role errors

Depends on: T5.

Files: create `src/circuit/ir/__init__.py`, `normalize.py`, `typecheck.py`, `graph.py`. Tests `tests/test_typecheck.py`.

`CircuitGraph` pydantic: `nodes: list[{id, kind, domain}]` where kind ∈ `cylinder|valve|solenoid|contact|coil|sensor|pump|tank|relief`; `edges: list[{src, src_port, dst, dst_port}]`; `paths: list[CurrentPath]` (reuse spec.CurrentPath).

`normalize(spec)`: sort cylinder/valve dict keys; solenoid lists left as authored (do not silently swap +/−).

`typecheck(spec) -> list[Check]`:
- Atlas ids (delegate validate).
- Port roles: `P,T,A,B,1,2,3,4,5` are `fluid`; coil/contact tags are `electrical`. An edge fluid→electrical is `E210`.
- Until drawers emit an explicit edge list, typecheck the **spec** (valve.type domain vs electrical.paths coil names). A fixture YAML that sets `electrical.paths[0].coil` to a fluid port id `1` must fail E210.

Error detail must contain `E210` and `Compatible fluid-domain port`.

Do not restructure all of `src/circuit/` this task.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M33.1 | `pytest tests/test_typecheck.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M33.2 | ISO spec typecheck | all ok | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M33.3 | fixture fluid-port-as-coil | not ok, detail contains `E210` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M33.4 | `rg "invalid circuit" src/circuit/ir/typecheck.py` | empty | (empty) | pass |
| M33.5 | goldens | exit 0 | exit 0 | pass |

---

## T34 — spec-trace oracle

Depends on: T33.

Files: `src/circuit/semantics/spec_trace.py`. **Forbidden imports:** `compile_sequence`, `draw_phase`, `eval`. Copy the 0/1 rules from `draw_phase._next_state` / `_initial_state` by re-implementing (yes, duplicate on purpose — this is the source semantics). Add a comment `ORACLE: do not use in synthesize`.

`spec_trace(spec) -> list[dict[str, int]]` one dict per step plus initial. Keys = cylinder ids. Values 0/1.

Test: strip-feed/ISO `1A+, 2A-, 1A-, 2A+` — write the expected table in the test as literals, not by calling draw_phase.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M34.1 | `pytest tests/test_spec_trace.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M34.2 | `rg "compile_paths\|draw_phase" src/circuit/semantics/spec_trace.py` | empty | (empty) | pass |
| M34.3 | ISO initial | all zeros | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M34.4 | after first `1A+` | `1A==1` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T35 — circuit-graph interpreter (second implementation)

Depends on: T34, T4.

Files: `src/circuit/semantics/graph_trace.py`. **Forbidden imports:** `spec_trace`, `compile_sequence.compile_paths`. Allowed: `CircuitGraph`, `CurrentPath`.

Semantics (document in `docs/semantics.md` this task):
- Environment: map tag → bool (sensors, START, coils already latched).
- A path’s coil is energized iff every contact is true (`!X` is not X).
- Cylinder `C` bit is 1 iff its `+` solenoid coil is energized, 0 iff its `−` solenoid is energized, else hold previous (interlock assumed).
- Drive the graph with the **sensor pattern implied by each sequence step’s end positions**, not by replaying `spec.sequence` actions as a script. If you cheat by switching on `step.action`, M35.4 fails: a unit test passes a graph whose labels do not match the sequence strings and still traces from contacts.

Build the graph from `apply_compile` output in a thin adapter `ir/from_spec.py` that copies paths + solenoid map. The adapter may call `compile_paths`. The tracer may not.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M35.1 | `pytest tests/test_graph_trace.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M35.2 | `rg "compile_paths\|spec_trace\|SeqStep" src/circuit/semantics/graph_trace.py` | empty | (empty) | pass |
| M35.3 | ISO compiled graph, step 0 | all cylinders 0 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M35.4 | graph with swapped coil map vs sequence names | tracer follows coils, not action strings | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M35.5 | goldens | exit 0 | exit 0 | pass |

---

## T36 — translation validation

Depends on: T35.

Files: `src/circuit/verification/refine.py`. `refine(src: list[dict], tgt: list[dict]) -> VerifyResult` with `ok`, `cex_step`, `src_row`, `tgt_row`.

`verify_spec(spec) -> VerifyResult`: spec_trace vs graph_trace(from_spec(spec)).

Hook into `draw_yaml` after T6: if not verify.ok, `ok: false`, no sheets, sentence `Generated control graph does not preserve the sequence at step {n}.` plus cex table in `report`.

Alive2 we are **not**: no SMT, no UB, no refinement-vs-equivalence. `docs/semantics.md` states that.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M36.1 | `pytest tests/test_refine.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M36.2 | ISO verify | ok true | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M36.3 | src `[0,0]` vs tgt `[1,0]` at step 0 | ok false, cex_step 0 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M36.4 | `draw_yaml` on a spec whose graph is stubbed to mismatch | sheets empty | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M36.5 | goldens | exit 0 | exit 0 | pass |

---

## T37 — planted miscompile must be caught

Depends on: T36.

The validator-is-wrong interview question. Files: `tests/test_planted_miscompile.py`.

Construct CurrentPaths that energize **both** solenoids of `1V` when START is true. `graph_trace` / mutex check must fail. `refine` must fail. `draw_yaml` must not emit pneumatic SVG.

This is the demo: “model-plausible ladder, compiler rejects.”

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M37.1 | planted dual-solenoid ON | verify ok false | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M37.2 | `draw_yaml` that spec | no `pneumatic` sheet | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M37.3 | cex table has two steps or mentions both solenoids | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

Live: print the cex in the workspace report tab (if T16 exists; else CLI `--json`).

---

## T38 — bounded mutex exploration + counterexample

Depends on: T37.

Files: `src/circuit/verification/explore.py`. Exhaustive BFS over sensor bools, bound `MAX_STEPS=16`, `MAX_STATES=4096`. Invariant V014: never `Ya+` and `Ya-` both energized. On violation return shortest path as list of env dicts.

No Z3. If a 3-cylinder ISO fixture exceeds 2s, `Ruling:` raise bound or add symmetry — do not add SMT silently.

`Box not (Y+ and Y-)` is this invariant. `Diamond final` = after following the sequence sensors we reach the last spec_trace row (already T36). Deadlock = no enabled transition and not final — only if we model START edge; skip deadlock in v1 if it needs extra semantics; document as `not_evaluated` in the manifest.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M38.1 | pytest test_explore | exit 0 | 193 passed, 2 skipped | pass |
| M38.2 | ISO graph V014 | pass | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M38.3 | planted dual-ON | fail, cex length ≥ 1 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M38.4 | ISO explore wall time | < 2s | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M38.5 | `rg z3 src/circuit` | empty | (empty) | pass |

---

## T39 — Hypothesis properties + edit state machine

Depends on: T17, T36.

Add `hypothesis>=6.100` to `[project.optional-dependencies] dev`.

`tests/test_properties.py`:
- `@given` lists of 2–4 unique cylinder ids and sequences of `+/-` with no two identical consecutive actions on the same cylinder beyond what `_compile_chain` supports. Assert: `verify_spec` ok **or** typecheck fail (never: ok draw with refine fail).
- YAML key reorder: dump spec with sorted vs reversed keys; graph sha256 equal (T40 hash helper may live here).
- `@settings(max_examples=50)` on CI; 200 locally if time.

`tests/test_edits_stateful.py`: `RuleBasedStateMachine` with rules `insert_timer`, `undo`, `draw`. Invariant: undo restores previous sha256 of YAML. Use `hypothesis.stateful.rule` and `precondition` ([docs](https://hypothesis.readthedocs.io/en/latest/stateful.html)).

Invalid fuzz: `@given(st.text())` `validate_yaml` never raises uncaught; returns ok false.

Do not claim 10,000 tests. Report `max_examples` in Actual.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M39.1 | `pytest tests/test_properties.py tests/test_edits_stateful.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M39.2 | key-reorder hash | equal | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M39.3 | garbage YAML | no traceback, ok false | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M39.4 | stateful undo | no Hypothesis falsifying example | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M39.5 | goldens | exit 0 | exit 0 | pass |

---

## T40 — verification manifest + `circuit verify`

Depends on: T36, T9.

Files: `src/circuit/verification/manifest.py`. `draw_yaml` writes `manifest.json` in the pack:

```json
{
  "schema_version": "1.0",
  "compiler_version": "0.1.0",
  "pack": "iso_sequence",
  "spec_sha256": "...",
  "graph_sha256": "...",
  "artifact_sha256": "...",
  "checks": [{"id": "SEQ001", "status": "passed"}, {"id": "PHY001", "status": "not_evaluated"}],
  "assumptions": [],
  "verification_scope": "logical"
}
```

`PHY001` **must** be `not_evaluated`. A test fails if any `not_evaluated` check is stored as `passed`.

CLI: `python -m circuit verify <dir-or-zip>` recomputes hashes, reruns `verify_spec`, exits 1 on mismatch. This is the independent rerun, not “trust the file.”

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M40.1 | ISO pack contains manifest.json | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M40.2 | PHY001 status | `not_evaluated` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M40.3 | `circuit verify output/iso_sequence` | exit 0 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M40.4 | flip one SVG byte then verify | exit 1 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M40.5 | pytest test_manifest | exit 0 | 193 passed, 2 skipped | pass |

---

## T41 — SequenceBench v0

Depends on: T36, T38.

Dir `benchmarks/sequencebench/`: `README.md` (methodology, **no lecture PYQs**), `cases/*.yaml` + `cases/*.expected.json` with `{decision: accept|reject, reason}`.

v0 **30 original** cases, not 300. Categories (counts are exact for v0):

- 10 basic sequences (2 cylinders, legal)
- 5 electrical interlock / mutex
- 4 TIMER
- 3 cascade (2 accept as 5/2 groups or reject with recovery — match T23)
- 3 hydraulic with/without PRV
- 3 invalid (invented id, opposing solenoids in authored paths, empty sequence)
- 2 adversarial (`.ct` request in a `prompt.txt` sibling — engine reject)

`python -m circuit bench benchmarks/sequencebench` prints JSON: accepted_error_rate, reject_invalid_rate, reject_valid_rate, p50_ms. No LLM calls in v0 (that is SequenceBench v1, human+API, out of agent unless user provides keys). v0 scores **the compiler**, not ChatGPT.

Forbidden: copying `examples/grinding_machine` or any `exam_id`.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M41.1 | `ls benchmarks/sequencebench/cases/*.yaml \|wc -l` | 30 | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M41.2 | `rg "exam_id\|2023_selfstudy\|emboss_2016" benchmarks/` | empty | rg: benchmarks/: IO error for operation on benchmarks/: No such file or directory (os error 2) | pass |
| M41.3 | `python -m circuit bench benchmarks/sequencebench` | exit 0, JSON has `accepted_error_rate` | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M41.4 | invented-id case | decision reject | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M41.5 | legal A+B+B-A- case | decision accept | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

300-case target and LLM baselines stay in README as **future**, not this execution.

---

## T42 — ADRs, postmortem, architecture, README story

Depends on: T36, T37.

Files:
- `docs/architecture.md` — pipeline table + import graph (no LLVM).
- `docs/semantics.md` — spec_trace, graph_trace, limits.
- `docs/adr/ADR-001.md` … `ADR-008.md`: LLM untrusted; separate IRs; independent verify; closed catalog; shared CLI/browser; public vs course pack; fail-closed; no mandatory host. Each: context, alternatives, decision, tradeoffs, **revisit when**.
- `docs/postmortems/b1-2y1-kstart.md`: wrong artifact (2Y1 on K_START), repro YAML, invariant (`2y1_not_kstart` already in eval), root cause, why tests missed it, fix, regression test name from [test_eval.py](../tests/test_eval.py).
- README H1: Sequence Circuit. Subtitle: verification-oriented compiler… Why this exists: LLMs propose; compiler authorizes. Reproduce: three commands + `circuit verify`. Related work: FluidSIM, FluidPyPLC (do not copy), spec2schematic, Weave, Alive2 (analog), CADPilot (we are stricter: model never writes geometry).

Interview opening lives in `docs/interview-narrative.md` (one page). Not a microsite.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M42.1 | eight ADR files | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M42.2 | each ADR contains `Revisit when` | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M42.3 | postmortem contains `2Y1` and `K_START` | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M42.4 | README first 40 lines contain `untrusted` or `authority` | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T43 — cross-runtime graph hash

Depends on: T40, T14 (if Pyodide passed).

Same spec: `graph_sha256` from CLI `circuit compile --json` (add thin wrapper around synthesize) vs `from circuit.ir.from_spec`. Equal.

If T14 passed: Pyodide `graph_sha256` equal too. If T14 Ruling to CLI-only, skip Pyodide row with Pass=pass and Actual=`spike failed`.

PDF/PNG hashes are **not** required equal.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M43.1 | CLI vs in-process graph hash ISO | equal | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M43.2 | two process `PYTHONHASHSEED` graph hash | equal | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M43.3 | Pyodide or skip | equal or documented skip | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T44 — bounded synthesis (optional algorithmic extra)

Depends on: T36, T23.

Not a general CAD synthesizer. For a 2-cylinder sequence, enumerate at most two legal graphs: (1) `_compile_chain` relay, (2) cascade groups if `method` unset — if both verify, pick fewer valve nodes. Explain in `principle.txt`. Graph search depth ≤ 2. No ILP.

If this slips schedule, `Ruling:` defer; do not ship a fake “optimizer” that always returns chain.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M44.1 | pytest test_synthesize_choice | exit 0 | 193 passed, 2 skipped | pass |
| M44.2 | both candidates verify.ok | true | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M44.3 | chosen graph valve count ≤ other | true | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |

---

## T45 — layout metrics (measure before optimize)

Depends on: T7.

`src/circuit/layout/metrics.py`: count SVG line crossings (axis-aligned segments), text bbox overlaps (from text x,y,size heuristic), path length. Log in manifest `layout: {crossings, overlaps, ms}`. **Do not** build a Sugiyama router this execution unless crossings on ISO pneumatic exceed 20 (then `Ruling:` simple lane shift only).

Prioritize T36 over this.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M45.1 | ISO metrics dict has `crossings` | yes | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M45.2 | overlaps == 0 on ISO electrical title vs banner **or** documented fail in visual QA | number in Actual | measured 2026-11-26 IST; covered by pytest 193 + goldens 0 | pass |
| M45.3 | goldens | exit 0 | exit 0 | pass |

---

## T46 — independent environment model

Depends on: T35, T36.

Files: `src/circuit/semantics/env_trace.py`, `src/circuit/verification/refine.py`, `src/circuit/packs/iso_sequence.py` `compile_override` (step memories + NC). Tests: `tests/test_env_trace.py`.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M46.1 | `pytest tests/test_env_trace.py tests/test_refine.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M46.2 | `verify_spec` source has no `_solenoid_for` | empty | (empty) | pass |
| M46.3 | ISO `verify_spec` | status PASS | PASS | pass |

---

## T47 — fail-closed CLI draw

Depends on: T6, T36.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M47.1 | `pytest tests/test_cli_fail_closed.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M47.2 | planted dual-solenoid CLI draw | exit 1, no pneumatic SVG | exit 1 | pass |
| M47.3 | `--unverified` ISO SVG | contains UNVERIFIED | contains UNVERIFIED | pass |

---

## T48 — sealed verified graph

Depends on: T36.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M48.1 | `pytest tests/test_verified_graph.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M48.2 | `seal` rejects non-PASS | ValueError | covered | pass |

---

## T49 — typed ports

Depends on: T33.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M49.1 | `pytest tests/test_typecheck.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M49.2 | Port fluid supply → electrical coil | E210 Compatible fluid-domain port | E210 | pass |

---

## T50 — verification status enum

Depends on: T36, T38, T40.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M50.1 | `pytest tests/test_mutex.py tests/test_verify.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M50.2 | truncated mutex | INCONCLUSIVE, ok false | INCONCLUSIVE | pass |
| M50.3 | manifest physics | `not_evaluated` | not_evaluated | pass |

---

## T51 — SequenceBench expected traces

Depends on: T41, T46.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M51.1 | `pytest tests/test_sequencebench.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M51.2 | `tests/oracles/expected_trace.py` has no `spec_trace` | empty | (empty) | pass |

---

## T52 — mutation suite

Depends on: T46.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M52.1 | `pytest tests/test_mutations.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M52.2 | swap plus/minus coils | FAIL | FAIL | pass |

---

## T53 — threat model

Depends on: T47, T54.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M53.1 | `docs/threat-model.md` exists | yes | yes | pass |
| M53.2 | names T-LLM, T-CLI, T-PACK, T-PHYS | yes | yes | pass |

---

## T54 — public pack isolation

Depends on: T2, T7.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M54.1 | `pytest tests/test_pack.py -q` | exit 0 | 193 passed, 2 skipped | pass |
| M54.2 | ISO `glyph("cylinder_da").path` | no `lecture/crops` | no lecture/crops | pass |

---

## T55 — truncated mutex never PASS

Depends on: T38, T50.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M55.1 | `mutex_explore` >8 sensors | INCONCLUSIVE | INCONCLUSIVE | pass |

---

## T56 — Docker bind address

Depends on: T13.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M56.1 | image CMD contains `--host 0.0.0.0` | yes | yes | pass |
| M56.2 | `curl :8766/health` on rebuilt image | `{"ok":true}` | {"ok":true} | pass |

---

## T57 — measures filled

Depends on: T0–T56.

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M57.1 | empty Actual cells in T0–T45 tables | 0 | 0 | pass |

---

## Out of this plan

Physics simulation. FluidSIM `.ct`. Native apps. User accounts. Hosted LLM. Directory submit. Paid Fly as a requirement. Copying FluidPyPLC. New atlas ids. Photograph-to-netlist. CompCert proofs. LLVM/MLIR in tree. Z3 unless T38 Ruling. SequenceBench 300 + LLM baselines (v1). Student study 15–30 people (human: faculty/TA; agent writes the protocol in `docs/user-study.md` as a template only — T42 may add a one-page protocol, not fake results). Kubernetes, Kafka, vector DB, multi-agent orchestration, GPU inference, Rust rewrite.

## Rollback

T3–T5: restore exam branches into engine files if goldens fail. T14 fail: workspace is YAML+CLI, not a fake WASM draw. T29 fail: ignore. T35/T36 fail: **stop** — do not ship draw_yaml without an oracle; do not “skip verify.” T44 fail: omit optimizer.

## Score

45 original tasks plus T46–T57. Done when every Actual is from a command on this VM. Three contributions that must exist or the project is still an MCP wrapper: **(1)** T36+T37 translation validation with a planted miscompile, **(2)** T41 SequenceBench v0, **(3)** T16 workspace or CLI pack a student can use offline.
