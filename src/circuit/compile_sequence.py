"""Sequence → electrical current paths + step-displacement rows (L8/L10)."""

from __future__ import annotations

from circuit.spec import CircuitSpec, CurrentPath, SeqStep


def nc(tag: str) -> str:
    """NC contact (relay, timer, or opposing solenoid interlock)."""
    return tag if tag.startswith("!") else f"!{tag}"


def bare(tag: str) -> str:
    return tag[1:] if tag.startswith("!") else tag


def _start_and_latch(spec: CircuitSpec) -> tuple[list[str], list[str]]:
    sensors = set(spec.sensors)
    start: list[str] = []
    if "S1" in sensors:
        start.append("S1")
        if "S3" in sensors:
            start.append("S3")
        if "S0" in sensors:
            start.append("S0")
    else:
        start.append("START")
        if "JOB" in sensors:
            start.append("JOB")
        elif "S0" in sensors:
            start.append("S0")
    first: dict[str, str] = {}
    for step in spec.sequence:
        act = step.action
        if act.endswith("+") or act.endswith("-"):
            first.setdefault(act[:-1], act)
    for cid, cyl in spec.cylinders.items():
        if not cyl.sensors:
            continue
        fa = first.get(cid, "")
        if fa.endswith("-") and len(cyl.sensors) > 1:
            start.append(cyl.sensors[-1])
        else:
            start.append(cyl.sensors[0])
    latch = ["K1"]
    if "JOB" in sensors:
        latch.append("JOB")
    elif "S0" in sensors:
        latch.append("S0")
    elif "S1" in sensors:
        latch.append("S1")
    return start, latch


def _solenoid_for(spec: CircuitSpec, action: str) -> str | None:
    if action.endswith("_ON"):
        mid = action[: -len("_ON")]
        motor = spec.motors.get(mid)
        if motor:
            return spec.valves[motor.dcv].solenoids[0]
        return None
    if action.endswith("+"):
        cid = action[:-1]
        cyl = spec.cylinders.get(cid)
        if cyl:
            return spec.valves[cyl.dcv].solenoids[0]
    if action.endswith("-"):
        cid = action[:-1]
        cyl = spec.cylinders.get(cid)
        if cyl:
            sols = spec.valves[cyl.dcv].solenoids
            return sols[1] if len(sols) > 1 else sols[0]
    return None


def _renumber(paths: list[CurrentPath]) -> list[CurrentPath]:
    control = [p for p in paths if p.kind != "main"]
    main = [p for p in paths if p.kind == "main"]
    return [
        p.model_copy(update={"number": i})
        for i, p in enumerate(control + main, start=1)
    ]


def _compile_motor_timer_double_solenoid(spec: CircuitSpec) -> list[CurrentPath]:
    """B1-style step relays: K1 → K2 → K3 → K4.

    Each step coil is one path. Motor running is K2 (not 3Y1 as a sequence
    contact). Opposing solenoids are NC-interlocked so 1Y1∧1Y2 and 2Y1∧2Y2
    cannot both be commanded.
    """
    cyl_ids = list(spec.cylinders)
    mot_id = next(iter(spec.motors))
    c1, c2 = cyl_ids[0], cyl_ids[1]
    s1 = spec.cylinders[c1].sensors
    s2 = spec.cylinders[c2].sensors
    y1 = spec.valves[spec.cylinders[c1].dcv].solenoids
    y2 = spec.valves[spec.cylinders[c2].dcv].solenoids
    ym = spec.valves[spec.motors[mot_id].dcv].solenoids[0]
    seconds = next((int(s.seconds or 0) for s in spec.sequence if s.action == "TIMER"), 0)
    end1 = s1[-1] if s1 else "1B2"
    home2, end2 = (s2[0], s2[-1]) if s2 else ("2B1", "2B2")
    k_hm, k_done, k_feed = "K2", "K4", "K3"
    start, latch = _start_and_latch(spec)

    paths = [
        CurrentPath(number=1, kind="control", contacts=start, coil="K1"),
        CurrentPath(number=2, kind="control", contacts=latch, coil="K1"),
        CurrentPath(number=3, kind="control", contacts=[end1, nc(k_done)], coil=k_hm),
        CurrentPath(number=4, kind="control", contacts=[end2], coil=f"T1_{seconds}s"),
        CurrentPath(number=5, kind="control", contacts=["T1"], coil=k_done),
        CurrentPath(
            number=6,
            kind="control",
            contacts=[k_hm, home2, nc(k_done)],
            coil=k_feed,
        ),
        CurrentPath(
            number=7,
            kind="main",
            contacts=["K1", nc(k_done), nc(y1[1])],
            coil=y1[0],
        ),
        CurrentPath(number=8, kind="main", contacts=[k_hm, nc(k_done)], coil=ym),
        CurrentPath(
            number=9,
            kind="main",
            contacts=[k_feed, nc(k_done), nc(y2[1])],
            coil=y2[0],
        ),
        CurrentPath(number=10, kind="main", contacts=[k_done, nc(y2[0])], coil=y2[1]),
        CurrentPath(
            number=11,
            kind="main",
            contacts=[k_done, home2, nc(y1[0])],
            coil=y1[1],
        ),
    ]
    return _renumber(paths)


