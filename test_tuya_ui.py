#!/usr/bin/env python3
"""
Quick test to show Tuya UI without real device.
This creates fake breaker data to preview the interface.
"""

# Temporarily modify config to enable Tuya with test data
import sys
sys.path.insert(0, '.')

import config

# Override config for testing
config.TUYA_ENABLED = True
config.TUYA_DEVICE_NAME = "Sauna Breaker (TEST)"

# Import after config override
from sauna_monitor.adapters.tuya.poller import breaker_monitor

# Set fake data
breaker_monitor.latest_data = {
    "breaker_on": True,  # Change to False to test OFF state
    "breaker_name": "Sauna Breaker",
    "last_update": 1234567890,
    "status": "ok",
    "error": None,
}

print("Tuya test data configured!")
print("Breaker status:", "ON" if breaker_monitor.latest_data["breaker_on"] else "OFF")
print("\nYou should now see the breaker status in top-left corner at:")
print("http://hockey-blast.com:5002/")
