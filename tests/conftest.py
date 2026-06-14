"""Pytest configuration — stub out homeassistant for unit tests."""
import sys
from unittest.mock import MagicMock

# Stub the entire homeassistant package tree so tests run without HA installed
for mod in [
    "homeassistant",
    "homeassistant.core",
    "homeassistant.config_entries",
    "homeassistant.const",
    "homeassistant.exceptions",
    "homeassistant.helpers",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.helpers.entity",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.components",
    "homeassistant.components.sensor",
]:
    sys.modules[mod] = MagicMock()
