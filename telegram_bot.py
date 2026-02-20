"""
Telegram Bot Service for Sauna Monitor

Sends event-driven notifications to a Telegram group about sauna status.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import logging

try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

import config

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends notifications to Telegram group based on sauna events."""

    def __init__(self):
        self.bot: Optional[Bot] = None
        self.chat_id: Optional[str] = None
        self.enabled = False
        self.last_ready_notification = None  # Track when we last sent "ready" notification
        self.last_weekly_reminder = None  # Track last weekly reminder to avoid spam

        if not config.TELEGRAM_ENABLED:
            logger.info("Telegram notifications disabled in config")
            return

        if not TELEGRAM_AVAILABLE:
            logger.warning("python-telegram-bot not installed. Install with: pip install python-telegram-bot")
            return

        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
            logger.warning("Telegram bot token or chat ID not configured")
            return

        try:
            self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
            self.chat_id = config.TELEGRAM_CHAT_ID
            self.enabled = True
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")

    async def send_message(self, message: str, disable_web_page_preview: bool = False):
        """Send a message to the configured Telegram chat."""
        if not self.enabled:
            return

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=disable_web_page_preview
            )
            logger.info(f"Sent Telegram message: {message}")
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")

    def send_message_sync(self, message: str, disable_web_page_preview: bool = False):
        """Synchronous wrapper for sending messages."""
        if not self.enabled:
            return

        try:
            # Create a new event loop if we're not in an async context
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule the task
                    asyncio.create_task(self.send_message(message, disable_web_page_preview))
                else:
                    loop.run_until_complete(self.send_message(message, disable_web_page_preview))
            except RuntimeError:
                # No event loop, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.send_message(message, disable_web_page_preview))
        except Exception as e:
            logger.error(f"Error in send_message_sync: {e}")

    def notify_heater_on(self):
        """Notify that the heater turned on."""
        message = "🔥 <b>GAME ON!</b> 🎮\n\nSauna heater just fired up! Time to get those towels ready! 🧖‍♂️💪"
        self.send_message_sync(message)

    def notify_heater_off(self, duration: str):
        """Notify that the heater turned off."""
        message = f"🏁 <b>GAME OVER!</b>\n\nSauna ran for {duration}. Drive safe and hydrate! 💧\n\nUntil next time, champions! 👋"
        self.send_message_sync(message)

    def notify_sauna_ready(self, temperature: float):
        """Notify that sauna reached target temperature (90°C)."""
        # Only send once per heating session - reset when heater turns off
        if self.last_ready_notification is not None:
            # Already sent during this session, don't send again
            return

        self.last_ready_notification = datetime.now()
        message = (
            f"🌡️ <b>TIME TO GET BUTT NAKED!</b> 🍑\n\n"
            f"Sauna hit {temperature}°C ! 🔥\n\n"
            f"📊 Stats: http://hockey-blast.com:5002/"
        )
        self.send_message_sync(message, disable_web_page_preview=True)

    def notify_wednesday_reminder(self, off_duration: str, current_temp: float = None):
        """Wednesday 3:33 PM reminder - time to poll for Thursday session."""
        temp_str = f" (currently {current_temp}°C)" if current_temp is not None else ""
        message = (
            f"📅 <b>HUMP DAY HEAT CHECK!</b> 🐫🔥\n\n"
            f"Sauna's been chillin' for {off_duration}{temp_str}...\n\n"
            f"Time to create the poll and see who's ready for tomorrow's sweat session! 🗳️💦\n\n"
            f"Who's ready to turn this frozen castle back into a badass air fryer? 🏰➡️🔥"
        )
        self.send_message_sync(message)

    def notify_weekly_rust_warning(self, weeks_off: int, off_duration: str):
        """Notify when sauna has been off for N weeks."""
        # Prevent spam - only send once per week
        now = datetime.now()
        if self.last_weekly_reminder:
            time_since_last = (now - self.last_weekly_reminder).total_seconds()
            if time_since_last < 604800:  # 7 days in seconds
                return

        self.last_weekly_reminder = now

        if weeks_off == 1:
            message = (
                f"🕸️ <b>RUST ALERT!</b> ⚠️\n\n"
                f"Sauna's been off for {off_duration}...\n\n"
                f"Pretty sure I saw a spider moving in. 🕷️\n\n"
                f"Time to fire it up before it turns into a storage unit! 📦"
            )
        elif weeks_off == 2:
            message = (
                f"🦠 <b>DOUBLE RUST WARNING!</b> 🚨\n\n"
                f"TWO WEEKS without heat! ({off_duration})\n\n"
                f"The sauna's starting to forget its purpose in life... 😢\n\n"
                f"Let's remind it what it was born to do! 🔥"
            )
        else:
            message = (
                f"☠️ <b>CRITICAL RUST LEVEL!</b> ☠️\n\n"
                f"{weeks_off} WEEKS! That's {off_duration} of sadness!\n\n"
                f"At this point, the sauna might be developing sentience from loneliness... 🤖\n\n"
                f"HEAT. IT. UP. NOW! 🆘"
            )

        self.send_message_sync(message)

    def reset_ready_notification(self):
        """Reset the ready notification tracker (call when heater turns off)."""
        self.last_ready_notification = None


# Global notifier instance
notifier = TelegramNotifier()
