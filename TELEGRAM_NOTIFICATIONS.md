# Telegram Notifications Summary

Your SweatMarshal bot (@SweatMarshalBot) will send the following notifications to the "Cinco de baños" group:

## Event-Driven Notifications (Immediate)

### 1. Heater Turns ON
**Trigger:** When sauna heater switches from OFF to ON
**Frequency:** Every time it turns on
**Message:**
```
🔥 GAME ON! 🎮

Sauna heater just fired up! Time to get those towels ready! 🧖‍♂️💪
```

### 2. Heater Turns OFF
**Trigger:** When sauna heater switches from ON to OFF
**Frequency:** Every time it turns off
**Message:**
```
🏁 GAME OVER!

Sauna ran for [duration]. Drive safe and hydrate! 💧

Until next time, champions! 👋
```

### 3. Sauna Ready (90°C)
**Trigger:** When temperature reaches 90°C AND heater is ON
**Frequency:** Once per heating session (won't spam if temp stays above 90°C)
**Message:**
```
🌡️ TIME TO GET BUTT NAKED! 🍑

Sauna hit 90°C - perfect sweat territory! 💦

Strip down and GO GO GO! 🏃‍♂️💨

📊 Live stats: http://hockey-blast.com:5002/
```

## Scheduled Notifications

### 4. Wednesday 4PM Reminder
**Trigger:** Every Wednesday at 4:00 PM (when sauna is OFF)
**Frequency:** Once per Wednesday
**Message:**
```
📅 HUMP DAY HEAT CHECK! 🐫🔥

Sauna's been chillin' for [duration]...

Wednesday afternoon = perfect time to sweat out the work week! 💪

Who's ready to turn this frozen castle back into a furnace? 🏰➡️🔥
```

### 5. Weekly Rust Warnings
**Trigger:** When sauna has been OFF for 1+ weeks
**Frequency:** Maximum once per week
**Messages escalate with severity:**

#### After 1 week OFF:
```
🕸️ RUST ALERT! ⚠️

Sauna's been off for [duration]...

Pretty sure I saw a spider moving in. 🕷️

Time to fire it up before it turns into a storage unit! 📦
```

#### After 2 weeks OFF:
```
🦠 DOUBLE RUST WARNING! 🚨

TWO WEEKS without heat! ([duration])

The sauna's starting to forget its purpose in life... 😢

Let's remind it what it was born to do! 🔥
```

#### After 3+ weeks OFF:
```
☠️ CRITICAL RUST LEVEL! ☠️

[N] WEEKS! That's [duration] of sadness!

At this point, the sauna might be developing sentience from loneliness... 🤖

HEAT. IT. UP. NOW! 🆘
```

## Anti-Spam Protection

- **90°C Ready:** Only sent once per heating session (resets when heater turns off)
- **Wednesday Reminder:** Only once per Wednesday
- **Weekly Rust:** Maximum once every 7 days, even if multiple weeks have passed

## Configuration

Configure in your `config.py` (copy from [config.example.py](config.example.py)):
- `TELEGRAM_ENABLED = True`
- `TELEGRAM_BOT_TOKEN = "your_bot_token_from_botfather"`
- `TELEGRAM_CHAT_ID = "your_group_chat_id"`
- `TELEGRAM_READY_TEMP = 90` (°C)

## Testing

To test the bot immediately after setup:
1. Turn the sauna heater ON → Should get "GAME ON" message
2. Wait for temp to reach 90°C → Should get "TIME TO GET BUTT NAKED" message
3. Turn the heater OFF → Should get "GAME OVER" message

The scheduled notifications (Wednesday 4PM, weekly rust) will run automatically based on the schedule.

## Disabling Notifications

To temporarily disable:
```python
# In config.py
TELEGRAM_ENABLED = False
```

Then restart the service.
