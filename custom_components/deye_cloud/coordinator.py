from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryNotReady

from .api import DeyeCloudClient, DeyeCloudApiError
from .const import COORDINATOR, DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

MAX_SN_PER_BATCH = 10


@dataclass
class DeyeStation:
    station_id: str
    name: str | None = None


@dataclass
class DeyeDevice:
    sn: str
    name: str | None = None
    model: str | None = None
    fw: str | None = None
    station_id: str | None = None


class DeyeCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Central coordinator for Deye Cloud integration."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: DeyeCloudClient,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=update_interval,
        )
        self.api = api

        # Public attrs used by sensor.py / switch.py to build entities
        self.stations: List[str] = []  # list of stationIds
        self.devices: List[str] = []   # list of device SNs

        # Data cache structure expected by your sensor.py:
        # self.data = {
        #   "stations": { station_id: { "info": {...}, "data": {...} } },
        #   "devices":  { sn: { "info": {...}, "data": {...} } }
        # }
        self.data: Dict[str, Any] = {"stations": {}, "devices": {}}

    async def async_config_entry_first_refresh(self) -> None:
        """Prepare discovery then perform first refresh."""
        try:
            await self._discover_topology()
        except Exception as exc:
            raise ConfigEntryNotReady(f"Failed to discover devices: {exc}") from exc
        await super().async_config_entry_first_refresh()

    async def _discover_topology(self) -> None:
        """Discover stations and devices, initialize data structures."""
        _LOGGER.debug("Discovering stations/devices via /station/listWithDevice")
        stations_payload = await self.api.get_station_list_with_devices()

        # The API shape varies across tenants; handle common shapes
        # Expecting: [{"stationId": "...", "stationName": "...", "deviceList":[{"deviceSn":"...", "deviceName": "...", "deviceModel":"...", "firmwareVersion":"..."}]}]
        self.stations = []
        self.devices = []
        self.data["stations"] = {}
        self.data["devices"] = {}

        for s in stations_payload or []:
            sid = s.get("stationId") or s.get("id") or s.get("station_id")
            if not sid:
                continue
            sname = s.get("stationName") or s.get("name")
            self.stations.append(sid)
            self.data["stations"][sid] = {"info": {"name": sname}, "data": {}}

            for d in (s.get("deviceList") or s.get("devices") or []):
                sn = d.get("deviceSn") or d.get("sn")
                if not sn:
                    continue
                dname = d.get("deviceName") or sn
                model = d.get("deviceModel")
                fw = d.get("firmwareVersion") or d.get("fwVersion") or d.get("version")
                if sn not in self.devices:
                    self.devices.append(sn)
                self.data["devices"][sn] = {
                    "info": {
                        "deviceName": dname,
                        "deviceModel": model,
                        "firmwareVersion": fw,
                        "stationId": sid,
                    },
                    "data": {},
                }

        _LOGGER.info(
            "Deye discovery finished: %d station(s), %d device(s)",
            len(self.stations),
            len(self.devices),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch and flatten latest station + device data."""
        # Update station latest
        await self._update_stations_latest()

        # Update device latest (batched)
        await self._update_devices_latest()

        # Return the cached structure for entities
        return self.data

    async def _update_stations_latest(self) -> None:
        """Refresh latest station-level metrics."""
        tasks = []
        for sid in self.stations:
            tasks.append(self._fetch_station_latest(sid))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _fetch_station_latest(self, station_id: str) -> None:
        try:
            latest = await self.api.get_station_latest_data(station_id)
            # Example shapes:
            # 1) {"todayEnergy": ..., "totalEnergy": ..., "currentPower": ..., ...}
            # 2) {"data": {...}} already handled in api._request to unwrap, so treat as flat
            if isinstance(latest, dict):
                self.data["stations"].setdefault(station_id, {"info": {}, "data": {}})
                # pick the keys you defined in STATION_SENSORS if present
                for key in (
                    "todayEnergy",
                    "totalEnergy",
                    "currentPower",
                    "gridPower",
                    "buyPower",
                    "sellPower",
                ):
                    if key in latest:
                        self.data["stations"][station_id]["data"][key] = latest[key]
        except DeyeCloudApiError as err:
            _LOGGER.warning("Failed to refresh station %s latest: %s", station_id, err)

    async def _update_devices_latest(self) -> None:
        """Refresh latest device metrics in batches of 10."""
        if not self.devices:
            return

        for i in range(0, len(self.devices), MAX_SN_PER_BATCH):
            batch = self.devices[i : i + MAX_SN_PER_BATCH]
            try:
                payload = await self.api.get_device_latest_data(batch)
            except DeyeCloudApiError as err:
                _LOGGER.warning("Device latest failed for batch %s: %s", batch, err)
                continue

            # Expected common shapes:
            # payload = {"deviceDataList": [
            #    {"deviceSn": "SN1", "dataList":[{"key": "batteryPower", "value": 123}, ...]},
            #    {"deviceSn": "SN2", "data": {"batteryPower": 123, "pv1Voltage": 350, ...}}
            # ]}
            if not isinstance(payload, dict):
                continue

            dev_list = payload.get("deviceDataList") or payload.get("list") or []
            for dev in dev_list:
                sn = dev.get("deviceSn") or dev.get("sn")
                if not sn or sn not in self.data["devices"]:
                    continue

                flat: Dict[str, Any] = {}

                # Case A: key/value pairs array
                for item in dev.get("dataList", []):
                    k = item.get("key")
                    v = item.get("value")
                    if k is not None:
                        flat[k] = v

                # Case B: direct dict of metrics
                if not flat and isinstance(dev.get("data"), dict):
                    for k, v in dev["data"].items():
                        flat[k] = v

                # Merge into cache
                if flat:
                    self.data["devices"][sn]["data"].update(flat)
