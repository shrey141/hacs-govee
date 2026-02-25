# Govee Integration for Home Assistant

A custom HACS integration to control and monitor Govee smart lights via the Govee cloud API.

## Features

- Control on/off, brightness, color (HS), and color temperature (Kelvin)
- Polls device state from the Govee cloud API
- Assumes state immediately after commands (optional, reduces visible lag)
- Diagnostic sensor exposing daily API rate limit usage
- Persists learned device settings across restarts (`govee_learning.yaml`)

## Installation

1. Install [HACS](https://hacs.xyz/) if you haven't already.
2. In HACS → Integrations, add this repository as a custom repository:
   `https://github.com/shrey141/hacs-govee`
3. Search for **Govee** and click **Download**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & Services → Add Integration** and search for **Govee**.
6. Enter your API key (see below) and a poll interval.

### Getting your API key

Open the **Govee Home** app → Account (bottom right) → Settings (top right) → **About Us** → **Apply for API Key**. The key will be emailed to your account address.

## Configuration

| Field | Description | Default |
| --- | --- | --- |
| API Key | Your Govee API key | — |
| Poll Interval | How often (seconds) to fetch device state | 120 |

## Options

After setup, click **Configure** on the integration card to access:

| Option | Description | Default |
| --- | --- | --- |
| API Key | Update your API key (requires restart) | — |
| Poll Interval | Seconds between state polls (requires restart) | 120 |
| Use assumed state | Show two buttons (on/off) while waiting for API confirmation | True |
| Offline is off | Show offline devices as off instead of keeping last known state | False |
| Disable attribute updates | Advanced: suppress specific state fields from API or history | — |

## Rate Limit

The Govee API allows **10,000 requests per account per day**. Each poll cycle makes one request per device.

| Devices | Safe minimum interval |
| --- | --- |
| 1 | 9 s |
| 5 | 44 s |
| 10 | 87 s |
| 13 | 113 s |

The integration warns in the log if your poll interval is too aggressive for your device count. The default of **120 seconds** is safe for up to ~13 devices.

A **diagnostic sensor** (`Govee API Rate Limit`) is available (disabled by default) that shows your remaining daily requests and reset time.

## Pulling vs. assuming state

Some devices don't support state polling. For those, state is assumed from your last command. For devices that do support polling, state is still assumed immediately after a command (configurable) and then updated from the API on the next poll.

## Disabling state updates for specific attributes

This is an advanced workaround for cases where the Govee API returns incorrect data for a specific field. You can suppress updates for that field without losing all state tracking.

Format: `SOURCE:attribute` — multiple entries separated by `;`

**Examples:**

```text
API:power_state
API:online;HISTORY:online
```

Sources are `API` and `HISTORY`. Attribute names match fields in the [GoveeDevice data class](https://github.com/shrey141/python-govee-api/blob/master/govee_api/govee_dtos.py).

A warning is logged on every poll while any attribute updates are disabled, to remind you this is a temporary workaround.

## govee_learning.yaml

The integration stores per-device learned settings in `<config_dir>/govee_learning.yaml`. You normally don't need to edit this, but you can override values:

```yaml
AA:BB:CC:DD:EE:FF:
  set_brightness_max: 100
  get_brightness_max: 100
  before_set_brightness_turn_on: false
  config_offline_is_off: false
```

- `set_brightness_max` / `get_brightness_max`: auto-learned (0–100 or 0–254 range)
- `before_set_brightness_turn_on`: if `true`, turns on the device before setting brightness (needed for some models)
- `config_offline_is_off`: if `true`, marks the device as off when it goes offline (useful for USB-powered lights tied to a TV)

## Debug logging

Add to your `configuration.yaml` and restart:

```yaml
logger:
  default: warning
  logs:
    custom_components.govee: debug
    govee_api: debug
```

Then go to **Settings → System → Logs** and click **Load Full Logs**.

## Issues

Report bugs at [github.com/shrey141/hacs-govee/issues](https://github.com/shrey141/hacs-govee/issues)

## License

MIT — see [LICENSE.txt](LICENSE.txt)
