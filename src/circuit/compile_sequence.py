"""Sequence → electrical current paths + step-displacement rows (L8/L10)."""

from __future__ import annotations

from circuit.spec import CircuitSpec, CurrentPath, SeqStep


def _start_and_latch(spec: CircuitSpec) -> tuple[list[str], list[str]]:
    sensors = set(spec.sensors)
    start: list[str] = []
    if "S1" in sensors:
        start.append("S1")
        if "S3" in sensors:
            start.append("S3")
    else:
        start.append("START")
        if "JOB" in sensors:
            start.append("JOB")
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
    latch = ["K_START"]
    if "JOB" in sensors:
        latch.append("JOB")
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


def compile_paths(spec: CircuitSpec) -> list[CurrentPath]:
    if spec.electrical.paths:
        return spec.electrical.paths

    paths: list[CurrentPath] = []
    n = 1
    start_contacts, latch = _start_and_latch(spec)
    paths.append(
        CurrentPath(number=n, kind="control", contacts=start_contacts, coil="K_START")
    )
    n += 1
    paths.append(
        CurrentPath(number=n, kind="control", contacts=latch, coil="K_START")
    )
    n += 1

    prev_contacts = ["K_START"]
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
            prev_contacts = [f"T1"]
            n += 1
            continue
        if coil:
            paths.append(
                CurrentPath(number=n, kind="main", contacts=contacts, coil=coil)
            )
            n += 1
            # next step waits on the actuator's extend/retract sensor when present
            cid = step.action.rstrip("+-").replace("_ON", "")
            cyl = spec.cylinders.get(cid)
            if cyl and cyl.sensors:
                prev_contacts = [cyl.sensors[-1] if step.action.endswith("+") else cyl.sensors[0]]
            elif cid in spec.motors:
                prev_contacts = ["K_START"]

    control = [p for p in paths if p.kind != "main"]
    main = [p for p in paths if p.kind == "main"]
    return [
        p.model_copy(update={"number": i})
        for i, p in enumerate(control + main, start=1)
    ]


def displacement_rows(sequence: list[SeqStep]) -> list[dict[str, str]]:
    rows = []
    for i, step in enumerate(sequence, start=1):
        rows.append({"step": str(i), "action": step.action, "label": step.label})
    return rows


def apply_compile(spec: CircuitSpec) -> CircuitSpec:
    compiled = spec.model_copy(deep=True)
    compiled.electrical.paths = compile_paths(spec)
    return compiled
