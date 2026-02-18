# Telegram Bot Setup

This guide explains how to set up Telegram notifications for your Sauna Monitor.

## Prerequisites

- A Telegram account
- Access to the Sauna lovers group where you want the bot to post

## Step 1: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Start a chat with BotFather and send the command: `/newbot`
3. Follow the prompts:
   - Choose a name for your bot (e.g., "Sauna Monitor")
   - Choose a username (must end in 'bot', e.g., "SaunaMonitorBot")
4. BotFather will give you a **bot token** - save this! It looks like:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

## Step 2: Add Bot to Your Group

1. Add your bot to the "Sauna lovers" Telegram group
2. Make sure the bot has permission to send messages in the group

## Step 3: Get Chat ID

You need to get the chat ID of your Telegram group. Here are two methods:

### Method A: Using a Web API (Easiest)

1. Send a message in your group (mention the bot with @YourBotName)
2. Visit this URL in your browser (replace YOUR_BOT_TOKEN with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Look for `"chat":{"id":-1001234567890}` in the response
4. Copy the chat ID (it will be negative for groups, like `-1001234567890`)

### Method B: Using Python Script

Create a temporary script to get the chat ID:

```python
import requests

BOT_TOKEN = "your_bot_token_here"
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
print(response.json())
```

Look for the chat ID in the output.

## Step 4: Configure the Bot

1. Open [config.py](config.py) in your project directory
2. Update the Telegram settings:

```python
# Telegram Bot Configuration
TELEGRAM_ENABLED = True  # Change to True
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Your bot token
TELEGRAM_CHAT_ID = "-1001234567890"  # Your group chat ID

# Telegram Notification Settings
TELEGRAM_READY_TEMP = 90  # Temperature in °C to trigger "sauna ready" notification
TELEGRAM_LONG_OFF_HOURS = 12  # Hours to wait before sending "long off" reminder
```

## Step 5: Install Dependencies

Install the required Python package:

```bash
./venv/bin/pip install python-telegram-bot
```

Or install all requirements:

```bash
./venv/bin/pip install -r requirements.txt
```

## Step 6: Restart the Service

If running as a LaunchAgent:

```bash
launchctl unload ~/Library/LaunchAgents/com.kletskov.sauna-monitor.plist
launchctl load ~/Library/LaunchAgents/com.kletskov.sauna-monitor.plist
```

Or if running manually:

```bash
./start.sh
```

## What Notifications Will Be Sent?

The bot will automatically send notifications for:

1. **🔥 Heater Turned ON**
   - Sent immediately when the sauna heater is turned on

2. **🌡️ Sauna Ready**
   - Sent when temperature reaches 90°C (configurable)
   - Only sent once per heating session
   - Only sent when heater is actively ON

3. **❄️ Heater Turned OFF**
   - Sent when the heater is turned off
   - Includes how long it was on

## Troubleshooting

### Bot not sending messages

1. **Check logs:**
   ```bash
   # If running manually
   # Logs will appear in console

   # If running as service
   launchctl list | grep sauna-monitor
   ```

2. **Verify bot token and chat ID are correct:**
   - Try sending a test message using the Telegram API:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" \
        -d "chat_id=<YOUR_CHAT_ID>" \
        -d "text=Test message"
   ```

3. **Check bot permissions:**
   - Make sure the bot is still in the group
   - Verify the bot has permission to send messages

### "python-telegram-bot not installed" error

Install the package:
```bash
./venv/bin/pip install python-telegram-bot
```

### Bot sends duplicate notifications

This shouldn't happen as the code tracks state changes. If it does:
- Check if you're running multiple instances of the service
- Restart the service to reset the state tracker

## Testing

To test notifications without waiting for actual events:

1. Manually toggle the sauna heater on/off
2. The bot should send notifications immediately
3. Check your Telegram group for the messages

## Example Notifications

The bot sends messages like:

- 🔥 **Sauna heater is ON!**

  Time to get ready for some heat! 🧖‍♂️

- 🌡️ **Sauna is READY!**

  Temperature reached 90°C 🔥

  Time to enjoy! 🧖‍♀️🧖‍♂️

- ❄️ **Sauna heater is OFF**

  It was on for 2h 15m.

## Privacy & Security

- The bot token should be kept secret (it's excluded from git via .gitignore)
- Only add the bot to groups you trust
- The bot can only send messages, not read or control anything

## Disabling Notifications

To disable Telegram notifications without removing the code:

1. Open [config.py](config.py)
2. Set `TELEGRAM_ENABLED = False`
3. Restart the service
