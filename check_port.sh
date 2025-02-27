#!/bin/bash

# check_port.sh - Script to check if a port is already in use
# Usage: ./check_port.sh <port_number>

if [ $# -eq 0 ]; then
    echo "Error: Port number not provided"
    echo "Usage: $0 <port_number>"
    exit 1
fi

PORT=$1

# More reliable method to check if a port is in use
(echo > /dev/tcp/127.0.0.1/$PORT) >/dev/null 2>&1
if [ $? -eq 0 ]; then
    # If we can connect to the port, it's in use
    echo "Error: Port $PORT is already in use by another process"
    echo "Details of the process using port $PORT:"
    
    # Get the PID of the process using the port
    PID=$(lsof -i :$PORT -t 2>/dev/null)
    
    if [ -n "$PID" ]; then
        echo "PID: $PID"
        echo "Process details:"
        ps -p $PID -o pid,ppid,user,cmd
    else
        echo "Could not determine the process ID"
        echo "Port usage details:"
        netstat -tuln | grep ":$PORT "
    fi
    
    exit 1
else
    # If we can't connect, the port is available
    echo "Port $PORT is available"
    exit 0
fi