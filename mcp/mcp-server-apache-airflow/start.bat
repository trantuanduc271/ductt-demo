@echo off
REM Start Airflow MCP Server with Basic Authentication
REM This uses the mcp-server-apache-airflow in your repo

cd /d %~dp0

echo ================================
echo Starting Airflow MCP Server
echo ================================
echo.

REM Set Airflow connection details
set AIRFLOW_HOST=https://airflow.ducttdevops.com
set AIRFLOW_USERNAME=admin
set AIRFLOW_PASSWORD=admin

echo Configuration:
echo   AIRFLOW_HOST: %AIRFLOW_HOST%
echo   AIRFLOW_USERNAME: %AIRFLOW_USERNAME%
echo.
echo Starting MCP server on http://0.0.0.0:8080/mcp
echo Press Ctrl+C to stop
echo.

REM Start the MCP server
uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start MCP server
    echo Check that you're in the mcp-server-apache-airflow directory
    pause
)
