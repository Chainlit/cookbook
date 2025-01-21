#!/bin/bash

# Store PIDs for cleanup
declare -a pids

# Cleanup function to kill all background processes
cleanup() {
    echo -e "\nReceived SIGINT (Ctrl+C). Shutting down..."

    # Kill all stored PIDs
    for pid in "${pids[@]}"; do
        if kill -0 $pid 2>/dev/null; then
            echo "Stopping process $pid"
            kill $pid
            wait $pid 2>/dev/null
        fi
    done

    exit 0
}

# Set up trap for Ctrl+C
trap cleanup SIGINT

# Start first application (replace with your actual command)
echo "Starting uvicorn..."
uvicorn app:app --host 0.0.0.0 --port 9000 --root-path=/proxy &
pids+=($!)

# Start second application (replace with your actual command)
echo "Starting Caddy..."
caddy run &
pids+=($!)

echo "Both applications started. Press Ctrl+C to exit."
echo "Running processes: ${pids[*]}"

echo "Proxy server running on http://localhost:8080/proxy/chainlit"

# Wait for all background processes
wait
