"""The Govee learned storage yaml file manager."""

from dataclasses import asdict
import logging

import dacite
from .govee_api import GoveeAbstractLearningStorage, GoveeDailyStats, GoveeLearnedInfo
import yaml

from homeassistant.util.yaml import load_yaml, save_yaml

_LOGGER = logging.getLogger(__name__)
LEARNING_STORAGE_YAML = "/govee_learning.yaml"
_DAILY_STATS_KEY = "_daily_stats"


class GoveeLearningStorage(GoveeAbstractLearningStorage):
    """The govee_api library uses this to store learned information about lights."""

    def __init__(self, hass, config_dir, *args, **kwargs):
        """Get the config directory."""
        super().__init__(*args, **kwargs)
        self._hass = hass
        self._config_dir = config_dir

    async def _load_yaml(self) -> dict:
        """Load the YAML file, returning an empty dict if missing."""
        try:
            return await self._hass.async_add_executor_job(
                load_yaml, self._config_dir + LEARNING_STORAGE_YAML
            ) or {}
        except FileNotFoundError:
            return {}

    async def read(self):
        """Restore device learning info from yaml file."""
        learned_info = {}
        try:
            learned_dict = await self._load_yaml()
            learned_info = {
                device: dacite.from_dict(
                    data_class=GoveeLearnedInfo, data=learned_dict[device]
                )
                for device in learned_dict
                if not device.startswith("_")  # skip metadata keys like _daily_stats
            }
            _LOGGER.info(
                "Loaded learning information from %s.",
                self._config_dir + LEARNING_STORAGE_YAML,
            )
        except FileNotFoundError:
            _LOGGER.warning(
                "There is no %s file containing learned information about your devices. "
                + "This is normal for first start of Govee integration.",
                self._config_dir + LEARNING_STORAGE_YAML,
            )
        except (
            dacite.DaciteError,
            TypeError,
            UnicodeDecodeError,
            yaml.YAMLError,
        ) as ex:
            _LOGGER.warning(
                "The %s file containing learned information about your devices is invalid: %s. "
                + "Learning starts from scratch.",
                self._config_dir + LEARNING_STORAGE_YAML,
                ex,
            )
        return learned_info

    async def write(self, learned_info):
        """Save device learning info to yaml file, preserving metadata keys."""
        existing = await self._load_yaml()
        # Preserve metadata keys (e.g. _daily_stats), replace device entries
        new_data = {k: v for k, v in existing.items() if k.startswith("_")}
        new_data.update({device: asdict(learned_info[device]) for device in learned_info})
        await self._hass.async_add_executor_job(
            save_yaml, self._config_dir + LEARNING_STORAGE_YAML, new_data
        )
        _LOGGER.info(
            "Stored learning information to %s.",
            self._config_dir + LEARNING_STORAGE_YAML,
        )

    async def read_daily_stats(self) -> GoveeDailyStats:
        """Read daily request stats from yaml file."""
        try:
            data = await self._load_yaml()
            if _DAILY_STATS_KEY in data:
                return dacite.from_dict(
                    data_class=GoveeDailyStats, data=data[_DAILY_STATS_KEY]
                )
        except (dacite.DaciteError, TypeError, yaml.YAMLError) as ex:
            _LOGGER.warning("Could not read daily stats: %s", ex)
        return GoveeDailyStats()

    async def write_daily_stats(self, stats: GoveeDailyStats):
        """Write daily request stats to yaml file."""
        existing = await self._load_yaml()
        existing[_DAILY_STATS_KEY] = asdict(stats)
        await self._hass.async_add_executor_job(
            save_yaml, self._config_dir + LEARNING_STORAGE_YAML, existing
        )
