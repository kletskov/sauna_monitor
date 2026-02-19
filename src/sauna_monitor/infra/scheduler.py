"""
Notification Scheduler for Telegram Bot

Handles periodic checks for:
- Wednesday 3:33 PM reminders
- Weekly rust warnings when sauna is off
"""

import threading
import time
from datetime import datetime, timezone

try:
    from sauna_monitor.adapters.telegram.notifier import notifier
    from sauna_monitor.infra.storage.json import breaker_tracker
    from sauna_monitor.adapters.yolink.poller import monitor
    IMPORTS_OK = True
except ImportError:
    IMPORTS_OK = False


class NotificationScheduler:
    """Schedules periodic notification checks."""

    def __init__(self):
        self.running = False
        self.thread = None
        self.last_wednesday_check = None

    def start(self):
        """Start the scheduler in a background thread."""
        if not IMPORTS_OK or not notifier.enabled:
            print("Notification scheduler disabled (Telegram not configured)")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("✓ Notification scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def _run_scheduler(self):
        """Main scheduler loop - runs every 5 minutes."""
        while self.running:
            try:
                self._check_notifications()
            except Exception as e:
                print(f"Error in notification scheduler: {e}")

            # Sleep for 5 minutes between checks
            time.sleep(300)

    def _check_notifications(self):
        """Check if any notifications should be sent."""
        now = datetime.now()

        # Check if sauna is OFF
        if not breaker_tracker.current_state and breaker_tracker.state_since:
            # Calculate how long it's been off
            state_since = datetime.fromisoformat(breaker_tracker.state_since)
            if state_since.tzinfo is None:
                state_since = state_since.replace(tzinfo=timezone.utc)

            now_utc = datetime.now(timezone.utc)
            off_seconds = (now_utc - state_since).total_seconds()
            off_duration = breaker_tracker._format_duration(off_seconds)

            # Check for Wednesday 3:33 PM reminder (within 10-minute window: 3:30-3:40)
            if now.weekday() == 2 and now.hour == 15 and 30 <= now.minute <= 40:  # Wednesday = 2
                # Only send once per Wednesday
                if not self.last_wednesday_check or self.last_wednesday_check.date() != now.date():
                    self.last_wednesday_check = now
                    # Get current temperature
                    current_temp = monitor.get_latest_data().get("temperature")
                    print(f"Sending Wednesday 3:33 PM reminder (off for {off_duration}, temp: {current_temp}°C)")
                    notifier.notify_wednesday_reminder(off_duration, current_temp)

            # Check for weekly rust warnings (every 7 days)
            off_days = off_seconds / 86400
            if off_days >= 7:
                weeks_off = int(off_days // 7)
                print(f"Checking weekly rust warning: {weeks_off} weeks off")
                notifier.notify_weekly_rust_warning(weeks_off, off_duration)


# Global scheduler instance
scheduler = NotificationScheduler()
