"""Pydantic circuit spec — YAML in, no coordinates."""

from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")
_GENERIC_PARENTS = {"examples", "lecture", "goldens", "output", "exams"}


class Domain(str, Enum):
    HYDRAULIC = "hydraulic"
    PNEUMATIC = "pneumatic"
    HYDRAULIC_PLUS_ELECTRICAL = "hydraulic_plus_electrical"
    PNEUMATIC_PLUS_ELECTRICAL = "pneumatic_plus_electrical"
    PLC = "plc"


class PatternId(str, Enum):
    SAC_3_2 = "sac_3_2"
    DAC_4_3 = "dac_4_3"
    REGEN = "regen"
    UNLOAD = "unload"
    HILO_DOUBLE_PUMP = "hilo_double_pump"
    SEQUENCE_VALVE = "sequence_valve"
    LOCKED_CYLINDER = "locked_cylinder"
    MOTOR_4_3 = "motor_4_3"
    METER_IN = "meter_in"
    METER_OUT = "meter_out"
    BLEED_OFF = "bleed_off"
    EP_DAC_5_2 = "ep_dac_5_2"
    SEQUENCE_DOUBLE_SOLENOID = "sequence_double_solenoid"
    TIMER_PULL_IN = "timer_pull_in"


class SeqStep(BaseModel):
    action: str
    label: str = ""
    seconds: float | None = None


class Cylinder(BaseModel):
    bore_mm: float | None = None
    rod_mm: float | None = None
    dcv: str
    sensors: list[str] = Field(default_factory=list)
    force_kn: float | None = None
    approach_cm: float | None = None


class Motor(BaseModel):
    dcv: str
    rpm: float | None = None


class Valve(BaseModel):
    type: str
    solenoids: list[str] = Field(default_factory=list)


class Pump(BaseModel):
    id: str
    flow_lpm: float | None = None


class Relief(BaseModel):
    id: str
    pump: str


class Power(BaseModel):
    pumps: list[Pump]
    relief_valves: list[Relief] = Field(default_factory=list)
    tank: str = "TANK"


class CurrentPath(BaseModel):
    number: int
    kind: str = "control"  # control | main
    contacts: list[str] = Field(default_factory=list)
    coil: str | None = None


class Electrical(BaseModel):
    convention: str = "lecture"
    paths: list[CurrentPath] = Field(default_factory=list)


class Meta(BaseModel):
    title: str
    domain: Domain
    patterns: list[PatternId] = Field(default_factory=list)
    exam_id: str | None = None
    figure_given: bool = False


class PlcIoRow(BaseModel):
    address: str
    device: str
    function: str = ""


class PlcFieldBox(BaseModel):
    title: str
    lines: list[str] = Field(default_factory=list)


class PlcScalingChannel(BaseModel):
    eng_max: float
    bits: int
    slot: int | None = None
    channel: int | None = None
    unit: str = ""
    eng_min: float = 0.0


class PlcScaling(BaseModel):
    ai: PlcScalingChannel | None = None
    ao: PlcScalingChannel | None = None
    checkpoints: dict[str, float] = Field(default_factory=dict)
    counts: dict[str, int] = Field(default_factory=dict)


class PlcElement(BaseModel):
    kind: str
    tag: str = ""
    label: str = ""
    sense: str = "NO"
    op: str = ""
    left: str = ""
    right: str = ""
    right_from: str = ""
    value: str | int | float | None = None
    value_from: str = ""
    dest: str = ""
    preset: int | float | None = None
    text: str = ""

    @field_validator("sense", mode="before")
    @classmethod
    def _yaml_no_is_false(cls, v: object) -> str:
        # PyYAML parses bare NO as False
        if v is False or v is None:
            return "NO"
        if v is True:
            return "NO"
        return str(v)


class PlcRung(BaseModel):
    id: int | str
    caption: str = ""
    series: list[PlcElement] = Field(default_factory=list)
    branch: list[PlcElement] = Field(default_factory=list)
    output: PlcElement | None = None


class PlcBlock(BaseModel):
    io: list[PlcIoRow] = Field(default_factory=list)
    field: list[PlcFieldBox] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    subtitle_connection: str = "PLC connection diagram"
    subtitle_ladder: str = "PLC ladder"
    scaling: PlcScaling | None = None
    scale_table: list[list[str]] = Field(default_factory=list)
    scale_headers: list[str] = Field(default_factory=list)
    rungs: list[PlcRung] = Field(default_factory=list)


class CircuitSpec(BaseModel):
    meta: Meta
    sequence: list[SeqStep]
    power: Power
    cylinders: dict[str, Cylinder] = Field(default_factory=dict)
    motors: dict[str, Motor] = Field(default_factory=dict)
    valves: dict[str, Valve] = Field(default_factory=dict)
    sensors: list[str] = Field(default_factory=list)
    electrical: Electrical = Field(default_factory=Electrical)
    plc: PlcBlock | None = None

    @classmethod
    def from_yaml(cls, path: Path | str) -> CircuitSpec:
        data: dict[str, Any] = yaml.safe_load(Path(path).read_text()) or {}
        return cls.model_validate(data)

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False)

    def output_slug(self, spec_path: Path | str | None = None) -> str:
        """Folder name under output/ — exam_id, else YAML parent, else title."""
        raw = (self.meta.exam_id or "").strip()
        if not raw and spec_path is not None:
            parent = Path(spec_path).resolve().parent.name
            if parent and parent.lower() not in _GENERIC_PARENTS:
                raw = parent
        if not raw:
            raw = self.meta.title or "untitled"
        slug = _SLUG_RE.sub("_", raw).strip("._-")
        return slug or "untitled"


def question_output_dir(
    root: Path,
    spec: CircuitSpec,
    spec_path: Path | str | None = None,
) -> Path:
    """Per-question drawings: output/<exam_id>/."""
    return Path(root) / "output" / spec.output_slug(spec_path)
