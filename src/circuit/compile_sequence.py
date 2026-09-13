"""Sequence → electrical current paths + step-displacement rows (L8/L10)."""

from __future__ import annotations

from circuit.spec import CircuitSpec, CurrentPath, SeqStep


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
    start_contacts = ["START"]
    if "JOB" in spec.sensors:
        start_contacts.append("JOB")
    paths.append(
        CurrentPath(number=n, kind="control", contacts=start_contacts, coil="K_START")
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
    return paths


def displacement_rows(sequence: list[SeqStep]) -> list[dict[str, str]]:
    rows = []
    for i, step in enumerate(sequence, start=1):
        rows.append({"step": str(i), "action": step.action, "label": step.label})
    return rows


def apply_compile(spec: CircuitSpec) -> CircuitSpec:
    compiled = spec.model_copy(deep=True)
    compiled.electrical.paths = compile_paths(spec)
    return compiled
