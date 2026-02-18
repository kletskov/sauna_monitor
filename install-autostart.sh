#!/bin/bash
# Install Sauna Monitor as LaunchAgent (auto-start on login)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.kletskov.sauna-monitor.plist"
PLIST_SOURCE="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=========================================="
echo "Sauna Monitor - Auto-Start Installation"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if config.py exists
if [ ! -f "$SCRIPT_DIR/config.py" ]; then
    echo "❌ config.py not found!"
    echo "Please create config.py from config.example.py and add your credentials."
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Stop existing service if running
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "Stopping existing service..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# Copy plist file
echo "Installing LaunchAgent..."
cp "$PLIST_SOURCE" "$PLIST_DEST"

# Load the service
echo "Loading service..."
launchctl load "$PLIST_DEST"

echo ""
echo "✓ Installation complete!"
echo ""
echo "Service details:"
echo "  Name: $PLIST_NAME"
echo "  Location: $PLIST_DEST"
echo "  Logs: $SCRIPT_DIR/sauna-monitor.log"
echo "  Error logs: $SCRIPT_DIR/sauna-monitor-error.log"
echo ""
echo "The service will:"
echo "  • Start automatically on login"
echo "  • Restart automatically if it crashes"
echo "  • Run in the background"
echo ""
echo "Useful commands:"
echo "  Check status:  launchctl list | grep sauna-monitor"
echo "  View logs:     tail -f $SCRIPT_DIR/sauna-monitor.log"
echo "  Stop service:  launchctl unload $PLIST_DEST"
echo "  Start service: launchctl load $PLIST_DEST"
echo "  Uninstall:     ./uninstall-autostart.sh"
echo ""
