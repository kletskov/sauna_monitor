"""
Tuya WiFi Breaker Monitoring Service

Monitors the status of a Tuya smart switch/breaker (e.g., sauna circuit).
"""

import threading
import time
from typing import Optional

try:
    import tinytuya
    TUYA_AVAILABLE = True
except ImportError:
    TUYA_AVAILABLE = False

import config
from data_logger import breaker_tracker


class TuyaBreakerMonitor:
    """Monitors Tuya WiFi breaker status."""

    def __init__(self):
        self.latest_data = {
            "breaker_on": None,
            "breaker_name": config.TUYA_DEVICE_NAME,
            "last_update": None,
            "status": "disabled",
            "error": None,
        }
        self.device: Optional[tinytuya.Device] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def initialize(self):
        """Initialize connection to Tuya device."""
        if not config.TUYA_ENABLED:
            self.latest_data["status"] = "disabled"
            print("Tuya integration disabled in config")
            return False

        if not TUYA_AVAILABLE:
            self.latest_data["status"] = "error"
            self.latest_data["error"] = "tinytuya not installed"
            print("Error: tinytuya library not installed")
            return False

        if not config.TUYA_DEVICE_ID or not config.TUYA_LOCAL_KEY:
            self.latest_data["status"] = "error"
            self.latest_data["error"] = "Missing device credentials"
            print("Error: Tuya device credentials not configured")
            return False

        try:
            print("Initializing Tuya Breaker Monitor...")
            self.device = tinytuya.Device(
                dev_id=config.TUYA_DEVICE_ID,
                address=config.TUYA_IP_ADDRESS,
                local_key=config.TUYA_LOCAL_KEY,
                version=config.TUYA_VERSION,
            )

            # Set connection timeout
            self.device.set_socketTimeout(5)

            # Test connection
            status = self.device.status()
            if status and 'dps' in status:
                self.latest_data["status"] = "ok"
                print(f"✓ Connected to {config.TUYA_DEVICE_NAME}")
                return True
            else:
                raise Exception("Unable to get device status")

        except Exception as e:
            self.latest_data["status"] = "error"
            self.latest_data["error"] = str(e)
            print(f"Error connecting to Tuya device: {e}")
            return False

    def update_status(self):
        """Fetch latest breaker status."""
        if not self.device or self.latest_data["status"] == "disabled":
            return

        try:
            status = self.device.status()

            if status and 'dps' in status:
                # DPS 1 is typically the main switch
                breaker_on = status['dps'].get('1', None)
                self.latest_data["breaker_on"] = breaker_on
                self.latest_data["last_update"] = time.time()
                self.latest_data["status"] = "ok"
                self.latest_data["error"] = None

                # Track state changes and duration
                if breaker_on is not None:
                    breaker_tracker.update_state(breaker_on)
                    duration = breaker_tracker.get_current_duration()
                    self.latest_data["duration"] = duration

                state_str = "ON" if self.latest_data["breaker_on"] else "OFF"
                duration_str = f" for {self.latest_data.get('duration', '?')}" if self.latest_data.get('duration') else ""
                print(f"[Tuya] {config.TUYA_DEVICE_NAME}: {state_str}{duration_str}")
            else:
                raise Exception("Invalid device response")

        except Exception as e:
            self.latest_data["status"] = "error"
            self.latest_data["error"] = str(e)
            print(f"Error fetching Tuya status: {e}")

    def _monitor_loop(self):
        """Background monitoring loop."""
        # Initial update
        self.update_status()

        # Continuous monitoring
        while self._running:
            time.sleep(config.REFRESH_INTERVAL)  # Use same interval as temperature
            self.update_status()

    def start_monitoring(self):
        """Start background monitoring thread."""
        if not self.initialize():
            return False

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print(f"✓ Tuya monitoring started (polling every {config.REFRESH_INTERVAL}s)")
        return True

    def stop_monitoring(self):
        """Stop background monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def get_latest_data(self) -> dict:
        """Return the latest breaker data."""
        return self.latest_data.copy()

    def turn_on(self) -> bool:
        """Turn the breaker ON."""
        if not self.device or self.latest_data["status"] != "ok":
            return False

        try:
            self.device.set_status(True, 1)  # DPS 1 controls the switch
            time.sleep(0.5)  # Brief delay for device to respond
            self.update_status()  # Update status immediately
            return True
        except Exception as e:
            print(f"Error turning breaker on: {e}")
            return False

    def turn_off(self) -> bool:
        """Turn the breaker OFF."""
        if not self.device or self.latest_data["status"] != "ok":
            return False

        try:
            self.device.set_status(False, 1)  # DPS 1 controls the switch
            time.sleep(0.5)  # Brief delay for device to respond
            self.update_status()  # Update status immediately
            return True
        except Exception as e:
            print(f"Error turning breaker off: {e}")
            return False


# Global monitor instance
breaker_monitor = TuyaBreakerMonitor()
