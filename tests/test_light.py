"""Tests for the Govee light platform."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from custom_components.govee.light import GoveeLightEntity, GoveeDataUpdateCoordinator
from custom_components.govee.const import COLOR_TEMP_KELVIN_MIN, COLOR_TEMP_KELVIN_MAX


def _make_mock_device(
    device="AA:BB:CC:DD:EE:FF",
    model="H6159",
    device_name="Test Light",
    support_color=True,
    support_color_tem=True,
    support_brightness=True,
    power_state=True,
    brightness=128,
    color=(255, 0, 0),
    color_temp=4000,
    online=True,
    source=None,
    error=None,
    retrievable=True,
):
    """Create a mock GoveeDevice."""
    device_mock = MagicMock()
    device_mock.device = device
    device_mock.model = model
    device_mock.device_name = device_name
    device_mock.support_color = support_color
    device_mock.support_color_tem = support_color_tem
    device_mock.support_brightness = support_brightness
    device_mock.support_turn = True
    device_mock.controllable = True
    device_mock.retrievable = retrievable
    device_mock.power_state = power_state
    device_mock.brightness = brightness
    device_mock.color = color
    device_mock.color_temp = color_temp
    device_mock.online = online
    device_mock.source = source
    device_mock.error = error
    return device_mock


def _make_mock_hub():
    """Create a mock Govee hub."""
    hub = AsyncMock()
    hub.rate_limit_total = 100
    hub.rate_limit_remaining = 95
    hub.rate_limit_reset_seconds = 60.0
    hub.rate_limit_reset = 1700000000.0
    hub.rate_limit_on = 5
    hub.online = True
    hub.devices = []
    return hub


def _make_entity(hub=None, device=None, coordinator=None):
    """Create a GoveeLightEntity with mocks."""
    if hub is None:
        hub = _make_mock_hub()
    if device is None:
        device = _make_mock_device()
    if coordinator is None:
        coordinator = MagicMock()
    return GoveeLightEntity(hub, "test", coordinator, device)


class TestColorTempKelvinRange:
    """Test that color temp kelvin min/max are correct (Bug 1)."""

    def test_min_less_than_max(self):
        entity = _make_entity()
        assert entity.min_color_temp_kelvin < entity.max_color_temp_kelvin

    def test_min_is_2000(self):
        entity = _make_entity()
        assert entity.min_color_temp_kelvin == COLOR_TEMP_KELVIN_MIN
        assert entity.min_color_temp_kelvin == 2000

    def test_max_is_9000(self):
        entity = _make_entity()
        assert entity.max_color_temp_kelvin == COLOR_TEMP_KELVIN_MAX
        assert entity.max_color_temp_kelvin == 9000


class TestTurnOffLogsError:
    """Test that async_turn_off logs errors (Bug 2)."""

    @pytest.mark.asyncio
    async def test_turn_off_success(self):
        hub = _make_mock_hub()
        hub.turn_off = AsyncMock(return_value=(True, None))
        entity = _make_entity(hub=hub)
        await entity.async_turn_off()
        hub.turn_off.assert_called_once()

    @pytest.mark.asyncio
    async def test_turn_off_logs_error(self):
        hub = _make_mock_hub()
        hub.turn_off = AsyncMock(return_value=(False, "device unreachable"))
        entity = _make_entity(hub=hub)
        with patch("custom_components.govee.light._LOGGER") as mock_logger:
            await entity.async_turn_off()
            mock_logger.warning.assert_called_once()
            assert "device unreachable" in str(mock_logger.warning.call_args)


class TestTurnOnAccumulatesErrors:
    """Test that async_turn_on reports all errors (Bug 3)."""

    @pytest.mark.asyncio
    async def test_turn_on_multiple_errors(self):
        hub = _make_mock_hub()
        hub.set_color = AsyncMock(return_value=(False, "color failed"))
        hub.set_brightness = AsyncMock(return_value=(False, "brightness failed"))
        entity = _make_entity(hub=hub)

        from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_HS_COLOR

        with patch("custom_components.govee.light._LOGGER") as mock_logger:
            await entity.async_turn_on(
                **{ATTR_HS_COLOR: (120, 100), ATTR_BRIGHTNESS: 200}
            )
            mock_logger.warning.assert_called_once()
            warning_msg = str(mock_logger.warning.call_args)
            assert "color failed" in warning_msg
            assert "brightness failed" in warning_msg

    @pytest.mark.asyncio
    async def test_turn_on_single_error(self):
        hub = _make_mock_hub()
        hub.set_color = AsyncMock(return_value=(False, "color failed"))
        hub.set_brightness = AsyncMock(return_value=(True, None))
        entity = _make_entity(hub=hub)

        from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_HS_COLOR

        with patch("custom_components.govee.light._LOGGER") as mock_logger:
            await entity.async_turn_on(
                **{ATTR_HS_COLOR: (120, 100), ATTR_BRIGHTNESS: 200}
            )
            mock_logger.warning.assert_called_once()
            warning_msg = str(mock_logger.warning.call_args)
            assert "color failed" in warning_msg
            assert "brightness" not in warning_msg

    @pytest.mark.asyncio
    async def test_turn_on_no_error(self):
        hub = _make_mock_hub()
        hub.turn_on = AsyncMock(return_value=(True, None))
        entity = _make_entity(hub=hub)

        with patch("custom_components.govee.light._LOGGER") as mock_logger:
            await entity.async_turn_on()
            mock_logger.warning.assert_not_called()


class TestListenerCleanup:
    """Test that listeners are properly cleaned up (Imp 13)."""

    @pytest.mark.asyncio
    async def test_listener_removed_on_hass_removal(self):
        coordinator = MagicMock()
        unsub = MagicMock()
        coordinator.async_add_listener = MagicMock(return_value=unsub)

        entity = _make_entity(coordinator=coordinator)
        await entity.async_added_to_hass()
        coordinator.async_add_listener.assert_called_once()

        await entity.async_will_remove_from_hass()
        unsub.assert_called_once()

    @pytest.mark.asyncio
    async def test_double_removal_safe(self):
        coordinator = MagicMock()
        unsub = MagicMock()
        coordinator.async_add_listener = MagicMock(return_value=unsub)

        entity = _make_entity(coordinator=coordinator)
        await entity.async_added_to_hass()
        await entity.async_will_remove_from_hass()
        await entity.async_will_remove_from_hass()
        # unsub should only be called once
        unsub.assert_called_once()


class TestColorNullSafety:
    """Test null safety for color properties (Bug 6)."""

    def test_hs_color_returns_none_when_no_color(self):
        device = _make_mock_device(color=None)
        entity = _make_entity(device=device)
        assert entity.hs_color is None

    def test_rgb_color_returns_none_when_no_color(self):
        device = _make_mock_device(color=None)
        entity = _make_entity(device=device)
        assert entity.rgb_color is None

    def test_hs_color_returns_value_when_color_set(self):
        device = _make_mock_device(color=(255, 0, 0))
        entity = _make_entity(device=device)
        result = entity.hs_color
        assert result is not None
        assert len(result) == 2

    def test_rgb_color_returns_value_when_color_set(self):
        device = _make_mock_device(color=(255, 0, 0))
        entity = _make_entity(device=device)
        result = entity.rgb_color
        assert result == [255, 0, 0]


class TestBrightnessMapping:
    """Test brightness mapping from Govee to HA range."""

    def test_brightness_zero(self):
        device = _make_mock_device(brightness=0)
        entity = _make_entity(device=device)
        assert entity.brightness == 1

    def test_brightness_max(self):
        device = _make_mock_device(brightness=254)
        entity = _make_entity(device=device)
        assert entity.brightness == 255

    def test_brightness_mid(self):
        device = _make_mock_device(brightness=127)
        entity = _make_entity(device=device)
        assert entity.brightness == 128


class TestExtraStateAttributes:
    """Test that rate limit info has been removed from extra_state_attributes (Imp 10)."""

    def test_no_rate_limit_attributes(self):
        entity = _make_entity()
        attrs = entity.extra_state_attributes
        assert "rate_limit_total" not in attrs
        assert "rate_limit_remaining" not in attrs
        assert "rate_limit_reset_seconds" not in attrs
        assert "rate_limit_reset" not in attrs
        assert "rate_limit_on" not in attrs

    def test_has_model_and_manufacturer(self):
        device = _make_mock_device(model="H6159")
        entity = _make_entity(device=device)
        attrs = entity.extra_state_attributes
        assert attrs["manufacturer"] == "Govee"
        assert attrs["model"] == "H6159"
