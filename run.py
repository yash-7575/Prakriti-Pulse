#!/usr/bin/env python3
"""
Flask application runner for Prakriti Pulse
"""

from app import app

if __name__ == '__main__':
    print("🌿 Starting Prakriti Pulse Flask Application...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
