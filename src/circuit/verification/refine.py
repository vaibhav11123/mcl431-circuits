from __future__ import annotations

from dataclasses import dataclass, field

from circuit.ir.from_spec import from_spec
from circuit.semantics.env_trace import compress_changes, env_trace
from circuit.semantics.spec_trace import spec_trace
from circuit.spec import CircuitSpec
from circuit.verification.status import Status


@dataclass
class VerifyResult:
    ok: bool
    status: Status = Status.PASS
    cex_step: int | None = None
    src_row: dict | None = None
    tgt_row: dict | None = None
    stats: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status is Status.PASS:
            self.ok = True
        else:
            self.ok = False


def _result(
    status: Status,
    *,
    cex_step: int | None = None,
    src_row: dict | None = None,
    tgt_row: dict | None = None,
    stats: dict | None = None,
) -> VerifyResult:
    return VerifyResult(
        ok=status is Status.PASS,
        status=status,
        cex_step=cex_step,
        src_row=src_row,
        tgt_row=tgt_row,
        stats=stats or {},
    )


def refine(src: list[dict], tgt: list[dict]) -> VerifyResult:
    n = min(len(src), len(tgt))
    for i in range(n):
        if src[i] != tgt[i]:
            return _result(Status.FAIL, cex_step=i, src_row=src[i], tgt_row=tgt[i])
    if len(src) != len(tgt):
        return _result(
            Status.FAIL,
            cex_step=n,
            src_row=src[n] if n < len(src) else None,
            tgt_row=tgt[n] if n < len(tgt) else None,
        )
    return _result(Status.PASS)


def verify_spec(spec: CircuitSpec) -> VerifyResult:
    from circuit.verification.mutex import start_dual_solenoid

    if any(s.action == "TIMER" for s in spec.sequence):
        return _result(Status.UNSUPPORTED, stats={"reason": "TIMER"})
    if (spec.meta.method or "") == "cascade":
        return _result(Status.UNSUPPORTED, stats={"reason": "cascade"})
    src = spec_trace(spec)
    graph = from_spec(spec)
    mx = start_dual_solenoid(graph)
    if not mx["ok"]:
        return _result(
            Status.FAIL,
            cex_step=0,
            src_row=mx.get("cex"),
            tgt_row=None,
            stats={"check": "start_dual_solenoid"},
        )
    run = env_trace(graph)
    if run.get("conflict"):
        return _result(
            Status.FAIL,
            cex_step=int(run["conflict"].get("step") or 0),
            src_row=run["conflict"],
            tgt_row=None,
            stats={"check": "env_conflict"},
        )
    if run.get("exhausted"):
        return _result(
            Status.INCONCLUSIVE,
            stats={"check": "env_trace", "max_steps": run.get("max_steps")},
        )
    tgt = compress_changes(run["rows"])
    out = refine(src, tgt)
    out.stats = {
        "check": "env_trace",
        "transitions": run.get("transitions"),
        "states": run.get("states"),
    }
    return out
