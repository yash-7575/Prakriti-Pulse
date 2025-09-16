@echo off
echo.
echo ========================================
echo    Prakriti Pulse - Flask Application
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting the application...
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python run.py
pause
