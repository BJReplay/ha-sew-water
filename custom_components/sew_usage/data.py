"""Data Class.

Data Class for Config Entry.

"""

from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.loader import Integration

from .coordinator import SEWDataUpdateCoordinator

type SEWConfigEntry = ConfigEntry[SEWData]


@dataclass
class SEWData:
    """SEW options for the integration."""

    coordinator: SEWDataUpdateCoordinator
    integration: Integration
    other_data: dict[str, Any] | None
