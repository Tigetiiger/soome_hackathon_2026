"""Paths and configuration loading for the virtual-scale simulation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "sensor_sim.yaml"
DEFAULT_PACK = (
    Path.home()
    / "input-files/Europress_SinceAI2026_FINAL"
    / "Europress_SMART_Material_Value_Engine_v1.0.1_PARTICIPANTS (3)"
    / "Europress_SMART_Material_Value_Engine_v1.0.1/data/competition/public"
)
DEFAULT_OUT = PROJECT_ROOT / "data"

REQUIRED_SECTIONS = ("materials", "press", "hydraulics", "sensors", "scales", "climate", "tiers")


@dataclass(frozen=True)
class Paths:
    pack: Path
    out: Path

    def validate(self) -> None:
        needed = [
            self.pack / "reference" / "devices.parquet",
            self.pack / "reference" / "sites.parquet",
            self.pack / "operations" / "collection_events.parquet",
        ]
        missing = [str(p) for p in needed if not p.exists()]
        if missing:
            raise FileNotFoundError(f"Europress data pack incomplete, missing: {missing}")


def load_config(path: Path | str = DEFAULT_CONFIG) -> dict:
    with open(path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    absent = [s for s in REQUIRED_SECTIONS if s not in cfg]
    if absent:
        raise ValueError(f"config {path} is missing sections: {absent}")
    return cfg
