"""Constants for the Govee Thermometer integration."""

DOMAIN = "govee_thermometer"

# ── Govee OpenAPI v1 ───────────────────────────────────────────────────────
GOVEE_API_BASE       = "https://openapi.api.govee.com/router/api/v1"
GOVEE_API_DEVICES    = f"{GOVEE_API_BASE}/user/devices"
GOVEE_API_STATE      = f"{GOVEE_API_BASE}/device/state"

# Capability instance names returned by the state endpoint
CAP_TEMPERATURE = "sensorTemperature"
CAP_HUMIDITY    = "sensorHumidity"
CAP_ONLINE      = "online"

# Known thermometer / hygrometer SKUs.
# has_humidity=False  → pool/water thermometers that report temperature only.
# The P1 pool thermometer hasn't been assigned a confirmed SKU in the public
# API yet; H5055 is the most commonly cited candidate — add others as needed.
GOVEE_SENSOR_SKUS: dict[str, dict] = {
    # ── patio / indoor ──────────────────────────────────────────────────
    "H5103": {"label": "WiFi Thermometer Hygrometer H5103", "has_humidity": True},
    "H5179": {"label": "WiFi Thermo-Hygrometer H5179",      "has_humidity": True},
    "H5100": {"label": "Thermo-Hygrometer H5100",           "has_humidity": True},
    "H5101": {"label": "Thermo-Hygrometer H5101",           "has_humidity": True},
    "H5102": {"label": "Thermo-Hygrometer H5102",           "has_humidity": True},
    "H5104": {"label": "Thermo-Hygrometer H5104",           "has_humidity": True},
    # ── pool / water ────────────────────────────────────────────────────
    "H5055": {"label": "GoveeLife WiFi Pool Thermometer P1","has_humidity": False},
    "H5056": {"label": "Pool Thermometer H5056",             "has_humidity": False},
}

# Govee can return temperature/humidity multiplied by 100 (e.g. 2560 = 25.60°C)
# Values above this threshold are divided by 100 before use.
SCALE_THRESHOLD = 1000
SCALE_DIVISOR   = 100

# Config-entry / options keys
CONF_API_KEY   = "api_key"
CONF_TEMP_UNIT = "temp_unit"

# Temperature unit options
TEMP_UNIT_CELSIUS    = "celsius"
TEMP_UNIT_FAHRENHEIT = "fahrenheit"

# Polling
SCAN_INTERVAL_SECONDS = 60   # safe for Govee's cloud rate limit
