# YoLink Temperature Monitor - Quick Start

## ✅ Project Status: READY TO USE

Everything is set up and tested! Your YoLink temperature sensor is connected and working.

## 🎯 What You Have

- **Device Detected:** Temperature Sensor (YS8004-UC - Weatherproof Temperature Sensor)
- **Current Reading:** 92.1°F (last test)
- **Server Port:** 5002 (configured to avoid conflicts with ports 5000, 5001, 8000)
- **Local IP:** 192.168.86.83

## 🚀 How to Start

### Method 1: Using the startup script (easiest)
```bash
cd /Users/pavelkletskov/yolink/temp-monitor
./start.sh
```

### Method 2: Direct command
```bash
cd /Users/pavelkletskov/yolink/temp-monitor
./venv/bin/python web_server.py
```

## 🌐 Access URLs

### On this computer
```
http://localhost:5002/
```

### From other devices on your network
```
http://192.168.86.83:5002/
```

### For Telegram (use your public IP or domain)
```
http://YOUR_PUBLIC_IP:5002/
```

## 📱 Telegram Sharing

Since your host is already exposed to the internet, just share:
- **http://YOUR_PUBLIC_IP:5002/** (replace YOUR_PUBLIC_IP with your actual public IP)
- The page auto-refreshes every 30 seconds
- Shows current temperature and humidity
- Clean, mobile-friendly interface

## 🔧 Useful Commands

### Check which ports are available
```bash
./check_ports.sh
```

### Test the API (while server is running)
```bash
curl http://localhost:5002/api/temperature
```

### Run in background with screen
```bash
screen -S temp
./start.sh
# Press Ctrl+A then D to detach
```

### Reattach to background session
```bash
screen -r temp
```

## 📊 API Endpoints

1. **Main Page (HTML)** - `http://localhost:5002/`
   - Beautiful web interface
   - Auto-refreshes every 30 seconds

2. **JSON API** - `http://localhost:5002/api/temperature`
   ```json
   {
     "temperature": 92.1,
     "humidity": null,
     "device_name": "Temperature Sensor",
     "device_id": "d88b4c01000e936d",
     "last_update": "2026-02-13T03:07:42Z",
     "status": "ok",
     "error": null
   }
   ```

3. **Health Check** - `http://localhost:5002/health`
   - Returns 200 if OK, 503 if error

## ⚙️ Configuration

All settings are in [config.py](config.py):
- YoLink credentials (already configured)
- Server port (5002)
- Refresh interval (30 seconds)

## 📚 Documentation

- [SETUP.md](SETUP.md) - Complete setup guide with virtual environment info
- [README.md](README.md) - Feature overview and usage instructions

## 🔍 Troubleshooting

### Server won't start
```bash
./check_ports.sh  # Check if port 5002 is available
```

### Want to use a different port
Edit `config.py` and change `PORT = 5002` to any available port

### Need to see what's happening
Run the server in foreground mode (not in background) to see logs

## 🎉 You're All Set!

Your temperature monitor is ready to use. Just run `./start.sh` and share the link!

**Next Steps:**
1. Start the server: `./start.sh`
2. Test locally: Visit `http://localhost:5002/`
3. Share in Telegram: Use your public IP instead of localhost
4. Enjoy live temperature monitoring!
