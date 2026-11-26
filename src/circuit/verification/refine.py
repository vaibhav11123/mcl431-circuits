from __future__ import annotations

from dataclasses import dataclass

from circuit.ir.from_spec import from_spec
from circuit.semantics.graph_trace import graph_trace, sensor_envs_from_positions
from circuit.semantics.spec_trace import spec_trace
from circuit.spec import CircuitSpec


@dataclass
class VerifyResult:
    ok: bool
    cex_step: int | None = None
    src_row: dict | None = None
    tgt_row: dict | None = None


def refine(src: list[dict], tgt: list[dict]) -> VerifyResult:
    n = min(len(src), len(tgt))
    for i in range(n):
        if src[i] != tgt[i]:
            return VerifyResult(ok=False, cex_step=i, src_row=src[i], tgt_row=tgt[i])
    if len(src) != len(tgt):
        return VerifyResult(
            ok=False,
            cex_step=n,
            src_row=src[n] if n < len(src) else None,
            tgt_row=tgt[n] if n < len(tgt) else None,
        )
    return VerifyResult(ok=True)


def verify_spec(spec: CircuitSpec) -> VerifyResult:
    from circuit.verification.mutex import start_dual_solenoid

    src = spec_trace(spec)
    graph = from_spec(spec)
    mx = start_dual_solenoid(graph)
    if not mx["ok"]:
        return VerifyResult(ok=False, cex_step=0, src_row=mx.get("cex"), tgt_row=None)
    from circuit.compile_sequence import _solenoid_for

    envs: list[dict[str, bool]] = [{"START": False}]
    for step in spec.sequence:
        env: dict[str, bool] = {"START": True, "K1": True}
        coil = _solenoid_for(spec, step.action)
        path = next((p for p in graph.paths if p.coil == coil), None)
        if path:
            for c in path.contacts or []:
                name = c[1:] if c.startswith("!") else c
                env[name] = not c.startswith("!")
        envs.append(env)
    tgt = graph_trace(graph, envs)
    return refine(src, tgt)
