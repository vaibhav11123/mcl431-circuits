#!/usr/bin/env python3
"""Write T41 SequenceBench v0 cases under benchmarks/sequencebench/."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "sequencebench"
CASES = OUT / "cases"

PNEU_HEAD = """meta:
  title: {title}
  domain: pneumatic_plus_electrical
  patterns: [ep_dac_5_2, sequence_double_solenoid]
{method}sequence:
{sequence}
power: {{ pumps: [], tank: "" }}
cylinders:
{cylinders}
motors: {{}}
valves:
{valves}
sensors: {sensors}
electrical:
  convention: lecture
  paths: {paths}
"""


def cyl_block(n: int) -> tuple[str, str, str]:
    cyls = []
    valves = []
    sensors = []
    for i in range(1, n + 1):
        cyls.append(
            f"  {i}A: {{ dcv: {i}V, sensors: [{i}B1, {i}B2] }}"
        )
        valves.append(
            f"  {i}V: {{ type: dcv_5_2_double_solenoid, solenoids: [{i}Y1, {i}Y2] }}"
        )
        sensors.extend([f"{i}B1", f"{i}B2"])
    return "\n".join(cyls), "\n".join(valves), "[" + ", ".join(sensors) + "]"


def seq_lines(actions: list[tuple[str, str, int | None]]) -> str:
    rows = []
    for action, label, seconds in actions:
        extra = f", seconds: {seconds}" if seconds is not None else ""
        rows.append(f"  - {{ action: {action}, label: {label}{extra} }}")
    return "\n".join(rows)


def write_case(
    stem: str,
    yaml_text: str,
    decision: str,
    reason: str,
    prompt: str | None = None,
) -> None:
    (CASES / f"{stem}.yaml").write_text(yaml_text, encoding="utf-8")
    (CASES / f"{stem}.expected.json").write_text(
        json.dumps({"decision": decision, "reason": reason}, indent=2) + "\n",
        encoding="utf-8",
    )
    if prompt is not None:
        (CASES / f"{stem}.prompt.txt").write_text(prompt, encoding="utf-8")


def pneu(
    title: str,
    actions: list[tuple[str, str, int | None]],
    n: int = 2,
    paths: str = "[]",
    method: str = "",
) -> str:
    cyls, valves, sensors = cyl_block(n)
    method_block = f"  method: {method}\n" if method else ""
    return PNEU_HEAD.format(
        title=title,
        method=method_block,
        sequence=seq_lines(actions),
        cylinders=cyls,
        valves=valves,
        sensors=sensors,
        paths=paths,
    )


def hyd(title: str, with_prv: bool, two: bool = False) -> str:
    prv = "    - { id: RV1, pump: P1 }\n" if with_prv else ""
    cylinders = "  1A: { dcv: 1V, sensors: [1B1, 1B2] }"
    valves = "  1V: { type: dcv_4_3_closed_center, solenoids: [1Y1, 1Y2] }"
    sensors = "[1B1, 1B2]"
    seq = seq_lines(
        [("1A+", "extend", None), ("1A-", "retract", None)]
    )
    if two:
        cylinders += "\n  2A: { dcv: 2V, sensors: [2B1, 2B2] }"
        valves += "\n  2V: { type: dcv_4_3_closed_center, solenoids: [2Y1, 2Y2] }"
        sensors = "[1B1, 1B2, 2B1, 2B2]"
        seq = seq_lines(
            [
                ("1A+", "clamp", None),
                ("2A+", "press", None),
                ("2A-", "unpress", None),
                ("1A-", "unclamp", None),
            ]
        )
    return f"""meta:
  title: {title}
  domain: hydraulic
  patterns: [dac_4_3]
