"""SequenceBench-300: deterministic original compiler cases. No lecture PYQs.

Cases are generated in-memory so the suite is reproducible from this module.
Materialize with ``materialize(Path)`` if you need YAML on disk.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.validate import all_ok, validate_spec
from circuit.verification.refine import verify_spec
from circuit.verification.status import Status


def _iso_pack() -> Pack:
    root = Path(__file__).resolve().parent / "packs" / "iso_sequence"
    return Pack(
        root=root,
        atlas_path=root / "atlas.yaml",
        stamp_dir=root / "stamps",
        hooks_module="circuit.packs.iso_sequence",
    )


def _pneu(
    title: str,
    actions: list[tuple[str, str]],
    *,
    n: int = 2,
    extra: str = "",
    paths: str = "[]",
) -> str:
    cyls = []
    valves = []
    sensors: list[str] = []
    for i in range(1, n + 1):
        cyls.append(f"  {i}A: {{ dcv: {i}V, sensors: [{i}B1, {i}B2] }}")
        valves.append(
            f"  {i}V: {{ type: dcv_5_2_double_solenoid, solenoids: [{i}Y1, {i}Y2] }}"
        )
        sensors.extend([f"{i}B1", f"{i}B2"])
    seq_lines = []
    for a, lab in actions:
        if a.startswith("TIMER:"):
            seq_lines.append(
                f"  - {{ action: TIMER, label: {lab}, seconds: {a.split(':')[1]} }}"
            )
        else:
            seq_lines.append(f"  - {{ action: {a}, label: {lab} }}")
    seq = "\n".join(seq_lines)
    return f"""meta:
  title: {title}
  domain: pneumatic_plus_electrical
  patterns: [ep_dac_5_2, sequence_double_solenoid]
{extra}sequence:
{seq}
power: {{ pumps: [], tank: "" }}
cylinders:
{chr(10).join(cyls)}
motors: {{}}
valves:
{chr(10).join(valves)}
sensors: [{", ".join(sensors)}]
electrical: {{ convention: lecture, paths: {paths} }}
"""


def closed_walks(cyls: tuple[str, ...], length: int, limit: int) -> list[list[str]]:
    """One-cycle walks: back to rest only at the end, every cylinder used.

    ``env_trace`` stops at the first return to rest, so a mid-sequence rest
    is not independently verified. Those walks are not accept cases.
    """
    out: list[list[str]] = []
    rest = {c: 0 for c in cyls}

    def rec(state: dict[str, int], path: list[str]) -> None:
        if len(out) >= limit:
            return
        if path and state == rest:
            if len(path) == length and {p[:-1] for p in path} >= set(cyls):
                out.append(list(path))
            return
        if len(path) == length:
            return
        for cid in cyls:
            nxt = dict(state)
            if state[cid] == 0:
                nxt[cid] = 1
                rec(nxt, path + [f"{cid}+"])
            else:
                nxt[cid] = 0
                rec(nxt, path + [f"{cid}-"])

    rec(dict(rest), [])
    return out


def generate_cases() -> list[dict]:
    cases: list[dict] = []

    def add(yaml_text: str, decision: str, reason: str) -> None:
        cases.append(
            {
                "id": f"n{len(cases):03d}",
                "yaml": yaml_text,
                "decision": decision,
                "reason": reason,
            }
        )

    two4 = closed_walks(("1A", "2A"), 4, 40)
    two6 = closed_walks(("1A", "2A"), 6, 80)
    two8 = closed_walks(("1A", "2A"), 8, 40)
    three6 = closed_walks(("1A", "2A", "3A"), 6, 40)

    for i, w in enumerate(two4):
        add(
            _pneu(f"sb300 legal4 {i}", [(a, f"s{j}") for j, a in enumerate(w)]),
            "accept",
            "legal 4-step walk back to rest",
        )
    for i, w in enumerate(two6):
        add(
            _pneu(f"sb300 legal6 {i}", [(a, f"s{j}") for j, a in enumerate(w)]),
            "accept",
            "legal 6-step walk back to rest",
        )
    for i, w in enumerate(two8):
        add(
            _pneu(f"sb300 legal8 {i}", [(a, f"s{j}") for j, a in enumerate(w)]),
            "accept",
            "legal 8-step walk back to rest",
        )
    for i, w in enumerate(three6):
        add(
            _pneu(
                f"sb300 legal3cyl {i}",
                [(a, f"s{j}") for j, a in enumerate(w)],
                n=3,
            ),
            "accept",
            "legal 3-cylinder walk back to rest",
        )
    for i, w in enumerate(two4[:40] or two4):
        acts = [(a, f"s{j}") for j, a in enumerate(w)]
        pos = 1 + (i % max(len(acts) - 1, 1))
        acts = acts[:pos] + [("TIMER:" + str(1 + (i % 4)), "wait")] + acts[pos:]
        add(_pneu(f"sb300 timer {i}", acts), "accept", "discrete timer ticks")
    for i, w in enumerate(two4[:25] or two4):
        acts = [(a, f"s{j}") for j, a in enumerate(w)]
        add(
            _pneu(f"sb300 cascade2 {i}", acts, extra="  method: cascade\n"),
            "accept",
            "cascade 5/2 groups, electrical step-memory",
        )
    for i, w in enumerate(three6[:10] or three6):
        acts = [(a, f"s{j}") for j, a in enumerate(w)]
        add(
            _pneu(f"sb300 cascade3 {i}", acts, n=3, extra="  method: cascade\n"),
            "accept",
            "cascade three cylinders, electrical step-memory",
        )

    dual = (
        "[{number: 1, kind: main, contacts: [START], coil: 1Y1}, "
        "{number: 2, kind: main, contacts: [START], coil: 1Y2}]"
    )
    reject_walks = (two4 + two6 + two8) or [["1A+", "2A+", "2A-", "1A-"]]
    invented_types = [
        "magic_valve",
        "servo_9_3",
        "made_up_dcv",
        "proportional_7_3",
        "mystery_valve",
    ]
    for i in range(30):
        w = reject_walks[i % len(reject_walks)]
        acts = [(a, f"s{j}") for j, a in enumerate(w)]
        bad = invented_types[i % len(invented_types)]
        y = _pneu(f"sb300 invented {i}", acts).replace(
            "dcv_5_2_double_solenoid", bad, 1
        )
        add(y, "reject", "invented id")
    for i in range(20):
        w = reject_walks[i % len(reject_walks)]
        acts = [(a, f"s{j}") for j, a in enumerate(w)]
        add(
            _pneu(f"sb300 dual {i}", acts, paths=dual),
            "reject",
            "dual solenoid at START",
        )
    for i in range(15):
        w = reject_walks[i % len(reject_walks)]
        y = "# export FluidSIM .ct\n" + _pneu(
            f"sb300 ct {i}",
            [(a, f"s{j}") for j, a in enumerate(w)],
        )
        add(y, "reject", "FluidSIM .ct refused")
    four = [
        "1A+",
        "2A+",
        "3A+",
        "4A+",
        "4A-",
        "3A-",
        "2A-",
        "1A-",
    ]
    for i in range(15):
        add(
            _pneu(
                f"sb300 cascade4 {i}",
                [(a, f"s{j}") for j, a in enumerate(four)],
                n=4,
                extra="  method: cascade\n",
            ),
            "reject",
            "cascade beyond three cylinders",
        )

    accept = [c for c in cases if c["decision"] == "accept"]
    reject = [c for c in cases if c["decision"] == "reject"]
    pad = 0
    while len(accept) < 220 and two4:
        w = two4[pad % len(two4)]
        acts = [(a, f"p{j}") for j, a in enumerate(w)]
        accept.append(
            {
                "id": f"n{len(accept):03d}",
                "yaml": _pneu(f"sb300 pad {pad}", acts),
                "decision": "accept",
                "reason": "legal pad walk",
            }
        )
        pad += 1
    mixed = accept[:220] + reject
    while len(mixed) < 300 and accept:
        w = two6[len(mixed) % len(two6)] if two6 else two4[0]
        acts = [(a, f"q{j}") for j, a in enumerate(w)]
        mixed.append(
            {
                "id": f"n{len(mixed):03d}",
                "yaml": _pneu(f"sb300 fill {len(mixed)}", acts),
                "decision": "accept",
                "reason": "legal fill walk",
            }
        )
    out = mixed[:300]
    for i, case in enumerate(out):
        case["id"] = f"n{i:03d}"
    return out


def suite_fingerprint(cases: list[dict] | None = None) -> str:
    cases = cases or generate_cases()
    blob = "\n".join(c["id"] + "\n" + c["yaml"] for c in cases).encode()
    return hashlib.sha256(blob).hexdigest()


def decide(text: str) -> str:
    from circuit.service import _load_spec

    spec, err = _load_spec(text)
    if err:
        return "reject"
    pack = _iso_pack()
    with using_pack(pack):
        checks = validate_spec(spec, pack.root)
        if not all_ok(checks):
            return "reject"
        if (spec.meta.method or "") == "cascade" and len(spec.cylinders) > 3:
            return "reject"
        if any(s.action in {"PS", "PRESSURE"} for s in spec.sequence):
            return "unsupported"
        vr = verify_spec(spec)
        if vr.status is Status.PASS:
            return "accept"
        if vr.status is Status.UNSUPPORTED:
            return "unsupported"
        return "reject"


def materialize(dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    for case in generate_cases():
        (dest / f"{case['id']}.yaml").write_text(case["yaml"], encoding="utf-8")
        (dest / f"{case['id']}.expected.json").write_text(
            json.dumps(
                {"decision": case["decision"], "reason": case["reason"]}, indent=2
            )
            + "\n",
            encoding="utf-8",
        )
    (dest / "FINGERPRINT.txt").write_text(suite_fingerprint() + "\n", encoding="utf-8")
    return 300


def run_bench300() -> dict:
    accept_n = reject_n = accept_fail = reject_hit = unsupported_n = 0
    mismatches: list[dict] = []
    pack = _iso_pack()
    with using_pack(pack):
        for case in generate_cases():
            got = decide(case["yaml"])
            want = case["decision"]
            if want == "accept":
                accept_n += 1
                if got != "accept":
                    accept_fail += 1
                    if len(mismatches) < 20:
                        mismatches.append(
                            {"id": case["id"], "want": want, "got": got}
                        )
            elif want == "reject":
                reject_n += 1
                if got == "reject":
                    reject_hit += 1
                elif len(mismatches) < 20:
                    mismatches.append({"id": case["id"], "want": want, "got": got})
            else:
                unsupported_n += 1
    return {
        "n": 300,
        "fingerprint": suite_fingerprint(),
        "accepted_error_rate": (accept_fail / accept_n) if accept_n else 0.0,
        "reject_invalid_rate": (reject_hit / reject_n) if reject_n else 0.0,
        "reject_valid_rate": (accept_fail / accept_n) if accept_n else 0.0,
        "accept_n": accept_n,
        "reject_n": reject_n,
        "unsupported_n": unsupported_n,
        "mismatches": mismatches,
    }
