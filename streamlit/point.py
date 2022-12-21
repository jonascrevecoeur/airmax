from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Point:
    lat: float
    lon: float

    @classmethod
    def from_dict(cls, data: dict) -> Point:
        if "lat" in data:
            return cls(float(data["lat"]), float(data["lng"]))
        elif "latitude" in data:
            return cls(float(data["latitude"]), float(data["longitude"]))
        else:
            raise NotImplementedError(data.keys())

    def is_close_to(self, other: Point) -> bool:
        close_lat = self.lat - 0.0001 <= other.lat <= self.lat + 0.0001
        close_lon = self.lon - 0.0001 <= other.lon <= self.lon + 0.0001
        return close_lat and close_lon