sequence:
{seq}
power:
  pumps:
    - {{ id: P1 }}
  relief_valves:
{prv}  tank: TANK
cylinders:
{cylinders}
motors: {{}}
valves:
{valves}
sensors: {sensors}
electrical: {{ convention: lecture, paths: [] }}
"""


def main() -> None:
    CASES.mkdir(parents=True, exist_ok=True)
    basics = [
        ("00", "clamp then feed", [("1A+", "clamp", None), ("2A+", "feed", None), ("2A-", "return", None), ("1A-", "release", None)]),
        ("01", "feed then clamp", [("2A+", "feed", None), ("1A+", "clamp", None), ("1A-", "release", None), ("2A-", "return", None)]),
        ("02", "press index", [("1A+", "press", None), ("2A+", "index", None), ("1A-", "lift", None), ("2A-", "home", None)]),
        ("03", "lift then press", [("2A+", "lift", None), ("1A+", "press", None), ("1A-", "lift", None), ("2A-", "drop", None)]),
        ("04", "hold strip", [("1A+", "hold", None), ("2A+", "advance", None), ("2A-", "back", None), ("1A-", "open", None)]),
        ("05", "stamp nest", [("1A+", "nest", None), ("2A+", "stamp", None), ("2A-", "clear", None), ("1A-", "eject", None)]),
        ("06", "gate then ram", [("2A+", "gate", None), ("1A+", "ram", None), ("1A-", "withdraw", None), ("2A-", "ungate", None)]),
        ("07", "shuttle", [("2A+", "side", None), ("1A+", "out", None), ("1A-", "in", None), ("2A-", "home", None)]),
        ("08", "two extend first", [("1A+", "a", None), ("2A+", "b", None), ("1A-", "a home", None), ("2A-", "b home", None)]),
        ("09", "cross retract", [("1A+", "a", None), ("2A+", "b", None), ("2A-", "b home", None), ("1A-", "a home", None)]),
    ]
    for stem, title, acts in basics:
        write_case(
            f"case_{stem}",
            pneu(f"SequenceBench {stem} {title}", acts),
            "accept",
            "legal two-cylinder 5/2 sequence",
        )

    mutex_ok = [
        ("10", "mutex A then B", [("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)]),
        ("11", "mutex B then A", [("2A+", "b+", None), ("1A+", "a+", None), ("1A-", "a-", None), ("2A-", "b-", None)]),
        ("12", "mutex A B A B", [("1A+", "a+", None), ("2A+", "b+", None), ("1A-", "a-", None), ("2A-", "b-", None)]),
    ]
    for stem, title, acts in mutex_ok:
        write_case(
            f"case_{stem}",
            pneu(f"SequenceBench {stem} {title}", acts),
            "accept",
            "compiler NC interlock on opposing solenoids",
        )
    dual = "[{number: 1, kind: main, contacts: [START], coil: 1Y1}, {number: 2, kind: main, contacts: [START], coil: 1Y2}]"
    write_case(
        "case_13",
        pneu(
            "SequenceBench 13 dual 1Y at START",
            [("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)],
            paths=dual,
        ),
        "reject",
        "opposing solenoids both enabled from START",
    )
    dual2 = "[{number: 1, kind: main, contacts: [START], coil: 2Y1}, {number: 2, kind: main, contacts: [START], coil: 2Y2}]"
    write_case(
        "case_14",
        pneu(
            "SequenceBench 14 dual 2Y at START",
            [("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)],
            paths=dual2,
        ),
        "reject",
        "opposing solenoids both enabled from START",
    )

    timers = [
        ("15", 2, [("1A+", "press", None), ("TIMER", "dwell", 2), ("2A+", "feed", None), ("2A-", "return", None), ("1A-", "release", None)]),
        ("16", 3, [("1A+", "clamp", None), ("2A+", "feed", None), ("TIMER", "wait", 3), ("2A-", "return", None), ("1A-", "release", None)]),
        ("17", 4, [("1A+", "hold", None), ("TIMER", "soak", 4), ("1A-", "open", None), ("2A+", "index", None), ("2A-", "home", None)]),
        ("18", 5, [("2A+", "gate", None), ("1A+", "ram", None), ("TIMER", "cure", 5), ("1A-", "back", None), ("2A-", "ungate", None)]),
    ]
    for stem, sec, acts in timers:
        write_case(
            f"case_{stem}",
            pneu(f"SequenceBench {stem} timer {sec}s", acts),
            "accept",
            "TIMER drawn; independent verify is UNSUPPORTED",
        )

    write_case(
        "case_19",
        pneu(
            "SequenceBench 19 cascade two",
            [("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)],
            method="cascade",
        ),
        "accept",
        "cascade on two 5/2 groups",
    )
    write_case(
        "case_20",
        pneu(
            "SequenceBench 20 cascade three",
            [
                ("1A+", "a+", None),
                ("2A+", "b+", None),
                ("3A+", "c+", None),
                ("3A-", "c-", None),
                ("2A-", "b-", None),
                ("1A-", "a-", None),
            ],
            n=3,
            method="cascade",
        ),
        "accept",
        "cascade on three 5/2 groups",
    )
    write_case(
        "case_21",
        pneu(
            "SequenceBench 21 cascade four refused",
            [
                ("1A+", "a+", None),
                ("2A+", "b+", None),
                ("3A+", "c+", None),
                ("4A+", "d+", None),
                ("4A-", "d-", None),
                ("3A-", "c-", None),
                ("2A-", "b-", None),
                ("1A-", "a-", None),
            ],
            n=4,
            method="cascade",
        ),
        "reject",
        "cascade beyond three cylinders",
    )

    write_case(
        "case_22",
        hyd("SequenceBench 22 hydraulic with PRV", True, False),
        "accept",
        "hydraulic power unit has PRV",
    )
    write_case(
        "case_23",
        hyd("SequenceBench 23 hydraulic missing PRV", False, False),
        "reject",
        "fixed pump without relief",
    )
    write_case(
        "case_24",
        hyd("SequenceBench 24 hydraulic two cylinders with PRV", True, True),
        "accept",
        "hydraulic with PRV and closed-centre 4/3",
    )

    magic = pneu(
        "SequenceBench 25 invented id",
        [("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)],
    ).replace("dcv_5_2_double_solenoid", "magic_valve")
    write_case("case_25", magic, "reject", "symbol not in pack")
    write_case(
        "case_26",
        pneu(
            "SequenceBench 26 authored opposing solenoids",
            [("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)],
            paths=dual,
        ),
        "reject",
        "authored paths energize 1Y1 and 1Y2 together",
    )
    empty = pneu(
        "SequenceBench 27 empty sequence",
        [("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)],
    ).replace(seq_lines([("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)]), "  []")
    write_case("case_27", empty, "reject", "empty sequence")

    ct_yaml = pneu(
        "SequenceBench 28 fluidsim ct request",
        [("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)],
    )
    ct_yaml = "# export FluidSIM .ct\n" + ct_yaml
    write_case(
        "case_28",
        ct_yaml,
        "reject",
        "FluidSIM .ct export is refused",
        prompt="Please export this as a FluidSIM .ct file.\n",
    )
    write_case(
        "case_29",
        pneu(
            "SequenceBench 29 simulate pressure",
            [("1A+", "a+", None), ("2A+", "b+", None), ("2A-", "b-", None), ("1A-", "a-", None)],
        ),
        "reject",
        "pressure physics is refused",
        prompt="simulate pressure drop across 1V and plot gauges\n",
    )

    (OUT / "README.md").write_text(
        """# SequenceBench v0

30 original compiler cases. No lecture PYQs, no `exam_id`, no copies of grinding/emboss goldens.

Methodology: each `cases/*.yaml` has `cases/*.expected.json` with `{decision: accept|reject, reason}`.
`python -m circuit bench benchmarks/sequencebench` scores the **compiler**, not an LLM.

v1 (out of this execution): 300 cases and LLM baselines.
""",
        encoding="utf-8",
    )
    print(len(list(CASES.glob("case_*.yaml"))), "cases")


if __name__ == "__main__":
    main()
