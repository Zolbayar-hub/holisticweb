#!/usr/bin/env python3
"""
Simple script to start Flask app with debugging
"""

import os
import sys
sys.path.append(os.getcwd())

from flask_app import app

if __name__ == "__main__":
    print("🚀 Starting Flask application...")
    print("📍 URL: http://localhost:5000")
    print("📍 Booking page: http://localhost:5000/booking")
    print("💡 Check the console output for any errors")
    print()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        import traceback
        traceback.print_exc()
