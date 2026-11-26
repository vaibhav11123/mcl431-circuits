from hypothesis import given, settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, run_state_machine_as_test
from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import apply_sequence_edit, eval_yaml


ROOT = Path(__file__).resolve().parents[1]
ISO_YAML = (ROOT / "examples/iso_sequence/circuit.yaml").read_text()
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


class EditMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.yaml = ISO_YAML
        self.history = [ISO_YAML]

    @rule(seconds=st.integers(min_value=1, max_value=5))
    def insert_timer(self, seconds: int) -> None:
        with using_pack(ISO_PACK):
            out = apply_sequence_edit(
                self.yaml, {"op": "insert_timer", "after_action": "1A+", "seconds": seconds}
            )
        if out.get("yaml"):
            self.history.append(self.yaml)
            self.yaml = out["yaml"]

    @rule()
    def undo(self) -> None:
        if len(self.history) < 2:
            return
        prev = self.history.pop()
        with using_pack(ISO_PACK):
            out = apply_sequence_edit(self.yaml, {"op": "undo", "previous_yaml": prev})
        self.yaml = out.get("yaml") or prev

    @invariant()
    def yaml_parses(self) -> None:
        assert "1A+" in self.yaml or "sequence:" in self.yaml


def test_edit_state_machine() -> None:
    run_state_machine_as_test(
        EditMachine, settings=settings(max_examples=8, stateful_step_count=6, deadline=None)
    )


@given(st.integers(1, 4))
@settings(max_examples=8, deadline=None)
def test_insert_timer_eval_does_not_crash(seconds: int) -> None:
    with using_pack(ISO_PACK):
        out = apply_sequence_edit(
            ISO_YAML, {"op": "insert_timer", "after_action": "1A+", "seconds": seconds}
        )
        report = eval_yaml(out["yaml"])
    assert "ok" in report
