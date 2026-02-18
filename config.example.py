"""
YoLink Temperature Monitor Configuration Template

Copy this file to config.py and fill in your credentials.
"""

# YoLink API Credentials
# Get these from: https://yolink.net/Account
YOLINK_UAID = "your_uaid_here"
YOLINK_SECRET_KEY = "your_secret_key_here"

# Web Server Configuration
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5002  # Change if port is already in use

# Temperature Refresh Interval (seconds)
REFRESH_INTERVAL = 30  # Poll temperature every 30 seconds

# Temperature Display
DISPLAY_FAHRENHEIT = False  # Set to False to display Celsius

# Tuya WiFi Breaker (Sauna Control)
# Set TUYA_ENABLED = False to disable Tuya integration
TUYA_ENABLED = False
TUYA_DEVICE_ID = "your_device_id"
TUYA_LOCAL_KEY = "your_local_key"
TUYA_IP_ADDRESS = "192.168.x.x"
TUYA_VERSION = 3.4
TUYA_DEVICE_NAME = "Sauna"  # Display name

# Telegram Bot Configuration
# Create a bot with @BotFather on Telegram to get the token
# Add the bot to your group and get the chat ID
TELEGRAM_ENABLED = False  # Set to True to enable Telegram notifications
TELEGRAM_BOT_TOKEN = ""  # Get from @BotFather on Telegram
TELEGRAM_CHAT_ID = ""  # Get chat ID from your group (e.g., "-1001234567890")

# Telegram Notification Settings
TELEGRAM_READY_TEMP = 90  # Temperature in °C to trigger "sauna ready" notification
TELEGRAM_LONG_OFF_HOURS = 12  # Hours to wait before sending "long off" reminder
