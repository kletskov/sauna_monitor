# Auto-Start Setup for macOS

This guide explains how to configure the Sauna Monitor to start automatically when your Mac boots.

## Installation

Run the installation script:

```bash
./install-autostart.sh
```

This will:
- Install a LaunchAgent that runs on login
- Configure automatic restart if the service crashes
- Set up logging

## Verification

Check if the service is running:

```bash
launchctl list | grep sauna-monitor
```

View logs:

```bash
tail -f sauna-monitor.log
tail -f sauna-monitor-error.log
```

Test the web interface:

```bash
open http://localhost:5002
```

## Management

**Stop the service:**
```bash
launchctl unload ~/Library/LaunchAgents/com.kletskov.sauna-monitor.plist
```

**Start the service:**
```bash
launchctl load ~/Library/LaunchAgents/com.kletskov.sauna-monitor.plist
```

**Restart the service:**
```bash
launchctl unload ~/Library/LaunchAgents/com.kletskov.sauna-monitor.plist
launchctl load ~/Library/LaunchAgents/com.kletskov.sauna-monitor.plist
```

## Uninstallation

To remove auto-start:

```bash
./uninstall-autostart.sh
```

## Troubleshooting

### Service won't start

1. Check logs:
   ```bash
   cat sauna-monitor-error.log
   ```

2. Verify config.py exists and has correct credentials

3. Ensure virtual environment is set up:
   ```bash
   ./venv/bin/python --version
   ```

4. Test manual start:
   ```bash
   ./start.sh
   ```

### Port already in use

If port 5002 is occupied, edit `config.py` and change the `PORT` setting, then restart the service.

### Permission errors

The service runs as your user account, so it has the same permissions as when you run it manually.

## Files

- `com.kletskov.sauna-monitor.plist` - LaunchAgent configuration
- `~/Library/LaunchAgents/com.kletskov.sauna-monitor.plist` - Installed location
- `sauna-monitor.log` - Standard output log
- `sauna-monitor-error.log` - Error log
