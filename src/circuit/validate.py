"""Catalog lock + hydraulic graph + no-invention."""

from __future__ import annotations

from pathlib import Path

import yaml

from circuit.spec import CircuitSpec, Domain, PatternId


class Check:
    def __init__(self, name: str, ok: bool, detail: str = "") -> None:
        self.name = name
        self.ok = ok
        self.detail = detail

    def __bool__(self) -> bool:
        return self.ok


def load_atlas_ids(root: Path) -> set[str]:
    atlas = yaml.safe_load((root / "lecture" / "atlas.yaml").read_text()) or {}
    return {s["id"] for s in atlas.get("symbols") or [] if "id" in s}


def validate_spec(spec: CircuitSpec, root: Path | None = None) -> list[Check]:
    root = root or Path(__file__).resolve().parents[2]
    checks: list[Check] = []
    atlas = load_atlas_ids(root)

    hyd = spec.meta.domain in {
        Domain.HYDRAULIC,
        Domain.HYDRAULIC_PLUS_ELECTRICAL,
    }
    pneu = spec.meta.domain in {
        Domain.PNEUMATIC,
        Domain.PNEUMATIC_PLUS_ELECTRICAL,
    }
    if spec.meta.figure_given:
        checks.append(Check("figure_given", True, "calc only — circuit is on the paper"))
    elif spec.power.pumps:
        checks.append(Check("has_pump", True, ",".join(p.id for p in spec.power.pumps)))
    elif pneu:
        checks.append(Check("has_pump", True, "pneumatic — no hydraulic pump"))
    else:
        checks.append(Check("has_pump", False, "no pump"))
    if hyd and not spec.meta.figure_given:
        checks.append(
            Check(
                "has_prv",
                bool(spec.power.relief_valves),
                "PRV required on every hydraulic power unit (L3)",
            )
        )
        checks.append(Check("has_tank", bool(spec.power.tank), spec.power.tank))

    for cid, cyl in spec.cylinders.items():
        checks.append(Check(f"cyl_{cid}_dcv", bool(cyl.dcv), cyl.dcv))
        if cyl.dcv not in spec.valves:
            checks.append(Check(f"cyl_{cid}_valve_defined", False, cyl.dcv))
        else:
            checks.append(Check(f"cyl_{cid}_valve_defined", True, cyl.dcv))
        for s in cyl.sensors:
            checks.append(Check(f"sensor_{s}", s in spec.sensors, s))

    for vid, valve in spec.valves.items():
        if atlas:
            checks.append(
                Check(
                    f"valve_{vid}_in_atlas",
                    valve.type in atlas,
                    valve.type,
                )
            )
        else:
            checks.append(Check(f"valve_{vid}_typed", bool(valve.type), valve.type))
        needs_y = valve.type.startswith("dcv") or "solenoid" in valve.type
        if needs_y and not valve.solenoids:
            checks.append(Check(f"valve_{vid}_solenoids", False, "missing Y tags"))
        elif valve.solenoids:
            checks.append(Check(f"valve_{vid}_solenoids", True, ",".join(valve.solenoids)))

    if PatternId.HILO_DOUBLE_PUMP in spec.meta.patterns and not spec.meta.figure_given:
        checks.append(
            Check(
                "hilo_two_pumps",
                len(spec.power.pumps) >= 2,
                f"pumps={len(spec.power.pumps)}",
            )
        )
        has_uv = any(v.type == "unloading_valve" for v in spec.valves.values())
        checks.append(Check("hilo_has_uv", has_uv, "unloading_valve required (L4 p13)"))

    extra_flow = PatternId.METER_IN in spec.meta.patterns or PatternId.METER_OUT in spec.meta.patterns
    if not extra_flow:
        sneaky = [v for v in spec.valves.values() if "flow" in v.type or "meter" in v.type]
        checks.append(Check("no_extra_fcv", not sneaky, "question did not ask for FCV"))

    coils = [s for v in spec.valves.values() for s in v.solenoids]
    path_coils = [p.coil for p in spec.electrical.paths if p.coil]
    if path_coils:
        missing = [c for c in coils if c not in path_coils]
        checks.append(Check("coil_tag_bijection", not missing, ",".join(missing)))

    if spec.sequence:
        checks.append(Check("has_sequence", True, f"{len(spec.sequence)} steps"))
    elif spec.meta.figure_given:
        checks.append(Check("has_sequence", True, "figure given — no sequence to draw"))
    else:
        checks.append(Check("has_sequence", False, "empty"))

    return checks


def all_ok(checks: list[Check]) -> bool:
    return all(c.ok for c in checks)
