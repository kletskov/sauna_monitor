"""
Data Logger for Temperature and Breaker State History

Stores temperature readings and breaker state changes with timestamps.
Persists to JSON files and keeps 1 month of history.
"""

import json
import os
import threading
from datetime import datetime, timedelta, timezone
from typing import Optional

try:
    from sauna_monitor.adapters.telegram.notifier import notifier
    TELEGRAM_IMPORTED = True
except ImportError:
    TELEGRAM_IMPORTED = False
    notifier = None


class TemperatureLogger:
    """Logs temperature readings with 1-minute granularity."""

    def __init__(self, filename="temperature_history.json"):
        self.filename = filename
        self.data = []  # List of {"timestamp": "ISO8601", "temperature": float, "humidity": float}
        self.last_save_time = None
        self.lock = threading.RLock()  # Use RLock for consistency
        self.load_from_disk()

    def load_from_disk(self):
        """Load existing data from disk."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.data = json.load(f)
                print(f"Loaded {len(self.data)} temperature records from {self.filename}")
                self.cleanup_old_data()
            except Exception as e:
                print(f"Error loading temperature history: {e}")
                self.data = []

    def save_to_disk(self):
        """Persist data to disk."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving temperature history: {e}")

    def cleanup_old_data(self):
        """Remove data older than 1 month."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        cutoff_str = cutoff.isoformat()

        with self.lock:
            original_len = len(self.data)
            self.data = [d for d in self.data if d.get("timestamp", "") >= cutoff_str]
            removed = original_len - len(self.data)
            if removed > 0:
                print(f"Cleaned up {removed} old temperature records (older than 30 days)")

    def add_reading(self, temperature: float, humidity: Optional[float] = None):
        """Add a temperature reading (with 1-minute granularity)."""
        now = datetime.now(timezone.utc)

        # Only save if at least 1 minute has passed since last save
        if self.last_save_time:
            time_since_last = (now - self.last_save_time).total_seconds()
            if time_since_last < 60:  # Less than 1 minute
                return

        with self.lock:
            record = {
                "timestamp": now.isoformat(),
                "temperature": temperature,
            }
            if humidity is not None:
                record["humidity"] = humidity

            self.data.append(record)
            self.last_save_time = now

            # Save to disk after every reading (to prevent data loss on restart)
            self.save_to_disk()

            # Cleanup old data every 100 records
            if len(self.data) % 100 == 0:
                self.cleanup_old_data()

    def get_recent_data(self, hours: int = 24):
        """Get temperature data for the last N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()

        with self.lock:
            return [d for d in self.data if d.get("timestamp", "") >= cutoff_str]

    def get_all_data(self):
        """Get all temperature data."""
        with self.lock:
            return self.data.copy()

    def get_history(self, hours: int = 24):
        """Alias for get_recent_data for API consistency."""
        return self.get_recent_data(hours)


class BreakerStateTracker:
    """Tracks breaker ON/OFF state changes and durations."""

    def __init__(self, filename="breaker_history.json"):
        self.filename = filename
        self.current_state = None  # True=ON, False=OFF
        self.state_since = None  # When did current state start
        self.history = []  # List of {"state": bool, "timestamp": "ISO8601", "duration_seconds": int}
        self.lock = threading.RLock()  # Use RLock to allow reentrant locking
        self.load_from_disk()

    def load_from_disk(self):
        """Load existing state history from disk."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.current_state = data.get("current_state")
                    self.state_since = data.get("state_since")
                    self.history = data.get("history", [])
                print(f"Loaded breaker state history: {len(self.history)} state changes")
                # No cleanup - keep all history
            except Exception as e:
                print(f"Error loading breaker history: {e}")
                self.history = []

    def save_to_disk(self):
        """Persist state data to disk."""
        try:
            with self.lock:
                data = {
                    "current_state": self.current_state,
                    "state_since": self.state_since,
                    "history": self.history
                }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving breaker history: {e}")

    def cleanup_old_data(self):
        """Keep all breaker history (no cleanup - user wants full log)."""
        # Breaker state changes are important events, keep all history forever
        pass

    def update_state(self, new_state: bool):
        """Update breaker state and track duration."""
        now = datetime.now(timezone.utc)

        with self.lock:
            # If state changed, record the transition
            if self.current_state is not None and self.current_state != new_state:
                duration = (now - datetime.fromisoformat(self.state_since)).total_seconds()

                # Add to history
                self.history.append({
                    "state": self.current_state,
                    "timestamp": self.state_since,
                    "duration_seconds": int(duration)
                })

                print(f"Breaker state changed: {'ON' if self.current_state else 'OFF'} for {self._format_duration(duration)}")

                # Send Telegram notification for state change
                if TELEGRAM_IMPORTED and notifier:
                    if new_state:
                        # Heater turned ON
                        notifier.notify_heater_on()
                    else:
                        # Heater turned OFF
                        duration_str = self._format_duration(duration)
                        notifier.notify_heater_off(duration_str)
                        # Reset ready notification when heater turns off
                        notifier.reset_ready_notification()

                # Cleanup and save
                if len(self.history) % 10 == 0:
                    self.cleanup_old_data()
                self.save_to_disk()

            # Update current state
            if self.current_state != new_state or self.state_since is None:
                self.current_state = new_state
                self.state_since = now.isoformat()
                self.save_to_disk()

    def get_current_duration(self) -> Optional[str]:
        """Get how long the breaker has been in current state."""
        if self.state_since is None:
            return None

        now = datetime.now(timezone.utc)
        since = datetime.fromisoformat(self.state_since)
        duration = (now - since).total_seconds()

        return self._format_duration(duration)

    def _format_duration(self, seconds: float) -> str:
        """Format duration as human-readable string (no seconds)."""
        seconds = int(seconds)

        if seconds < 60:
            return "< 1m"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"

    def get_history(self, hours: int = 24):
        """Get state change history for the last N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()

        with self.lock:
            return [h for h in self.history if h.get("timestamp", "") >= cutoff_str]


# Global instances
temp_logger = TemperatureLogger()
breaker_tracker = BreakerStateTracker()
