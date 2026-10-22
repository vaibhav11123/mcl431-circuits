# What eval checks

```bash
pytest -q
python -m circuit eval --goldens
```

A passing `eval` means the **spec is legal for that exam**. It does not mean the sheet looks like handwriting.

## Required goldens

| Exam | What eval requires | Must not do |
| --- | --- | --- |
| 2023 Self-Study B1 grinding | JOB, one pump, 30 s, 15.72 bar, L8 latch; solenoid NC interlock OK | Extra FCV / second pump; solenoid NO as sequence |
| 2017 Minor-1 hi-lo punch | P1+P2, UV, RV; bore `not_given` | Invented 50/28 |
| 2023 Minor-2 Q1 strip feed | Domain pneumatic, two 5/2, coils `1Y1 2Y2 1Y2 2Y1` | Hydraulic 4/3 on a 5/2 paper |
| 2018 hi-lo | `figure_given` calc cites `exams/transcribed/2018_minor1_hilo/facts.yaml` | Draw a figure the paper already printed |
| 2019 meter-in / meter-out | `figure_given`; bore `not_given` | Invent a table size |
| 2016 hoist | `figure_given`; load 5.4 ton from facts | Invent pipe losses |
| 2023 Self-Study B2 | `figure_given`; Ap/Ar from facts | Invent Q |
| 2022 grind-on-given hi-lo | `figure_given`; HC1 50/25 from facts | Redraw the given figure |
| 2017 Minor-2 indexing drill | Three `dcv_5_3`, S0, 12 motions, KM | Stamp a 5/2 or invent a 5/3 box |
| 2016 Minor-1 Q2 emboss | Two `dcv_5_2`, S0, PS 4 bar; `2Y2` from K4/PS not 2B2 | Retract 2A1 on 2B2; closed-centre 5/3 |
| 2023 Minor-2 Q2 PLC conveyor | Domain `plc`; `plc:` IR; AI 948 / cmp 949 / 2500; AO 303/575/907; START/STOP + L1–L3 | L8 relay sheet or hydraulic pumps |
| L14 fan controller | AO 205/512/818; PB + L1–L3; CMP/MOV zones | Invent rpm outside paper table |
| L14 counter eject | CTU PV=15 + RES | Allow S1 after DN without reset story |
| L14 stamping | Full LS1–3 / LSUP / LSDN / Up / Dn / CONV / lamps I/O | Drop lamp addresses |
| L14 apple packing | CTU=12 + TON 5 s | Skip delay or wrong count |

Also: every stamp PNG the drawer uses must exist. B1 SVG must name HC1, HC2, HM1.

## Skipped

- Pixel-SSIM against a full lecture slide

## Visual marking checklist

Eval PASS is not handwriting. The sheet still has to look like an exam answer:

- **Terminals:** home nB1 is NC **1/2** with rest-closed arrow; K aux is **11/14** (second **21/24**); START/S1/S3 pushbutton **13/14**; T1 timed contact **7/8**; PS pressure switch **1/4**. Never label home NC as 21/22.
- **Contact-element table** under each K and T1 coil (coil name, A1/A2, aux terms used).
- **L8:** coils at the bottom of numbered current paths; sheet drawn de-energized.
- **Hydraulic:** ISO hop (polyline, no filled dot) at P/T crossings; B1 uses `cylinder_da`, not the L10 air cylinder; RV1 setpoint on B1 is **15.72 bar** (2.5 kN is the relief setting, not a pressure switch).
- Hydraulic-only papers skip electrical/phase sheets; electro papers write both; PLC papers write `plc_connection` + `plc_ladder`.
- Outputs go to `output/<exam_id>/`.
- **Strip-feed:** H1 lamp on a main path; start contacts S1/S3, not JOB.
- **Emboss (2016 Q2):** PS on the 2A1+ line, 4 bar; retract 2A1 from the pressure switch, not 2B2.
- Missing atlas crop (`dcv_5_3` etc.) → stop. Do not draw a generic ISO box.
