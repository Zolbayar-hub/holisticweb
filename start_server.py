#!/usr/bin/env python
import subprocess
import sys
import os

# Change to the project directory
os.chdir('/Users/zoloo/project_v2/holisticweb')

# Set environment variables
os.environ['FLASK_APP'] = 'flask_app.py'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'True'

print("Starting Flask development server...")
print("Admin credentials:")
print("  Username: admin")
print("  Email: admin@example.com")
print("  Password: admin123")
print("\nAccess the application at: http://127.0.0.1:5000")
print("Admin panel at: http://127.0.0.1:5000/admin/")
print("\nPress Ctrl+C to stop the server")

try:
    # Start the Flask app
    subprocess.run([sys.executable, 'flask_app.py'], check=True)
except KeyboardInterrupt:
    print("\nServer stopped.")
