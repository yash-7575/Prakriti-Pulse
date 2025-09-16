@echo off
echo.
echo ========================================
echo    Prakriti Pulse Database Setup
echo ========================================
echo.
echo This script will set up the MySQL database for Prakriti Pulse
echo.
echo Prerequisites:
echo 1. MySQL server must be running
echo 2. MySQL root user should have no password (or update the script)
echo 3. Python must be installed
echo.
pause
echo.
echo Installing required packages...
pip install mysql-connector-python python-dotenv
echo.
echo Setting up database...
python setup_database.py
echo.
echo Database setup complete!
echo.
pause
