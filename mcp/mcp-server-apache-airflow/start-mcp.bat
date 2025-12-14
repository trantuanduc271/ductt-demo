@echo off
cd /d "%~dp0"
echo Starting Airflow MCP Server...
echo.

set AIRFLOW_HOST=https://airflow.ducttdevops.com
set AIRFLOW_USERNAME=admin
set AIRFLOW_PASSWORD=admin

echo Environment:
echo   AIRFLOW_HOST=%AIRFLOW_HOST%
echo   AIRFLOW_USERNAME=%AIRFLOW_USERNAME%
echo.

echo Running MCP server on http://0.0.0.0:8080/mcp
echo Press Ctrl+C to stop
echo.

uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080

pause
