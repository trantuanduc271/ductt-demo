# Start Airflow MCP Server (supports basic auth)
# Run this from: mcp\mcp-server-apache-airflow directory

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Airflow MCP Server Startup" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Set environment variables
$env:AIRFLOW_HOST = "https://airflow.ducttdevops.com"
$env:AIRFLOW_USERNAME = "admin"
$env:AIRFLOW_PASSWORD = "admin"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  AIRFLOW_HOST: $env:AIRFLOW_HOST"
Write-Host "  AIRFLOW_USERNAME: $env:AIRFLOW_USERNAME"
Write-Host "  AIRFLOW_PASSWORD: ****`n"

Write-Host "Starting MCP server on http://0.0.0.0:8080/mcp" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

# Start the server
uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080
