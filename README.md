# Govee Thermometer / Hygrometer — Home Assistant Integration

[![Home Assistant Marketplace](https://img.shields.io/badge/HA%20Marketplace-custom%20repository-41BDF5.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Conexo-Casa&repository=govee-thermometer-ha&category=integration)
[![HA Version][ha-badge]][ha-url]

A custom integration that pulls **temperature**, **humidity**, and **online status** from Govee WiFi thermometers and hygrometers using the Govee OpenAPI.

## Supported Devices

| SKU    | Device                              | Temperature | Humidity |
|--------|-------------------------------------|:-----------:|:--------:|
| H5103  | GoveeLife WiFi Thermometer H5103    | ✅          | ✅       |
| H5179  | WiFi Thermo-Hygrometer H5179        | ✅          | ✅       |
| H5100  | Thermo-Hygrometer H5100             | ✅          | ✅       |
| H5101  | Thermo-Hygrometer H5101             | ✅          | ✅       |
| H5102  | Thermo-Hygrometer H5102             | ✅          | ✅       |
| H5104  | Thermo-Hygrometer H5104             | ✅          | ✅       |
| H5055  | **GoveeLife WiFi Pool Thermometer P1** | ✅       | —        |
| H5056  | Pool Thermometer H5056              | ✅          | —        |

> Don't see your device? Open an issue — adding a SKU is a one-line change.

## Prerequisites

1. **Govee Developer API key** — request one from the Govee Home app:  
   Settings → About Us → Apply for API Key  
   (or visit [developer.govee.com](https://developer.govee.com/docs/getting-started))
2. Home Assistant **2024.1** or newer
3. For installing: the built-in Marketplace (HA 2026.11+) or HACS (older versions)

## Installation

### Marketplace (Home Assistant 2026.11 and newer)

[![Open your Home Assistant instance and show this repository in the Marketplace.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Conexo-Casa&repository=govee-thermometer-ha&category=integration)

Or by hand:

1. Go to **Settings → Marketplace**.
2. Select **Add from link** (top right) and enter `Conexo-Casa/govee-thermometer-ha`.
   The first time, Home Assistant asks you to connect GitHub. That is a one-time,
   read-only sign-in on github.com.
3. Open **Govee Thermometer / Hygrometer** and select **Install**. The setup screen opens right away; a first
   install doesn't need a restart.

Updates show up under **Settings → Updates**. After an update, Home Assistant shows a
repair that offers to restart.

### HACS (Home Assistant 2026.10 and older)

1. HACS → **Integrations** → **⋮** → **Custom repositories**.
2. Add `https://github.com/Conexo-Casa/govee-thermometer-ha`, category **Integration**.
3. Download **Govee Thermometer / Hygrometer**, then restart Home Assistant.

An existing HACS install moves to the Marketplace by itself when you upgrade to 2026.11.

### Manual

Copy `custom_components/govee_thermometer/` into your HA `config/custom_components/` directory and restart.

## Configuration

1. Settings → Devices & Services → **Add Integration**
2. Search for **Govee Thermometer**
3. Enter your API key

All matching sensor devices on your account are discovered automatically.

## Entities Created

For each detected device:

| Entity | Device Class | Enabled by default |
|--------|-------------|-------------------|
| `sensor.<name>_temperature` | `temperature` | ✅ |
| `sensor.<name>_humidity` | `humidity` | ✅ (if supported) |
| `sensor.<name>_connection` | — | ❌ (opt-in) |

## Polling

The integration polls Govee's cloud API once per minute. This is within Govee's published rate limits.

## Notes

- The **Pool Thermometer P1** is cloud-only (no LAN API); this integration is the only way to get its readings into HA without MQTT bridging.
- Temperature values are always stored in **°C** internally; HA converts to your preferred unit automatically.

---

[ha-badge]: https://img.shields.io/badge/HA-2024.1%2B-blue.svg
[ha-url]: https://www.home-assistant.io

## License

MIT — see [LICENSE](LICENSE).
