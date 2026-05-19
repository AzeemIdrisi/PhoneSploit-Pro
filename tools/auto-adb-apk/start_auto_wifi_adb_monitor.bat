@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File ".\auto_wifi_adb_monitor.ps1"
