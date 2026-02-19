"""
Flask Web Server for YoLink Temperature Sharing

Provides shareable endpoints for viewing live temperature readings.
"""

import asyncio
import signal
import sys
import threading
from datetime import datetime

from flask import Flask, jsonify, render_template_string
import os

import config
from sauna_monitor.adapters.yolink.poller import monitor, start_monitoring
from sauna_monitor.adapters.tuya.poller import breaker_monitor
from sauna_monitor.infra.storage.json import temp_logger, breaker_tracker
from sauna_monitor.infra.scheduler import scheduler

# Set up Flask with static folder
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # Cache images for 5 minutes


# HTML template for shareable page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Temperature</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8/hammer.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            height: 100vh;
            overflow: hidden;
            background-image: url('/static/cinco_background.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.3);
            z-index: 1;
        }
        .heading {
            position: absolute;
            top: 30px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 3;
            font-size: 90px;
            font-weight: bold;
            color: #FFD700;
            text-align: center;
            text-shadow: 0 4px 12px rgba(0,0,0,0.8);
        }
        .content {
            position: relative;
            z-index: 2;
            text-align: center;
            color: white;
            text-shadow: 0 4px 12px rgba(0,0,0,0.8);
            margin-top: -60px;
        }
        .temperature {
            font-size: 140px;
            font-weight: bold;
            line-height: 1;
            margin: 0;
        }
        .unit {
            font-size: 62px;
        }
        .humidity {
            font-size: 60px;
            margin-top: 30px;
            opacity: 0.9;
        }
        .breaker-status {
            position: absolute;
            top: 280px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 3;
            background: rgba(0,0,0,0.6);
            padding: 20px 40px;
            border-radius: 30px;
            font-size: 36px;
            backdrop-filter: blur(10px);
            font-weight: bold;
            text-align: center;
            line-height: 1.3;
        }
        .breaker-status.on {
            color: #22c55e;
            border: 2px solid #22c55e;
        }
        .breaker-status.off {
            color: #94a3b8;
            border: 2px solid #64748b;
        }
        .chart-container {
            position: absolute;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            max-width: 1000px;
            height: 250px;
            z-index: 3;
            background: rgba(0,0,0,0.7);
            padding: 20px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        .chart-hint {
            position: absolute;
            top: 5px;
            right: 20px;
            font-size: 11px;
            color: rgba(255,255,255,0.5);
            z-index: 4;
        }
        .reset-zoom {
            position: absolute;
            top: 5px;
            right: 20px;
            padding: 5px 10px;
            background: rgba(255,215,0,0.2);
            border: 1px solid #FFD700;
            border-radius: 5px;
            color: #FFD700;
            font-size: 12px;
            cursor: pointer;
            z-index: 4;
            display: none;
        }
        .reset-zoom:hover {
            background: rgba(255,215,0,0.3);
        }
        @media (max-width: 768px) {
            .heading {
                top: 20px;
                font-size: 50px;
            }
            .breaker-status {
                top: 180px;
                font-size: 24px;
                padding: 15px 25px;
                line-height: 1.3;
            }
            .temperature {
                font-size: 95px;
            }
            .unit {
                font-size: 48px;
            }
            .humidity {
                font-size: 40px;
            }
            .chart-container {
                width: 95%;
                height: 235px;
                bottom: 60px;
                padding: 15px;
            }
            .chart-hint {
                font-size: 9px;
                right: 15px;
            }
            .reset-zoom {
                font-size: 10px;
                padding: 4px 8px;
                right: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="heading">Cinco de baños</div>

    {% if breaker_status == 'ok' %}
    <div class="breaker-status {{ 'on' if breaker_on else 'off' }}">
        Heater {{ 'ON' if breaker_on else 'OFF' }}{% if breaker_duration %}<br>for {{ breaker_duration }}{% endif %}
    </div>
    {% elif breaker_status == 'disabled' %}
    <div class="breaker-status off" style="opacity: 0.5;">
        Heater<br>DISABLED
    </div>
    {% elif breaker_status == 'error' %}
    <div class="breaker-status off" style="border-color: #ef4444;">
        Heater<br>ERROR
    </div>
    {% endif %}

    {% if status == 'ok' and temperature is not none %}
    <div class="content">
        <div class="temperature">
            {{ temperature }}<span class="unit">{{ temp_unit }}</span>
        </div>
        {% if humidity is not none %}
        <div class="humidity">
            Humidity: {{ humidity }}%
        </div>
        {% endif %}
    </div>
    {% elif status == 'error' %}
    <div class="content">
        <div style="font-size: 48px;">⚠️</div>
        <div style="font-size: 32px; margin-top: 20px;">Error</div>
        <div style="font-size: 18px; margin-top: 10px;">{{ error }}</div>
    </div>
    {% else %}
    <div class="content">
        <div style="font-size: 48px;">⏳</div>
        <div style="font-size: 32px; margin-top: 20px;">Initializing...</div>
    </div>
    {% endif %}

    {% if status == 'ok' %}
    <div class="chart-container">
        <div class="chart-hint">Scroll to zoom • Drag to pan</div>
        <button class="reset-zoom" id="resetZoom" onclick="resetChartZoom()">Reset Zoom</button>
        <canvas id="tempChart"></canvas>
    </div>
    {% endif %}

    <script>
        let tempChart = null;

        // Reset chart zoom
        function resetChartZoom() {
            if (tempChart) {
                tempChart.resetZoom();
                document.getElementById('resetZoom').style.display = 'none';
            }
        }

        // Initialize chart with temperature history
        function initChart() {
            fetch('/api/temperature/history')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('tempChart');
                    if (!ctx || data.length === 0) return;

                    // Extract timestamps and temperatures
                    const labels = data.map(item => {
                        const date = new Date(item.timestamp);
                        return date.toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit',
                            month: 'short',
                            day: 'numeric'
                        });
                    });
                    const temperatures = data.map(item => item.temperature);

                    // Create chart
                    tempChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Temperature ({{ temp_unit }})',
                                data: temperatures,
                                borderColor: '#FFD700',
                                backgroundColor: 'rgba(255, 215, 0, 0.1)',
                                tension: 0.3,
                                pointRadius: 2,
                                pointHoverRadius: 5
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    labels: {
                                        color: 'white',
                                        font: { size: 14 }
                                    }
                                },
                                zoom: {
                                    zoom: {
                                        wheel: {
                                            enabled: true,
                                        },
                                        pinch: {
                                            enabled: true
                                        },
                                        mode: 'x',
                                        onZoomComplete: function() {
                                            document.getElementById('resetZoom').style.display = 'block';
                                        }
                                    },
                                    pan: {
                                        enabled: true,
                                        mode: 'x',
                                        onPanComplete: function() {
                                            document.getElementById('resetZoom').style.display = 'block';
                                        }
                                    },
                                    limits: {
                                        x: {min: 'original', max: 'original'}
                                    }
                                }
                            },
                            scales: {
                                x: {
                                    ticks: {
                                        color: 'white',
                                        maxRotation: 45,
                                        minRotation: 45,
                                        maxTicksLimit: 10
                                    },
                                    grid: {
                                        color: 'rgba(255,255,255,0.1)'
                                    }
                                },
                                y: {
                                    ticks: {
                                        color: 'white'
                                    },
                                    grid: {
                                        color: 'rgba(255,255,255,0.1)'
                                    }
                                }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading temperature history:', error));
        }

        // Update temperature and breaker status dynamically
        function updateData() {
            fetch('/api/temperature')
                .then(response => response.json())
                .then(data => {
                    const tempData = data.temperature;
                    const breakerData = data.breaker;

                    // Update temperature display
                    const tempElement = document.querySelector('.temperature');
                    if (tempElement && tempData.temperature !== null) {
                        tempElement.innerHTML = tempData.temperature + '<span class="unit">{{ temp_unit }}</span>';
                    }

                    // Update humidity display
                    const humidityElement = document.querySelector('.humidity');
                    if (humidityElement && tempData.humidity !== null) {
                        humidityElement.textContent = 'Humidity: ' + tempData.humidity + '%';
                    }

                    // Update breaker status
                    const breakerElement = document.querySelector('.breaker-status');
                    if (breakerElement && breakerData.status === 'ok') {
                        const isOn = breakerData.breaker_on;
                        const duration = breakerData.duration ? '<br>for ' + breakerData.duration : '';
                        breakerElement.innerHTML = 'Heater ' + (isOn ? 'ON' : 'OFF') + duration;
                        breakerElement.className = 'breaker-status ' + (isOn ? 'on' : 'off');
                    }

                    // Update chart with latest data
                    if (tempChart) {
                        fetch('/api/temperature/history')
                            .then(response => response.json())
                            .then(historyData => {
                                if (historyData.length > 0) {
                                    const labels = historyData.map(item => {
                                        const date = new Date(item.timestamp);
                                        return date.toLocaleTimeString('en-US', {
                                            hour: '2-digit',
                                            minute: '2-digit',
                                            month: 'short',
                                            day: 'numeric'
                                        });
                                    });
                                    const temperatures = historyData.map(item => item.temperature);

                                    tempChart.data.labels = labels;
                                    tempChart.data.datasets[0].data = temperatures;
                                    tempChart.update('none'); // Update without animation for smoother experience
                                }
                            });
                    }
                })
                .catch(error => console.error('Error updating data:', error));
        }

        // Initialize on page load
        initChart();

        // Update every 30 seconds
        setInterval(updateData, 30000);
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Main page with live temperature display."""
    data = monitor.get_latest_data()
    breaker_data = breaker_monitor.get_latest_data()

    # Format timestamp
    last_update_time = None
    if data.get("last_update"):
        try:
            dt = datetime.fromisoformat(data["last_update"])
            last_update_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            last_update_time = data["last_update"]

    return render_template_string(
        HTML_TEMPLATE,
        temperature=data.get("temperature"),
        humidity=data.get("humidity"),
        device_name=data.get("device_name"),
        status=data.get("status"),
        error=data.get("error"),
        last_update=data.get("last_update"),
        last_update_time=last_update_time,
        temp_unit=data.get("temp_unit", "°F"),
        breaker_status=breaker_data.get("status"),
        breaker_on=breaker_data.get("breaker_on"),
        breaker_name=breaker_data.get("breaker_name"),
        breaker_duration=breaker_data.get("duration"),
    )


@app.route("/api/temperature")
def api_temperature():
    """JSON API endpoint for programmatic access."""
    temp_data = monitor.get_latest_data()
    breaker_data = breaker_monitor.get_latest_data()

    # Combine both datasets
    combined_data = {
        "temperature": temp_data,
        "breaker": breaker_data
    }
    return jsonify(combined_data)


@app.route("/api/breaker/status")
def breaker_status():
    """Get breaker status only."""
    data = breaker_monitor.get_latest_data()
    return jsonify(data)


@app.route("/api/temperature/history")
def temperature_history():
    """Get temperature history for chart display."""
    history = temp_logger.get_history()
    return jsonify(history)


@app.route("/health")
def health():
    """Health check endpoint."""
    temp_data = monitor.get_latest_data()
    breaker_data = breaker_monitor.get_latest_data()

    temp_ok = temp_data.get("status") == "ok"
    breaker_ok = breaker_data.get("status") in ["ok", "disabled"]

    overall_ok = temp_ok and breaker_ok
    status_code = 200 if overall_ok else 503

    return jsonify({
        "status": "ok" if overall_ok else "error",
        "temperature": temp_data.get("status"),
        "breaker": breaker_data.get("status")
    }), status_code


def run_async_loop():
    """Run the async temperature monitoring loop in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_monitoring())


