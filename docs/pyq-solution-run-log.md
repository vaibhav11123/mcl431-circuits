# PYQ solution run log

Corpus: `/Users/vaibhavsingh/Downloads/PYQs with solutions MCL431.zip` (same tree as the earlier `PYQs with solutions.zip`). Scans stay local under `exams/pyqs/` (gitignored).

## Wave 0 — baseline (before any new golden)

- `pytest -q`: **120 passed**, 7 warnings
- `python -m circuit eval --goldens`: **exit 0**
- L14 intake log: [plc-intake-run-log.md](plc-intake-run-log.md)

## Wave 1 — inventory

Unique basenames (deduped `_papers/` copies and jpeg twins): **92**. `__MACOSX` skipped.

Measures:

| ID | Check | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| M1.1 | pytest + eval --goldens | exit 0; count in log | 120 passed; goldens exit 0 | pass |
| M1.2 | disposition lines | = unique basenames | 92 | pass |
| M1.3 | git status — no zip path | empty for zip/PDF adds | no zip staged | pass |

### Disposition (one line each)

**Out of scope**

- `TP-202-Electropneumatics-Advanced-Level.pdf` — Festo workbook; do not mine symbols
- `CHEGG2RSBOT.pdf` — textbook psi/gpm drill; not an exam
- `Lecture 33 Droplet Combustion.pdf` — MCL 343
- `Lecture 34 Diffusion Flames.pdf` — MCL 343
- `MCL431_L21_CNCPartProgramming-1.pdf` — local CNC notes (like L11–L13); not atlas
- `MCL431_L22_CNC_Turning_1.pdf` — local CNC notes; not atlas

**Duplicates (covered by canonical basename)**

- `MCL431_Major-21Nov2019 copy.pdf` → `MCL431_Major-21Nov2019.pdf`
- `MCL431_SelfStudy_Minor_01July2023[1].pdf` → `MCL431_SelfStudy_Minor_01July2023.pdf`
- `MCL431_Minor1_2022-23.jpeg.jpg` → `MCL431_Minor1_2022-23.jpeg`
- `MCL431_Minor2_2022-23.jpeg.jpg` → `MCL431_Minor2_2022-23.jpeg`
- `Mcl431 major.pdf` → `Major 2022.pdf` (OCR twin)
- papers under `MCL431 _papers/` → top-level same basename

**Already locked (same_as / existing index)**

- `MCL431_SelfStudy_Minor_01July2023.pdf` — `2023_selfstudy_b1`, `2023_selfstudy_b2`
- `MCL431_Minor_1-01Sep2017.pdf` / `[Fall17]-Minor1.pdf` — `2017_minor1_hilo`
- `MCL431_Minor_1-25Aug2018.pdf` — `2018_minor1_hilo`
- `MCL431_Minor_1-26Aug2019.pdf` — `2019_minor1_meter`
- `MCL431_Minor-13Dec2020.pdf` / `[Fall16]-Minor1.pdf` — `2016_minor1_hoist`, `2016_minor1_emboss`
- `MCL431_Minor2_2017-18_Sem1.pdf` / `[Fall17]-Minor2.pdf` — indexing drill
- `MCL431_Minor2_2022-23.jpeg` — strip feed + PLC conveyor
- `MCL431_minor.pdf` / `MCL431_Minor-Part-B-27Sep2022.pdf` / `MCL431_Minor1_2022-23_Sem1.pdf` / `MCL431_Minor1_2022-23.jpeg` — grinding; **locked 1.6 kN-cm** (reject 6.5 kN-m OCR twin until solution card proves otherwise)
- `MCL431_Minor1_2016-17_Sem1.pdf` — image scan twin of Fall16
- `MCL431_Minor1_2017-18_Sem1.pdf` — image scan twin of Fall17 Minor1

**Solution scans (W3 evidence; never commit)**

- `Major 2022 Solution.pdf` — image-mostly; structural twin for 2022 major
- `Major_07May2023_Solution.pdf` — text layer K1–K13 ladder for 2023 B1
- `Major_S.pdf` — image-only
- `major q + sol.pdf` — image-only

**Image-only / OCR deferred to W3**

- `lab.pdf`, `MCL431_Re_Major_2022-23.pdf`
- `Quiz 2 - Hydraulic Circuit Design and Analysis.jpeg.jpg`
- `Quiz 4 - Electropneumatic.jpeg.jpg`
- `Quiz 5 - PLC.jpeg.jpg`
- `Quiz 6 - PLC.jpeg.jpg`
- `Quiz 8 - CnC Part Programming.jpeg.jpg`
- `2024 self study minor.jpg`
- `Screenshot 2025-09-14 034530.png`
- all `WhatsApp Image 2025-09-14 at …` (solution / workings photos)

**New text papers (W2 cards)**

