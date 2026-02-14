# Tuya WiFi Breaker Setup Guide

## What You're Adding

Your WiFi breaker (controlling the sauna circuit) can be monitored and controlled through the webapp.

## Prerequisites

- Smart Life app installed on your phone
- Your WiFi breaker already paired with Smart Life app
- 10 minutes for setup

## Step 1: Create Tuya Developer Account

1. Go to: https://iot.tuya.com
2. Click "Register" (it's free!)
3. Complete registration with email verification

## Step 2: Create Cloud Project

1. Log into https://iot.tuya.com
2. Go to **Cloud** → **Development**
3. Click **Create Cloud Project**
   - Project Name: "Home Automation"
   - Industry: "Smart Home"
   - Data Center: Select your region (US, EU, etc.)
4. Click **Create**

## Step 3: Subscribe to APIs

1. In your project, go to **Service API** tab
2. Subscribe to these APIs (click "Subscribe"):
   - **IoT Core**
   - **Authorization**
3. Click **Go to Authorize** after subscribing

## Step 4: Link Your Smart Life App

1. Still in your project, go to **Devices** tab
2. Click **Link Tuya App Account**
3. Select **Automatic** → **Read Only Status**
4. A QR code will appear
5. Open Smart Life app → **Me** tab → Click QR scanner icon (top right)
6. Scan the QR code
7. Your devices should now appear in the Devices list

## Step 5: Get API Credentials

1. In your project, click **Overview** tab
2. Copy these values:
   - **Access ID/Client ID** (looks like: `abcdef1234567890abcd`)
   - **Access Secret/Client Secret** (longer string)
3. Note your **Data Center** (US, EU, CN, etc.)

## Step 6: Run TinyTuya Setup Wizard

Open terminal and run:

```bash
cd /Users/pavelkletskov/yolink/temp-monitor
source venv/bin/activate
python -m tinytuya wizard
```

The wizard will ask you:

1. **Enter API Key** → Paste your Access ID
2. **Enter API Secret** → Paste your Access Secret
3. **Enter API Region** → us, eu, cn, etc.
4. **Enter Device ID** → Press Enter to discover all devices

The wizard will:
- Connect to Tuya cloud
- Download your device list
- Get local encryption keys
- Scan your network for device IPs
- Create `tuyadevices.json` with all credentials

## Step 7: Find Your Sauna Breaker

After the wizard completes, open the generated file:

```bash
cat tuyadevices.json
```

Look for your sauna breaker by name. You'll see something like:

```json
{
  "name": "Sauna Breaker",
  "id": "bf1234567890abcdef",
  "key": "1234567890abcdef",
  "ip": "192.168.1.100",
  "version": "3.3"
}
```

Copy these 4 values:
- **Device ID** (id)
- **Local Key** (key)
- **IP Address** (ip)
- **Version** (version)

## Step 8: Add to Config

Edit `config.py` and add at the bottom:

```python
# Tuya WiFi Breaker (Sauna Control)
TUYA_ENABLED = True  # Set to False to disable
TUYA_DEVICE_ID = "bf1234567890abcdef"  # From tuyadevices.json
TUYA_LOCAL_KEY = "1234567890abcdef"    # From tuyadevices.json
TUYA_IP_ADDRESS = "192.168.1.100"      # From tuyadevices.json
TUYA_VERSION = 3.3                      # From tuyadevices.json
TUYA_DEVICE_NAME = "Sauna Breaker"     # Display name
```

## Step 9: Restart Server

```bash
pkill -f "web_server.py"
./start.sh
```

The webapp will now show the sauna breaker status!

## Troubleshooting

### "Device not found" during wizard
- Make sure devices are online in Smart Life app
- Check that you linked your Smart Life account to the cloud project
- Verify you subscribed to IoT Core and Authorization APIs

### "Connection timeout"
- Ensure device and computer are on same WiFi network
- Check device IP hasn't changed (use static IP if possible)
- Verify local key is correct

### "Version mismatch"
- Try version 3.3 first (most common)
- If that fails, try 3.4
- Check device protocol version in tuyadevices.json

### Manual device discovery
If wizard doesn't work, try network scan:
```bash
python -m tinytuya scan
```

## Security Notes

- Local keys are sensitive - keep them private
- Consider using environment variables for production
- The integration uses local control (no cloud after setup)
- Device must be on your network to control

## Testing Your Setup

After adding credentials to config.py, test the connection:

```bash
cd /Users/pavelkletskov/yolink/temp-monitor
source venv/bin/activate
python -c "
import tinytuya
import config

device = tinytuya.OutletDevice(
    config.TUYA_DEVICE_ID,
    config.TUYA_IP_ADDRESS,
    config.TUYA_LOCAL_KEY,
    config.TUYA_VERSION
)

status = device.status()
print('Device Status:', status)
print('Breaker is:', 'ON' if status['dps']['1'] else 'OFF')
"
```

If you see the status, it's working! 🎉