def _compile_chain(spec: CircuitSpec) -> list[CurrentPath]:
    paths: list[CurrentPath] = []
    n = 1
    start_contacts, latch = _start_and_latch(spec)
    paths.append(
        CurrentPath(number=n, kind="control", contacts=start_contacts, coil="K1")
    )
    n += 1
    paths.append(
        CurrentPath(number=n, kind="control", contacts=latch, coil="K1")
    )
    n += 1

    prev_contacts = ["K1"]
    emitted_k: set[str] = set()
    for step in spec.sequence:
        coil = _solenoid_for(spec, step.action)
        contacts = list(prev_contacts)
        if step.action == "TIMER":
            paths.append(
                CurrentPath(
                    number=n,
                    kind="control",
                    contacts=contacts,
                    coil=f"T1_{int(step.seconds or 0)}s",
                )
            )
            prev_contacts = ["T1"]
            n += 1
            continue
        if coil and step.action.endswith("_ON"):
            mid = step.action[: -len("_ON")]
            k_hm = f"K_{mid}"
            if k_hm not in emitted_k:
                paths.append(
                    CurrentPath(number=n, kind="control", contacts=contacts, coil=k_hm)
                )
                n += 1
                emitted_k.add(k_hm)
            paths.append(
                CurrentPath(number=n, kind="main", contacts=[k_hm], coil=coil)
            )
            n += 1
            prev_contacts = [k_hm]
            continue
        if coil:
            paths.append(
                CurrentPath(number=n, kind="main", contacts=contacts, coil=coil)
            )
            n += 1
            cid = step.action.rstrip("+-").replace("_ON", "")
            cyl = spec.cylinders.get(cid)
            if cyl and cyl.sensors:
                prev_contacts = [
                    cyl.sensors[-1] if step.action.endswith("+") else cyl.sensors[0]
                ]
            elif cid in spec.motors:
                prev_contacts = [f"K_{cid}"]

    if "H1" in spec.sensors:
        paths.append(
            CurrentPath(number=n, kind="main", contacts=["2B1", "1B1"], coil="H1")
        )

    return _renumber(paths)


def _opposing_solenoid(sol: str) -> str:
    if sol.endswith("1"):
        return sol[:-1] + "2"
    if sol.endswith("2"):
        return sol[:-1] + "1"
    return sol


def _compile_indexing_drill(spec: CircuitSpec) -> list[CurrentPath]:
    """Fall-17 Minor-2: 12 motions as K2–K13, K1 cycle, K14 done, KM with K1.

    Closed-centre 5/3 needs each solenoid held until the next step is set.
    Paper: spindle ON from START until holes are drilled (drops at return K13).
    """
    start, latch = _start_and_latch(spec)
    motions = [
        ("3Y1", ["1B1", "2B1", "3B1"]),
        ("3Y2", ["3B2"]),
        ("1Y1", ["3B1", "1B1", "2B1"]),
        ("3Y1", ["1B2", "2B1", "3B1"]),
        ("3Y2", ["3B2"]),
        ("2Y1", ["3B1", "1B2", "2B1"]),
        ("3Y1", ["1B2", "2B2", "3B1"]),
        ("3Y2", ["3B2"]),
        ("1Y2", ["3B1", "1B2", "2B2"]),
        ("3Y1", ["1B1", "2B2", "3B1"]),
        ("3Y2", ["3B2"]),
        ("2Y2", ["3B1", "1B1", "2B2"]),
    ]
    n_steps = len(motions)
    k_first = 2
    k_last = k_first + n_steps - 1  # K13
    k_done = f"K{k_last + 1}"  # K14
    k_return = f"K{k_last}"  # K13
    paths = [
        CurrentPath(number=1, kind="control", contacts=start, coil="K1"),
        CurrentPath(
            number=2,
            kind="control",
            contacts=[*latch, nc(k_done)],
            coil="K1",
        ),
    ]
    prev = "K1"
    for i, (sol, enable) in enumerate(motions):
        k = f"K{k_first + i}"
        nxt = f"K{k_first + i + 1}"
        paths.append(
            CurrentPath(number=0, kind="control", contacts=[prev, *enable], coil=k)
        )
        paths.append(
            CurrentPath(number=0, kind="control", contacts=[k, nc(nxt)], coil=k)
        )
        paths.append(
            CurrentPath(
                number=0,
                kind="main",
                contacts=[k, nc(_opposing_solenoid(sol))],
                coil=sol,
            )
        )
        prev = k
    paths.append(
        CurrentPath(number=0, kind="control", contacts=[k_return, "2B1"], coil=k_done)
    )
    paths.append(
        CurrentPath(number=0, kind="main", contacts=["K1", nc(k_return)], coil="KM")
    )
    return _renumber(paths)


