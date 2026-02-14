#!/bin/bash
# Check which ports are available for YoLink Temperature Monitor

cd "$(dirname "$0")"

echo "Port Status Checker"
echo "==================="
echo ""

# List of ports to check
PORTS=(5000 5001 5002 5003 5004 8000 8001 8002 8080 9000)

echo "Checking ports..."
echo ""
printf "%-6s %-10s %s\n" "Port" "Status" "Process"
printf "%-6s %-10s %s\n" "----" "------" "-------"

for port in "${PORTS[@]}"; do
    if lsof -i :$port > /dev/null 2>&1; then
        process=$(lsof -i :$port -sTCP:LISTEN -Fn | grep '^n' | head -1 | sed 's/^n//')
        printf "%-6s %-10s %s\n" "$port" "IN USE" "$process"
    else
        printf "%-6s %-10s %s\n" "$port" "AVAILABLE" "-"
    fi
done

echo ""
echo "Current configuration:"
PORT=$(grep "^PORT" config.py 2>/dev/null | cut -d'=' -f2 | cut -d'#' -f1 | tr -d ' ')
if [ -n "$PORT" ]; then
    echo "  Configured port: $PORT"
    if lsof -i :$PORT > /dev/null 2>&1; then
        echo "  ⚠️  This port is IN USE - change PORT in config.py"
    else
        echo "  ✓ This port is AVAILABLE"
    fi
else
    echo "  ⚠️  Could not read port from config.py"
fi
