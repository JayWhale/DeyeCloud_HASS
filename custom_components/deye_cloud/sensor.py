"""Sensor platform for Deye Cloud integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COORDINATOR, DOMAIN

_LOGGER = logging.getLogger(__name__)

# ---------------------------
# Sensor entity descriptions
# ---------------------------

STATION_SENSOR_DESCRIPTIONS: list[SensorEntityDescription] = [
    SensorEntityDescription(
        key="todayEnergy",
        name="Today Energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
    ),
    SensorEntityDescription(
        key="totalEnergy",
        name="Total Energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:solar-power",
    ),
    SensorEntityDescription(
        key="currentPower",
        name="Current Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    SensorEntityDescription(
        key="gridPower",
        name="Grid Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="buyPower",
        name="Buy Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-import",
    ),
    SensorEntityDescription(
        key="sellPower",
        name="Sell Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
    ),
]

DEVICE_SENSOR_DESCRIPTIONS: list[SensorEntityDescription] = [
    # Inverter / AC
    SensorEntityDescription(
        key="pac",
        name="AC Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    SensorEntityDescription(
        key="dailyEnergy",
        name="Daily Energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
    ),
    SensorEntityDescription(
        key="totalEnergy",
        name="Total Energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:solar-power",
    ),
    # Battery
    SensorEntityDescription(
        key="batteryPower",
        name="Battery Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
    ),
    SensorEntityDescription(
        key="batterySoc",
        name="Battery SOC",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
    ),
    SensorEntityDescription(
        key="batteryVoltage",
        name="Battery Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
    ),
    SensorEntityDescription(
        key="batteryCurrent",
        name="Battery Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
    ),
    SensorEntityDescription(
        key="batteryTemperature",
        name="Battery Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    # Grid
    SensorEntityDescription(
        key="gridVoltage",
        name="Grid Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    SensorEntityDescription(
        key="gridCurrent",
        name="Grid Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
    ),
    SensorEntityDescription(
        key="gridFrequency",
        name="Grid Frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    SensorEntityDescription(
        key="gridPower",
        name="Grid Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
    ),
    # Load
    SensorEntityDescription(
        key="loadPower",
        name="Load Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
    ),
    SensorEntityDescription(
        key="loadVoltage",
        name="Load Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
    ),
    SensorEntityDescription(
        key="loadCurrent",
        name="Load Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
    ),
    # PV
    SensorEntityDescription(
        key="pv1Power",
        name="PV1 Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="pv1Voltage",
        name="PV1 Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="pv1Current",
        name="PV1 Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="pv2Power",
        name="PV2 Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="pv2Voltage",
        name="PV2 Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="pv2Current",
        name="PV2 Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    # Inverter
    SensorEntityDescription(
        key="inverterTemperature",
        name="Inverter Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Deye Cloud sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    entities: list[SensorEntity] = []

    # Station sensors (always 6 if keys present)
    for station_id in getattr(coordinator, "stations", []):
        for desc in STATION_SENSOR_DESCRIPTIONS:
            entities.append(
                DeyeCloudStationSensor(
                    coordinator=coordinator,
                    station_id=station_id,
                    description=desc,
                )
            )

    # Device sensors (this is where the 'WAY more' come from)
    for device_sn in getattr(coordinator, "devices", []):
        for desc in DEVICE_SENSOR_DESCRIPTIONS:
            entities.append(
                DeyeCloudDeviceSensor(
                    coordinator=coordinator,
                    device_sn=device_sn,
                    description=desc,
                )
            )

    if not entities:
        _LOGGER.warning(
            "No Deye Cloud sensors were created. Check that the coordinator populated stations/devices."
        )

    async_add_entities(entities)


# ---------------------------
# Base classes
# ---------------------------

class DeyeBaseSensor(CoordinatorEntity, SensorEntity):
    """Common helpers for Deye sensors."""

    _attr_has_entity_name = True  # Let HA use device name + entity name pattern

    @staticmethod
    def _coerce_number(value: Any) -> float | int | None:
        """Convert various types to a number (float preferred), safely."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        try:
            # Some APIs return numeric strings
            f = float(value)
            # If it's an integer float, HA often prefers int
            return int(f) if f.is_integer() else f
        except (ValueError, TypeError):
            return None


class DeyeCloudStationSensor(DeyeBaseSensor):
    """Representation of a Deye Cloud station-level sensor."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator,
        station_id: str,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._station_id = station_id

        # Clean entity name; device card shows station name
        self._attr_name = description.name
        self._attr_unique_id = f"{station_id}_{description.key}"

    def _station_info(self) -> dict[str, Any]:
        return self.coordinator.data.get("stations", {}).get(self._station_id, {}).get("info", {})

    def _station_data(self) -> dict[str, Any]:
        return self.coordinator.data.get("stations", {}).get(self._station_id, {}).get("data", {})

    @property
    def native_value(self) -> float | int | None:
        value = self._station_data().get(self.entity_description.key)
        return self._coerce_number(value)

    @property
    def device_info(self) -> dict[str, Any]:
        info = self._station_info()
        return {
            "identifiers": {(DOMAIN, f"station-{self._station_id}")},
            "name": info.get("name") or f"Station {self._station_id}",
            "manufacturer": "Deye",
            "model": "Solar Station",
        }

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self._station_id in self.coordinator.data.get("stations", {})
        )


class DeyeCloudDeviceSensor(DeyeBaseSensor):
    """Representation of a Deye Cloud device-level sensor."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator,
        device_sn: str,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._device_sn = device_sn

        self._attr_name = description.name
        self._attr_unique_id = f"{device_sn}_{description.key}"

    def _device_info_obj(self) -> dict[str, Any]:
        return self.coordinator.data.get("devices", {}).get(self._device_sn, {}).get("info", {})

    def _device_data_obj(self) -> dict[str, Any]:
        return self.coordinator.data.get("devices", {}).get(self._device_sn, {}).get("data", {})

    @property
    def native_value(self) -> float | int | None:
        value = self._device_data_obj().get(self.entity_description.key)
        return self._coerce_number(value)

    @property
    def device_info(self) -> dict[str, Any]:
        info = self._device_info_obj()
        return {
            "identifiers": {(DOMAIN, self._device_sn)},
            "name": info.get("deviceName") or f"Device {self._device_sn}",
            "manufacturer": "Deye",
            "model": info.get("deviceModel", "Inverter"),
            "sw_version": info.get("firmwareVersion"),
            "serial_number": self._device_sn,
        }

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self._device_sn in self.coordinator.data.get("devices", {})
        )
