# YoLink Temperature Monitor - Complete Setup Guide

## Project Structure

```
/Users/pavelkletskov/yolink/
├── yolink-api/              # Official YoLink Python API (cloned from GitHub)
└── temp-monitor/            # Our temperature monitoring web app
    ├── venv/                # Python virtual environment (isolated dependencies)
    ├── config.py            # YoLink credentials and settings
    ├── temperature_service.py  # Background service that polls temperature
    ├── web_server.py        # Flask web server with shareable endpoints
    ├── requirements.txt     # Python package dependencies
    ├── README.md            # Usage documentation
    ├── SETUP.md            # This file - setup instructions
    └── .gitignore           # Git ignore patterns
```

## Dependencies

This project uses a **virtual environment (venv)** to isolate Python packages. This means:
- All packages are installed only for this project
- No conflicts with system Python or other projects
- Easy to reproduce and deploy

## Step-by-Step Setup

### 1. Virtual Environment (Already Created)

The venv is located at: `/Users/pavelkletskov/yolink/temp-monitor/venv/`

To activate it in a new terminal session:
```bash
cd /Users/pavelkletskov/yolink/temp-monitor
source venv/bin/activate
```

You'll see `(venv)` in your prompt when activated.

To deactivate:
```bash
deactivate
```

### 2. Installed Packages

All dependencies are already installed in the venv:
- `flask` - Web framework
- `aiohttp` - Async HTTP client for YoLink API
- `aiomqtt` - MQTT client for real-time events
- `pydantic` - Data validation
- `tenacity` - Retry logic
- `yolink-api` - Official YoLink Python library (installed from local clone)

### 3. YoLink API Credentials (Already Configured)

File: `config.py`
- UAID: `ua_0E068FE895A04A1794575D6B1F0AA7B6`
- Secret Key: `sec_v1_ZJpttS95NkS7L+Ff9bdkXw==`

**Security Note:** These credentials are stored in plaintext. If you commit this to a public repo, consider using environment variables or a secrets manager.

## Port Configuration

**Current port:** 5002

Occupied ports on this host:
- 5000, 5001, 8000 - Other services running
- 5002 - Available (configured for this app)

Available alternative ports if needed: 5003, 5004, 8002, 8080, 9000

## Running the Application

### Option 1: Using the Virtual Environment (Recommended)

```bash
cd /Users/pavelkletskov/yolink/temp-monitor
source venv/bin/activate
python web_server.py
```

### Option 2: Direct Execution (No Activation Needed)

```bash
cd /Users/pavelkletskov/yolink/temp-monitor
./venv/bin/python web_server.py
```

### Option 3: Using Absolute Path

```bash
/Users/pavelkletskov/yolink/temp-monitor/venv/bin/python \
  /Users/pavelkletskov/yolink/temp-monitor/web_server.py
```

## What Happens When You Run It

1. **Initialization (2-5 seconds)**
   - Connects to YoLink API
   - Authenticates with your credentials
   - Finds your temperature sensor(s)
   - Fetches initial temperature reading

2. **Background Monitoring**
   - Polls temperature every 30 seconds (configurable in `config.py`)
   - Updates in-memory cache with latest readings
   - Runs in a background thread

3. **Web Server**
   - Starts Flask server on port 5001
   - Serves HTML page and JSON API
   - Accessible from anywhere if your firewall allows

## Accessing Your Temperature

### Local Testing
```
http://localhost:5002/
```

### From Other Devices on Your Network
```
http://YOUR_LOCAL_IP:5002/
```

To find your local IP:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### From Internet (For Telegram Sharing)

If your host is already exposed to the internet:
```
http://YOUR_PUBLIC_IP:5002/
http://YOUR_DOMAIN:5002/
```

Make sure port 5002 is open in your firewall:
```bash
# Check if port is listening
sudo lsof -i :5002

# Open port (if using firewall)
sudo ufw allow 5002
```

## Available Endpoints

### 1. Main Page (Human-Readable)
```
GET http://localhost:5001/
```
- Beautiful HTML interface
- Auto-refreshes every 30 seconds
- Shows temperature, humidity, device name, status

### 2. JSON API (For Automation)
```
GET http://localhost:5001/api/temperature
```

Example response:
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

