# PLC visual + answer QA

Without an official MCL431 answer key, a golden is **exam-defensible** only if it passes gates 1–5. Never claim “official key match.” L14 still has no course key (use OpenPLC/Sanfoundry twins). Majors that have a readable solution scan use that scan as Gate 2 twin for structure, not as text to paste.

## Gate 0 — Pattern oracle (spike)

Map OpenPLC / Sanfoundry / MicroLogix teaching rungs into `plc:` kinds before rewriting goldens. Log in [plc-intake-run-log.md](plc-intake-run-log.md). Do not import OpenPLC into the draw pipeline.

## Gate 1 — Paper lock

Against `lecture/ingest/MCL431_L14_PLC_Problems/document.md` and `exams/transcribed/<exam>/facts.yaml`:

- [ ] Every named device is in `plc.io` and on `plc_connection.svg`
- [ ] Required numbers on ladder or scaling table (15, 12, 5 s, zone rpm, slot/bits)
- [ ] Deliverables: `plc_connection` + `plc_ladder` (not L8)

## Gate 2 — Twin structure

| Problem | Twin | Must show |
|---------|------|-----------|
| Fan | OpenPLC ex-06 / MicroLogix ONS | `ONS` + `(L)`/`(U)` (or `OTL`/`OTU`) |
| Counter | OpenPLC ex-05 | CTU PV=15, RES on S2, Y1 advance + retract path |
| Stamping | Sanfoundry | START→RUN→Power; LS1–3; LSUP/LSDN; CONV/Up/Dn |
| Apple | CTU+TON packing | Edge on apple pulse; CTU=12; TON=5 s |
| Conveyor 2023 | Paper + calc | Keep as quality bar |
| Oven 2017/2022 | Solution scan / question bands | OTL at low, OTU at high; 2022 MOV AO + TON 5 s |
| Sprinkler 2019 | Question | 1 s TON + CTU s/min/h; 5 min open |
| Lockout 2018 | Question | CTU=5; 5 min TON; permanent OTL |
| Preset counter 2018 | Question | 300/175/50; last switch wins |
| Tank mix 2017 | Question | TON 180 s |
| Orange juice 2020 | Question | pumps together; pump3 10 s |
| Plywood 2023 | Solution I/O table | CTU=20; paint 10.6 s; blink |
| Traffic quiz 5 | Question | R10 Y5 G15 |

## Gate 3 — Math

`plc_fan_l14_scaling` / `plc_2023_q2_scaling` unit tests must stay green (AO 205/512/818, conveyor counts).

## Gate 4 — Visual marker pass

After `python -m circuit draw`, open PNGs under `output/<exam_id>/`:

1. Contacts look like contacts (vertical ticks + gap), not anonymous rectangles
2. NC has a clear slash
3. Coils are circles; OTL/OTU/ONS/CTU/TON/MOV readable as instructions
4. Connection: PBs look like PBs; LS/prox/analog are **not** pushbutton stamps
5. I/O table readable; cmp ops show `<`/`>` correctly in SVG
6. Rung numbers + captions present

Score each golden pass/fail in the run log.

## Gate 5 — Hardened eval

`python -m circuit eval` must fail empty/Power-broken ladders:

- Fan: ladder SVG text contains `ONS` and (`OTL` or `(L)`) and (`OTU` or `(U)`)
- Counter: `Y1`, retract (`Y2` or retract caption), `CTU`, `PV=15`, `RES`
- Stamping: START (or RUN that START sets) drives Power; LS1–3; LSUP; LSDN
- Apple: edge token (`ONS`); presets 12 and 5

Still not a PLC simulator — structural evidence only.

## Commands

```bash
python -m circuit validate examples/plc_l14_<name>/circuit.yaml
python -m circuit draw examples/plc_l14_<name>/circuit.yaml
python -m circuit eval examples/plc_l14_<name>/circuit.yaml
pytest -q
python -m circuit eval --goldens
```
