# YoLink Temperature Monitor - Web Server

Share live temperature readings from your YoLink thermometer via a web link!

## What This Does

- Connects to YoLink cloud API
- Continuously polls your temperature sensor (every 30 seconds)
- Serves a beautiful web page with live readings
- Provides JSON API for programmatic access
- Auto-refreshes every 30 seconds
- Perfect for sharing in Telegram groups or embedding

## Setup

### 1. Install Dependencies

```bash
cd temp-monitor
pip install -r requirements.txt
```

### 2. Credentials

Your YoLink credentials are already configured in `config.py`:
- UAID: `ua_0E068FE895A04A1794575D6B1F0AA7B6`
- Secret Key: `sec_v1_ZJpttS95NkS7L+Ff9bdkXw==`

### 3. Run the Server

```bash
python web_server.py
```

The server will:
1. Connect to YoLink API
2. Find your temperature sensor
3. Start monitoring temperature
4. Launch web server on port 5002 (ports 5000, 5001, 8000 are already in use)

## Accessing Your Temperature

### Local Access
```
http://localhost:5002/
```

### Remote Access (for Telegram)
Replace `localhost` with your server's public IP or domain:
```
http://your-server-ip:5002/
```

Since your host is already exposed to the internet, you can share this URL directly in your Telegram group!

## API Endpoints

### Main Page (HTML)
```
GET /
```
Beautiful web page with auto-refresh, perfect for sharing

### JSON API
```
GET /api/temperature
```
Returns JSON:
```json
{
  "temperature": 72.5,
  "humidity": 45,
  "device_name": "Living Room Sensor",
  "device_id": "abc123",
  "last_update": "2025-02-12T18:30:00Z",
  "status": "ok",
  "error": null
}
```

### Health Check
```
GET /health
```
Returns 200 if connected, 503 if error

## Configuration

Edit `config.py` to change:
- `PORT` - Web server port (default: 5001)
- `HOST` - Listen address (default: 0.0.0.0)
- `REFRESH_INTERVAL` - How often to poll temperature in seconds (default: 30)

## Running as a Service

To keep it running in the background:

### Using screen
```bash
screen -S temp-monitor
python web_server.py
# Press Ctrl+A then D to detach
```

### Using nohup
```bash
nohup python web_server.py > temp-monitor.log 2>&1 &
```

### Using systemd (Linux)
Create `/etc/systemd/system/temp-monitor.service`:
```ini
[Unit]
Description=YoLink Temperature Monitor
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/temp-monitor
ExecStart=/usr/bin/python3 web_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable temp-monitor
sudo systemctl start temp-monitor
```

## Troubleshooting

### "No temperature sensor found"
The script will list all your devices. Check the output and modify `temperature_service.py` line 96-100 to match your device type.

### Port already in use
Change `PORT` in `config.py` to a different port (e.g., 5002, 8080)

### Can't access from internet
Make sure your firewall allows incoming connections on the port:
```bash
# Check if port is accessible
netstat -tuln | grep 5001

# Open firewall (example for ufw)
sudo ufw allow 5001
```

## Security Notes

- Your API credentials are stored in `config.py` - keep this file secure
- Consider adding authentication if exposing publicly
- The current setup allows anyone with the URL to view temperature
- For production, consider using HTTPS with nginx reverse proxy

## Features

✅ Real-time temperature monitoring
✅ Beautiful responsive web interface
✅ Auto-refresh every 30 seconds
✅ JSON API for automation
✅ Support for temperature + humidity sensors
✅ Error handling and status indicators
✅ Ready to share in Telegram

## Next Steps

Want to enhance this? You could add:
- Historical data storage (SQLite/PostgreSQL)
- Temperature graphs (Chart.js)
- Alerts when temperature exceeds thresholds
- Multiple sensor support
- Telegram bot integration
- MQTT real-time updates instead of polling
