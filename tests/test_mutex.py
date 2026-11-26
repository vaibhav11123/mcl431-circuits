from circuit.ir.graph import CircuitGraph, GraphNode
from circuit.spec import CurrentPath
from circuit.verification.mutex import SENSOR_BOUND, mutex_explore, start_dual_solenoid
from circuit.verification.status import Status


def test_mutex_truncated_is_inconclusive() -> None:
    sensors = {f"S{i}": f"S{i}" for i in range(SENSOR_BOUND + 1)}
    graph = CircuitGraph(
        nodes=[GraphNode(id="1A", kind="cylinder", domain="fluid")],
        paths=[],
        solenoid_plus={"1A": "1Y1"},
        solenoid_minus={"1A": "1Y2"},
        sensors_home=sensors,
        sensors_end={},
    )
    out = mutex_explore(graph)
    assert out["ok"] is False
    assert out["status"] == Status.INCONCLUSIVE.value


def test_start_dual_solenoid_pass_on_empty() -> None:
    graph = CircuitGraph(nodes=[GraphNode(id="1A", kind="cylinder")])
    out = start_dual_solenoid(graph)
    assert out["ok"] is True
    assert out["status"] == Status.PASS.value


def test_start_dual_solenoid_fail() -> None:
    graph = CircuitGraph(
        nodes=[GraphNode(id="1A", kind="cylinder")],
        paths=[
            CurrentPath(number=1, kind="main", contacts=["START"], coil="1Y1"),
            CurrentPath(number=2, kind="main", contacts=["START"], coil="1Y2"),
        ],
        solenoid_plus={"1A": "1Y1"},
        solenoid_minus={"1A": "1Y2"},
    )
    out = start_dual_solenoid(graph)
    assert out["ok"] is False
    assert out["status"] == Status.FAIL.value