### 3. Health Check
```
GET http://localhost:5001/health
```
- Returns 200 if connected
- Returns 503 if error

## Running as a Background Service

### Using screen (Recommended for Quick Testing)

Start:
```bash
cd /Users/pavelkletskov/yolink/temp-monitor
screen -S temp-monitor
source venv/bin/activate
python web_server.py
```

Detach (keep it running): Press `Ctrl+A` then `D`

Reattach:
```bash
screen -r temp-monitor
```

Stop: Reattach and press `Ctrl+C`

### Using nohup

Start:
```bash
cd /Users/pavelkletskov/yolink/temp-monitor
nohup ./venv/bin/python web_server.py > temp-monitor.log 2>&1 &
echo $! > temp-monitor.pid
```

Check status:
```bash
tail -f /Users/pavelkletskov/yolink/temp-monitor/temp-monitor.log
```

Stop:
```bash
kill $(cat /Users/pavelkletskov/yolink/temp-monitor/temp-monitor.pid)
```

### Using systemd (Linux Production)

Create `/etc/systemd/system/yolink-temp-monitor.service`:
```ini
[Unit]
Description=YoLink Temperature Monitor
After=network.target

[Service]
Type=simple
User=pavelkletskov
WorkingDirectory=/Users/pavelkletskov/yolink/temp-monitor
ExecStart=/Users/pavelkletskov/yolink/temp-monitor/venv/bin/python web_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable yolink-temp-monitor
sudo systemctl start yolink-temp-monitor
sudo systemctl status yolink-temp-monitor
```

View logs:
```bash
sudo journalctl -u yolink-temp-monitor -f
```

## Configuration

Edit `config.py` to customize:

```python
# Change web server port
PORT = 5002  # Default: 5001

# Change polling interval
REFRESH_INTERVAL = 60  # Default: 30 seconds

# Change listen address
HOST = "127.0.0.1"  # Default: "0.0.0.0" (all interfaces)
```

## Troubleshooting

### "No temperature sensor found"

The script will list all your devices. If it doesn't auto-detect your thermometer:

1. Run manually to see device list:
   ```bash
   ./venv/bin/python temperature_service.py
   ```

2. Edit `temperature_service.py` line 96-100 to match your device type

### "Port 5001 already in use"

Change the port in `config.py`:
```python
PORT = 8080  # Or any other available port
```

### "Cannot connect to YoLink API"

Check credentials in `config.py` and verify internet connection:
```bash
curl https://api.yosmart.com
```

### Virtual Environment Issues

If packages are missing, reinstall:
```bash
cd /Users/pavelkletskov/yolink/temp-monitor
rm -rf venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install -e ../yolink-api
```

## Updating Dependencies

If you need to add new packages:

1. Activate venv:
   ```bash
   source venv/bin/activate
   ```

2. Install package:
   ```bash
   pip install package-name
   ```

3. Update requirements.txt:
   ```bash
   pip freeze > requirements.txt
   ```

## Security Considerations

- [ ] Your API credentials are in `config.py` - keep this file secure
- [ ] The web server has no authentication - anyone with the URL can view
- [ ] Consider using HTTPS with nginx reverse proxy for production
- [ ] Consider adding basic auth or API keys for public deployment
- [ ] Don't commit `config.py` to public GitHub repos

## For Telegram Sharing

1. Make sure the server is running
2. Get your public IP or domain
3. Share this link in Telegram:
   ```
   http://your-server:5001/
   ```

The page auto-refreshes every 30 seconds, perfect for live monitoring!

## Need Help?

- Check logs: `tail -f temp-monitor.log` (if using nohup)
- Test API directly: `curl http://localhost:5001/api/temperature`
- Run in foreground to see errors: `./venv/bin/python web_server.py`
- Check YoLink API status: Visit official docs or check their status page

## Future Enhancements

Consider adding:
- [ ] Database storage (SQLite/PostgreSQL) for historical data
- [ ] Temperature graphs using Chart.js or Plotly
- [ ] Email/SMS alerts when temperature exceeds thresholds
- [ ] Multiple sensor support
- [ ] Telegram bot integration for push notifications
- [ ] MQTT real-time updates instead of polling
- [ ] Docker container for easy deployment
- [ ] HTTPS support with Let's Encrypt
