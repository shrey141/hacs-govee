"""Constants for the Govee LED strips integration."""

DOMAIN = "govee"

CONF_DISABLE_ATTRIBUTE_UPDATES = "disable_attribute_updates"
CONF_OFFLINE_IS_OFF = "offline_is_off"
CONF_USE_ASSUMED_STATE = "use_assumed_state"

COLOR_TEMP_KELVIN_MIN = 2000
COLOR_TEMP_KELVIN_MAX = 9000

DEFAULT_POLL_INTERVAL = 120  # seconds — safe default for up to ~13 devices at 10k/day limit
RATE_LIMIT_DAILY = 10000  # Govee API daily rate limit
