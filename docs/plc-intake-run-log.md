# PLC intake run log

## Wave 0 — baseline

- Copied L11–L14 PDFs into `lecture/` (gitignored).
- `pytest -q`: **119 passed**, 7 warnings
- `python -m circuit eval --goldens`: **exit 0**

## Wave 1 — rasterize + ingest

- `rasterize --only lecture`: 349 pages (includes L11–L14).
- Ingest exit 0 for L11, L12, L13, L14; all `kind: lecture_notes_draft`.
- Promote L14 → `proposal/` OK; atlas/crop git diff empty.
- L14 `document.md` has Counter, Stamping, Apple Packing, Fan Controller.
- Note: electropneumatic phrase check still runs on PLC notes (some false `5/2` hits); not treated as failure.

## Wave 2 — L14 facts

- Transcribed: `plc_l14_counter_eject`, `plc_l14_stamping`, `plc_l14_apple_packing`, `plc_l14_fan_controller`.
- Index rows point at `lecture/MCL431_L14_PLC_Problems.pdf` (local).

## Wave 3 — `plc:` IR

- `CircuitSpec.plc` + data-driven `draw_plc.py`; conveyor golden migrated.
- Conveyor eval PASS; atlas untouched.

## Wave 4 — L14 goldens

- Fan → counter → stamping → apple packing registered in `eval.py` goldens.
- Final: **120 passed** pytest; `eval --goldens` exit 0.

## Wave 5 — docs

- AGENTS.md, generate-circuit skill (PLC subagent split), solve-a-question, handbook index.

## Spike — OSS pattern oracle (answer + visual QA)

Sources (read only; not imported into draw):

- [Basil-Saad/openplc-ladder-logic-exercises](https://github.com/Basil-Saad/openplc-ladder-logic-exercises) MIT
  - **ex-06 rising-edge toggle:** `Button_Input` → `R_TRIG` → SET `Light` when `Light` false; RESET `Light` when `Light` true. Maps to our `ons` + `otl` / `otu` (MicroLogix ONS + latch/unlatch).
  - **ex-05 CTU:** `Sensor_Input` clocks `CTU`; `Reset_Switch` on R; `Full_Box_Alarm` on Q. Maps to `ctu` + `res` + DN contact.
- [Sanfoundry stamping](https://www.sanfoundry.com/plc-program-operate-stamping-parts/): START+LS1 latch CR1 → CONV until LS2; LS2 → DN; LSDN → CR4 → CONV to LS3; CR3/LSUP → UP. Our prior golden had Power from unbound `M0.0 RUN` (dead). Fix: START/STOP latch → Power; memory steps for CONV/Dn/Up.
- SchemaTex ladder XIC/XIO/(L)/(U): visual bar for IEC-ish contacts (not a runtime dep).

Mapping pass/fail (pre-fix):

| Pattern | OpenPLC / twin | Our `plc:` kinds | Pre-fix L14 | Post-fix target |
|---------|----------------|------------------|---------------|------------------|
| Alt PB toggle | R_TRIG + SET/RESET | `ons` in series; `otl`/`otu` | FAIL (fake oneshot) | PASS |
| CTU edge + RES | CTU CU/R/Q | `ctu`/`res` + ONS on CU | PARTIAL | PASS + Y2 retract |
| Stamping sequence | Sanfoundry CR1–4 | contacts + coils + START latch | FAIL (Power) | PASS |
| Apple edge+TON | CTU+TON labs | `ons`+`ctu`+`ton` | PARTIAL (level count) | PASS |

Verdict: plan direction OK — port patterns into YAML/SVG; do not import OpenPLC.

## Wave 6 — answer + visual QA (executed)

- `draw_plc`: IEC-ish contacts; ONS/OTL/OTU blocks/coils; PB stamp only for operator buttons; LS as boxes.
- Goldens fixed: fan ONS+OTL/OTU; counter Y2+edge; stamping START→RUN→Power; apple ONS edge.
- Eval hardened (`fan_ons/otl/otu`, `counter_*`, `stamp_*`, `apple_edge_ons`).
- Visual gate 4 (PNGs):

| Golden | Contacts | ONS/L/U | PB vs LS | Eval |
|--------|----------|---------|----------|------|
| fan | PASS | PASS | PB only | PASS |
| counter | PASS | ONS+CTU | S1/S2 PB | PASS |
| stamping | PASS | START latch | LS boxed | PASS |
| apple | PASS | ONS+CTU+TON | START/STOP PB | PASS |
| conveyor 2023 | PASS | n/a | START/STOP PB | PASS |

- Final: **120 passed** pytest; `eval --goldens` exit 0 (340 PASS lines, 0 FAIL).
