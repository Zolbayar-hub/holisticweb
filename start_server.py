#!/usr/bin/env python3
"""
Start the Flask application for Serenity Wellness Studio
Run this script to start the web server
"""

import os
import sys
from flask_app import app

if __name__ == '__main__':
    print("🌟 Starting Serenity Wellness Studio Web Application")
    print("=" * 60)
    print(f"🌐 Server will be available at: http://127.0.0.1:5000/")

    print(f"🛠️  Admin panel available at: http://127.0.0.1:5000/web_admin/")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