_shutting_down = False

def cleanup_and_exit(signum=None, frame=None):
    """Save all data and exit gracefully."""
    global _shutting_down

    # Prevent re-entry
    if _shutting_down:
        return

    _shutting_down = True

    print("\n\n🛑 Shutting down gracefully...")
    print("💾 Saving temperature history...")
    temp_logger.save_to_disk()
    print("💾 Saving breaker state history...")
    breaker_tracker.save_to_disk()
    print("✓ All data saved. Goodbye!")

    # Kill the process forcefully
    import subprocess
    subprocess.run(['kill', '-9', str(os.getpid())])


def main():
    """Start temperature monitor, breaker monitor, and web server."""
    print("=" * 60)
    print("YoLink Temperature & Sauna Monitor - Web Server")
    print("=" * 60)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    # Start temperature monitoring in background thread
    monitor_thread = threading.Thread(target=run_async_loop, daemon=True)
    monitor_thread.start()

    # Start Tuya breaker monitoring if enabled
    if config.TUYA_ENABLED:
        breaker_monitor.start_monitoring()

    # Start notification scheduler (Wednesday reminders, weekly rust warnings)
    scheduler.start()

    # Give monitors a moment to initialize
    import time
    time.sleep(2)

    print(f"\n🌐 Web server starting on http://{config.HOST}:{config.PORT}")
    print(f"\n📊 Access points:")
    print(f"   Main page:      http://localhost:{config.PORT}/")
    print(f"   JSON API:       http://localhost:{config.PORT}/api/temperature")
    print(f"   Breaker Status: http://localhost:{config.PORT}/api/breaker/status")
    print(f"   Health check:   http://localhost:{config.PORT}/health")
    print(f"\n💡 Share this link in your Telegram group!")
    print(f"   (Replace 'localhost' with your server's public IP/domain)")
    print("\nPress Ctrl+C to stop\n")

    # Start Flask server
    app.run(host=config.HOST, port=config.PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
