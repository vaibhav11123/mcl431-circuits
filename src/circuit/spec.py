"""Pydantic circuit spec — YAML in, no coordinates."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class Domain(str, Enum):
    HYDRAULIC = "hydraulic"
    PNEUMATIC = "pneumatic"
    HYDRAULIC_PLUS_ELECTRICAL = "hydraulic_plus_electrical"
    PNEUMATIC_PLUS_ELECTRICAL = "pneumatic_plus_electrical"


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


class CircuitSpec(BaseModel):
    meta: Meta
    sequence: list[SeqStep]
    power: Power
    cylinders: dict[str, Cylinder] = Field(default_factory=dict)
    motors: dict[str, Motor] = Field(default_factory=dict)
    valves: dict[str, Valve] = Field(default_factory=dict)
    sensors: list[str] = Field(default_factory=list)
    electrical: Electrical = Field(default_factory=Electrical)

    @classmethod
    def from_yaml(cls, path: Path | str) -> CircuitSpec:
        data: dict[str, Any] = yaml.safe_load(Path(path).read_text()) or {}
        return cls.model_validate(data)

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False)
