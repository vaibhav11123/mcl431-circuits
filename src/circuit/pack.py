"""Resolve which symbol pack the engine uses."""

from __future__ import annotations

import importlib
import os
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

_CHECKOUT = Path(__file__).resolve().parents[2]
_ISO_ROOT = Path(__file__).resolve().parent / "packs" / "iso_sequence"
_LECTURE_STAMPS = _CHECKOUT / "lecture" / "crops" / "stamps"

_stamp_dir: ContextVar[Path | None] = ContextVar("circuit_stamp_dir", default=None)
_active_pack: ContextVar["Pack | None"] = ContextVar("circuit_pack", default=None)


@dataclass(frozen=True)
class Pack:
    root: Path
    atlas_path: Path
    stamp_dir: Path
    hooks_module: str | None = None


def _from_root(root: Path, hooks_module: str | None = None) -> Pack:
    root = root.resolve()
    lecture = root / "lecture" / "atlas.yaml"
    if lecture.is_file():
        return Pack(
            root=root,
            atlas_path=lecture,
            stamp_dir=root / "lecture" / "crops" / "stamps",
            hooks_module=hooks_module or "circuit.packs.mcl431",
        )
    if hooks_module is None and (root / "stamps" / "dcv_5_2.png").is_file():
        hooks_module = "circuit.packs.iso_sequence"
    return Pack(
        root=root,
        atlas_path=root / "atlas.yaml",
        stamp_dir=root / "stamps",
        hooks_module=hooks_module,
    )


def pack_from_root(root: Path) -> Pack:
    """Pack for an explicit root. Ignores leftover CIRCUIT_PACK."""
    root = Path(root).resolve()
    lecture = root / "lecture" / "atlas.yaml"
    direct = root / "atlas.yaml"
    if lecture.is_file() or direct.is_file():
        return _from_root(root)
    return resolve_pack()


def resolve_pack(explicit: str | Path | None = None) -> Pack:
    """`--pack PATH` or `CIRCUIT_PACK`, else this checkout, else the ISO wheel pack."""
    if explicit is not None:
        return _from_root(Path(explicit))
    env = os.environ.get("CIRCUIT_PACK")
    if env:
        return _from_root(Path(env))
    if (_CHECKOUT / "lecture" / "atlas.yaml").is_file():
        return _from_root(_CHECKOUT, "circuit.packs.mcl431")
    return Pack(
        root=_ISO_ROOT,
        atlas_path=_ISO_ROOT / "atlas.yaml",
        stamp_dir=_ISO_ROOT / "stamps",
        hooks_module="circuit.packs.iso_sequence",
    )


def engine_pack() -> Pack:
    """Active `using_pack`, else lecture checkout, else resolve_pack.

    Goldens must not pick up a leftover CIRCUIT_PACK when no context is set.
    """
    current = _active_pack.get()
    if current is not None:
        return current
    if (_CHECKOUT / "lecture" / "atlas.yaml").is_file():
        return _from_root(_CHECKOUT, "circuit.packs.mcl431")
    return resolve_pack()


@contextmanager
def using_pack(pack: Pack) -> Iterator[Pack]:
    t_dir = _stamp_dir.set(pack.stamp_dir)
    t_pack = _active_pack.set(pack)
    try:
        yield pack
    finally:
        _active_pack.reset(t_pack)
        _stamp_dir.reset(t_dir)


def active_stamp_dir() -> Path:
    return _stamp_dir.get() or _LECTURE_STAMPS


def current_pack() -> Pack | None:
    return _active_pack.get()


def load_hooks(pack: Pack | None = None) -> Any | None:
    pack = pack or engine_pack()
    if pack is None or not pack.hooks_module:
        return None
    return importlib.import_module(pack.hooks_module)


def call_hook(name: str, *args: Any, default: Any = None, **kwargs: Any) -> Any:
    hooks = load_hooks()
    fn = getattr(hooks, name, None) if hooks else None
    if fn is None:
        return default
    return fn(*args, **kwargs)
