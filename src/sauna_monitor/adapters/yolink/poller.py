"""
YoLink Temperature Monitoring Service

This service connects to YoLink API, fetches temperature sensor data,
and keeps the latest readings in memory for the web server.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

import aiohttp

from yolink.auth_mgr import YoLinkAuthMgr
from yolink.client import YoLinkClient
from yolink.const import OAUTH2_TOKEN
from yolink.device import YoLinkDevice, YoLinkDeviceMode
from yolink.endpoint import Endpoints

import config
from sauna_monitor.infra.storage.json import temp_logger, breaker_tracker

try:
    from sauna_monitor.adapters.telegram.notifier import notifier
    TELEGRAM_IMPORTED = True
except ImportError:
    TELEGRAM_IMPORTED = False
    notifier = None


class SimpleAuthManager(YoLinkAuthMgr):
    """OAuth2 authentication manager for YoLink API."""

    def __init__(self, session: aiohttp.ClientSession, uaid: str, secret_key: str) -> None:
        super().__init__(session)
        self._uaid = uaid
        self._secret_key = secret_key
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

    def access_token(self) -> str:
        return self._access_token or ""

    async def check_and_refresh_token(self) -> str:
        if (
            self._access_token is None
            or self._token_expires_at is None
            or datetime.now(timezone.utc) >= self._token_expires_at - timedelta(minutes=5)
        ):
            await self._fetch_token()
        return self._access_token

    async def _fetch_token(self) -> None:
        async with self._session.post(
            OAUTH2_TOKEN,
            data={
                "grant_type": "client_credentials",
                "client_id": self._uaid,
                "client_secret": self._secret_key,
            },
        ) as response:
            response.raise_for_status()
            data = await response.json()
            self._access_token = data["access_token"]
            expires_in = data.get("expires_in", 7200)
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)


class TemperatureMonitor:
    """Monitors YoLink temperature sensors and stores latest readings."""

    def __init__(self):
        self.latest_data = {
            "temperature": None,
            "humidity": None,
            "device_name": None,
            "device_id": None,
            "last_update": None,
            "status": "initializing",
            "error": None,
            "temp_unit": "°F" if config.DISPLAY_FAHRENHEIT else "°C",
        }
        self.session: Optional[aiohttp.ClientSession] = None
        self.client: Optional[YoLinkClient] = None
        self.temperature_device: Optional[YoLinkDevice] = None

    async def initialize(self):
        """Initialize connection to YoLink API and find temperature sensor."""
        try:
            print("Initializing YoLink Temperature Monitor...")
            self.session = aiohttp.ClientSession()
            auth_mgr = SimpleAuthManager(self.session, config.YOLINK_UAID, config.YOLINK_SECRET_KEY)
            self.client = YoLinkClient(auth_mgr)

            # Authenticate
            await auth_mgr.check_and_refresh_token()
            print("✓ Successfully authenticated with YoLink API")

            # Fetch device list
            response = await self.client.execute(
                url=Endpoints.US.value.url, bsdp={"method": "Home.getDeviceList"}
            )
            devices = response.data.get("devices", [])

            if not devices:
                raise Exception("No devices found in your YoLink account")

            # Find temperature sensor (look for THSensor or similar)
            temp_devices = [
                d
                for d in devices
                if "temperature" in d.get("type", "").lower()
                or "thsensor" in d.get("type", "").lower()
            ]

            if not temp_devices:
                # If no specific temperature device, list all devices
                print("\nAvailable devices:")
                for dev in devices:
                    print(f"  - {dev.get('name')} ({dev.get('type')})")
                raise Exception(
                    "No temperature sensor found. Please check device list above."
                )

            # Use the first temperature sensor found
            device_data = temp_devices[0]
            device_mode = YoLinkDeviceMode(**device_data)
            self.temperature_device = YoLinkDevice(device_mode, self.client)

            self.latest_data["device_name"] = self.temperature_device.device_name
            self.latest_data["device_id"] = self.temperature_device.device_id
            self.latest_data["status"] = "connected"

            print(f"✓ Found temperature sensor: {self.temperature_device.device_name}")
            print(f"  Type: {self.temperature_device.device_type}")
            print(f"  Model: {self.temperature_device.device_model_name}")

        except Exception as e:
            self.latest_data["status"] = "error"
            self.latest_data["error"] = str(e)
            print(f"Error during initialization: {e}")
            raise

    async def update_temperature(self):
        """Fetch latest temperature reading from the sensor."""
        if not self.temperature_device:
            return

        try:
            # Get device state
            state_response = await self.temperature_device.get_state()
            state_data = state_response.data

            # Extract temperature and humidity
            # The structure varies by device, common fields:
            # - state.temperature
            # - state.humidity
            # - temperature
            # - humidity
            state_obj = state_data.get("state", {})

            temperature = state_obj.get("temperature") or state_data.get("temperature")
            humidity = state_obj.get("humidity") or state_data.get("humidity")

            self.latest_data["temperature"] = temperature
            self.latest_data["humidity"] = humidity
            self.latest_data["last_update"] = datetime.now(timezone.utc).isoformat()
            self.latest_data["status"] = "ok"
            self.latest_data["error"] = None

            # Log temperature reading (1-minute granularity handled by logger)
            if temperature is not None:
                temp_logger.add_reading(temperature, humidity)

                # Check if sauna reached ready temperature (only if heater is ON)
                if TELEGRAM_IMPORTED and notifier and hasattr(config, 'TELEGRAM_READY_TEMP'):
                    # Only notify if heater is ON (we're actively heating)
                    if breaker_tracker.current_state and temperature >= config.TELEGRAM_READY_TEMP:
                        notifier.notify_sauna_ready(temperature)

            temp_unit = "°F" if config.DISPLAY_FAHRENHEIT else "°C"
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] Temperature: {temperature}{temp_unit}"
                + (f", Humidity: {humidity}%" if humidity else "")
            )

        except Exception as e:
            self.latest_data["status"] = "error"
            self.latest_data["error"] = str(e)
            print(f"Error fetching temperature: {e}")

    async def run_monitor_loop(self):
        """Continuously monitor temperature at specified interval."""
        await self.initialize()

        # Initial reading
        await self.update_temperature()

        # Continuous monitoring loop
        while True:
            await asyncio.sleep(config.REFRESH_INTERVAL)
            await self.update_temperature()

    async def cleanup(self):
        """Close connections and cleanup resources."""
        if self.session:
            await self.session.close()

    def get_latest_data(self) -> dict:
        """Return the latest temperature data."""
        return self.latest_data.copy()


# Global monitor instance
monitor = TemperatureMonitor()


async def start_monitoring():
    """Start the temperature monitoring service."""
    try:
        await monitor.run_monitor_loop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await monitor.cleanup()


if __name__ == "__main__":
    asyncio.run(start_monitoring())
