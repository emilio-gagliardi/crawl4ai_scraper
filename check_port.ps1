# check_port.ps1 - Script to check if a port is already in use
# Usage: .\check_port.ps1 <port_number>

param (
    [Parameter(Mandatory=$true)]
    [int]$Port
)

# More reliable method to check if a port is in use by trying to create a listener
try {
    # Create a TCP listener on the specified port
    $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $Port)
    
    # Try to start the listener
    $listener.Start()
    
    # If we get here, the port is available
    $listener.Stop()
    Write-Host "Port $Port is available"
    exit 0
} catch {
    # If we get an exception, the port is in use
    Write-Host "Error: Port $Port is already in use by another process"
    
    # Try to get details about the process using the port
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connections) {
            Write-Host "Details of the process using port $($Port):"
            foreach ($conn in $connections) {
                $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "PID: $($process.Id)"
                    Write-Host "Process Name: $($process.ProcessName)"
                    Write-Host "Command Line: $($process.Path)"
                }
            }
        } else {
            Write-Host "Could not determine which process is using port $Port"
        }
    } catch {
        Write-Host "Error getting process details: $_"
    }
    
    exit 1
}