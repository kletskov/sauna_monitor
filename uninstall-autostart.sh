#!/bin/bash
# Uninstall Sauna Monitor LaunchAgent

set -e

PLIST_NAME="com.kletskov.sauna-monitor.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=========================================="
echo "Sauna Monitor - Auto-Start Uninstallation"
echo "=========================================="
echo ""

# Check if service exists
if [ ! -f "$PLIST_DEST" ]; then
    echo "❌ Service not found. Already uninstalled?"
    exit 0
fi

# Unload the service
echo "Stopping service..."
launchctl unload "$PLIST_DEST" 2>/dev/null || true

# Remove plist file
echo "Removing LaunchAgent..."
rm "$PLIST_DEST"

echo ""
echo "✓ Uninstallation complete!"
echo ""
echo "The service will no longer start automatically."
echo "To start manually, run: ./start.sh"
echo ""
