# Start MCP Server for Airflow Bot
# This script starts the Airflow MCP server with correct environment variables

Write-Host "🚀 Starting Airflow MCP Server..." -ForegroundColor Cyan

# Check if .env file exists in agent directory
if (Test-Path "..\..\agent\.env") {
    Write-Host "📄 Loading environment from agent/.env" -ForegroundColor Green
    Get-Content "..\..\agent\.env" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            if ($name -in @("AIRFLOW_HOST", "AIRFLOW_USERNAME", "AIRFLOW_PASSWORD")) {
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
                if ($name -eq "AIRFLOW_PASSWORD") {
                    Write-Host "   $name=****" -ForegroundColor Yellow
                } else {
                    Write-Host "   $name=$value" -ForegroundColor Yellow
                }
            }
        }
    }
} else {
    Write-Host "⚠️  No .env file found, using defaults" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting MCP server on http://0.0.0.0:8080/mcp" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Cyan
Write-Host ""

uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080