- `MCL431_Major-22Nov2017.pdf` — oven, tank mix, two-cylinder loss, servo numbers
- `MCL431_Major-17Nov2018.pdf` — air-jet electro, CNC, lockout, preset counter, fill-in CNC
- `MCL431_Major-21Nov2019.pdf` — sprinkler clock, meter-out calc, CNC, adaptation graph
- `MCL431_Major_Selfstudy_11July2020A.pdf` — oven, apple packing (same_as L14), hoist+loss, CNC, mill clamp 5 bar
- `MCL431_ReMajor-3Jan2020.pdf` — orange-juice PLC, servo, strip feed (same_as), CNC
- `Major 2022.pdf` / `MCL431_major_2022.pdf` — oven+AO, stepper, hoist+loss, two-hand stamp
- `Major_07May2023.pdf` — Part A MCQ, four-hole drill, plywood stack PLC, CNC turning

## Later waves

Filled as each wave closes.

## Wave 2 — cards

- New transcribed folders: 30 majors + quiz/OCR cards.
- Learnings on locked folders including MCL431_minor `keep_locked` for 6.5 kN-m OCR.
- Index `same_as`: apple packing, strip feed, oven 2020→2017, quiz4→airjet, 2024→B1.

| ID | Check | Actual | Pass |
| --- | --- | --- | --- |
| M2.1 | learnings.yaml per text id | 46+ learnings files | pass |
| M2.2 | no pasted solution paragraphs in new cards | new cards are one-line claims | pass |
| M2.3 | same_as apple/strip/grinding lock | present in index + learnings | pass |

## Wave 3 — scans / OCR

| Basename | Status | Note |
| --- | --- | --- |
| Major_07May2023_Solution.pdf | readable | K-ladder twin for B1; plywood I/O; G71 on p7 — B3 figure dims are on the *question* page → program adopted with question DOC 0.09 |
| Major 2022 Solution.pdf | readable (partial OCR) | stepper workings messy; two-hand marking mentions 1A/2A sequence |
| Major_S.pdf, major q + sol.pdf | unreadable | image-only |
| lab.pdf | readable (ocrmac) | **out of scope** — SBL100 biology buffers/microscopy, not MCL431 |
| MCL431_Re_Major_2022-23.pdf | readable (ocrmac) | 03-Jan-2023 Re-Major: Q1=quiz6 conveyor same_as; Q2 CNC mill not_given; Q3 bottle-fill electrical_only |
| Quiz 2/4/5/6/8, 2024 self study | readable via ocrmac | cards added |
| WhatsApp Image … (all) | readable (partial) | mapped to apple/tank/oven/air-jet/same_as + new 2024_midterm_q1_press; screenshot = MCL431_minor 6.5 kN twin (keep_locked); full OCR report `/tmp/pyq_ocr_report.md` (local) |

| ID | Check | Actual | Pass |
| --- | --- | --- | --- |
| M3.1 | each image-only basename readable/unreadable | logged above | pass |
| M3.2 | git status no ingest/zip staged | exams/pyqs gitignored | pass |
| M3.3 | readable quiz gets card or same_as | quiz2/4/5/6/8 + 2024 cards | pass |

## Wave 4 — numeric workings

Added in `src/circuit/calc.py`: meter-out 2019, hoist-with-loss 2020/2022, two-cyl loss, servo, stepper, Part A, quiz regen, oven band counts, adaptation refusal, CNC `not_given` lines.

| ID | Check | Actual | Pass |
| --- | --- | --- | --- |
| M4.1 | pytest tests/test_calc.py | 15 passed | pass |
| M4.2 | 2016 hoist still no invented pipe loss; 2020 names pipes | both | pass |
| M4.3 | scan compare | solution scans mostly unreadable for numbers; lecture results kept | pass |

## Wave 5 — PLC goldens

Tank mix, lockout, preset counter, orange juice, plywood, oven 2017, oven 2022, sprinkler, traffic quiz5, quiz6 conveyor. Eval hooks in `eval.py`. All draw+eval PASS.

## Wave 6 — electro goldens

Air-jet (`dcv_3_2` stamp + atlas crop), mill clamp 5 bar, two-hand, four-hole (compile via indexing drill). All PASS.

## Wave 7 — CNC

All program exam_ids return `not_given`. No gcode/sim module. 2019 Q4 adaptation = one-line refusal.

## Wave 8 — docs

README, handbook, solve, eval, PLC QA, AGENTS, skill, circuit-designer, exams/lecture README, ship-plan corpus note. copyright.md unchanged. Skill has no `draw_spec`. Score still 0/39.

## Wave 9 — regression

| ID | Check | Actual | Pass |
| --- | --- | --- | --- |
| M9.1 | pytest -q | **124 passed** (baseline was 120) | pass |
| M9.2 | eval --goldens | exit 0 | pass |
| M9.3 | no scans in git status | clean for pdf/jpg/ingest | pass |