def is_wait_step(action: str) -> bool:
    """Non-motion holds: timer or pressure-switch wait (not an end sensor)."""
    return action in {"TIMER", "PS", "PRESSURE"}


def _compile_emboss_2016(spec: CircuitSpec) -> list[CurrentPath]:
    """Fall-16 Minor-1 Q2: clamp, emboss, hold until PS≥4 bar, then retract.

    2A1 must not retract on 2B2. 1Y2 cannot be a raw 2B1 (true at rest).
    """
    start, latch = _start_and_latch(spec)
    y1 = spec.valves[spec.cylinders["1A1"].dcv].solenoids
    y2 = spec.valves[spec.cylinders["2A1"].dcv].solenoids
    paths = [
        CurrentPath(number=1, kind="control", contacts=start, coil="K1"),
        CurrentPath(
            number=2,
            kind="control",
            contacts=[*latch, nc("K5")],
            coil="K1",
        ),
        CurrentPath(
            number=3,
            kind="control",
            contacts=["K1", "1B2", nc("K4")],
            coil="K3",
        ),
        CurrentPath(number=4, kind="control", contacts=["K3", "PS"], coil="K4"),
        CurrentPath(
            number=5,
            kind="control",
            contacts=["K4", nc("K5")],
            coil="K4",
        ),
        CurrentPath(number=6, kind="control", contacts=["K4", "2B1"], coil="K5"),
        CurrentPath(number=7, kind="control", contacts=["K5", "1B2"], coil="K5"),
        CurrentPath(
            number=8,
            kind="main",
            contacts=["K1", nc("K5"), nc(y1[1])],
            coil=y1[0],
        ),
        CurrentPath(
            number=9,
            kind="main",
            contacts=["K3", nc("K4"), nc(y2[1])],
            coil=y2[0],
        ),
        CurrentPath(
            number=10,
            kind="main",
            contacts=["K4", nc(y2[0])],
            coil=y2[1],
        ),
        CurrentPath(
            number=11,
            kind="main",
            contacts=["K5", nc(y1[0])],
            coil=y1[1],
        ),
    ]
    return _renumber(paths)


def compile_paths(spec: CircuitSpec) -> list[CurrentPath]:
    if spec.electrical.paths:
        return spec.electrical.paths
    if spec.meta.exam_id == "2016_minor1_emboss":
        return _compile_emboss_2016(spec)
    if spec.meta.exam_id in {"Fall17-Minor2", "MCL431_Minor2_2017-18_Sem1"}:
        return _compile_indexing_drill(spec)
    if spec.cylinders and all(
        spec.valves[c.dcv].type == "dcv_5_3" for c in spec.cylinders.values()
    ):
        return _compile_indexing_drill(spec)
    timer = any(s.action == "TIMER" for s in spec.sequence)
    if spec.motors and timer and len(spec.cylinders) >= 2:
        return _compile_motor_timer_double_solenoid(spec)
    return _compile_chain(spec)


def displacement_rows(sequence: list[SeqStep]) -> list[dict[str, str]]:
    rows = []
    for i, step in enumerate(sequence, start=1):
        rows.append({"step": str(i), "action": step.action, "label": step.label})
    return rows


def apply_compile(spec: CircuitSpec) -> CircuitSpec:
    compiled = spec.model_copy(deep=True)
    compiled.electrical.paths = compile_paths(spec)
    return compiled
