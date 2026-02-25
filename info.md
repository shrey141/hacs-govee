[![hacs][hacsbadge]][hacs]

_Control your Govee smart lights from Home Assistant._

**Platforms set up by this integration:**

| Platform | Description |
| -- | -- |
| `light` | Control brightness, color, and color temperature |
| `sensor` | Diagnostic: API rate limit remaining (disabled by default) |

{% if not installed %}

## Installation

1. In HACS → Integrations, add `https://github.com/shrey141/hacs-govee` as a custom repository.
2. Search for **Govee** and click **Download**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and search for **Govee**.

{% endif %}

## Configuration

Enter your Govee API key and a poll interval. Configuration is done entirely in the UI.

- [Full documentation](https://github.com/shrey141/hacs-govee/blob/master/README.md)
- [Report an issue](https://github.com/shrey141/hacs-govee/issues)

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
