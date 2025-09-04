"""
HolisticWeb Flask Application
A modern, organized Flask application for holistic therapy services

This is the main application entry point that uses the application factory pattern
for better organization and testing capabilities.
"""

import os
from app_factory import create_app
from utils.scheduler import init_scheduler


# Create application instance
app = create_app()

# Initialize SMS reminder scheduler
if __name__ == '__main__':
    with app.app_context():
        # Initialize SMS reminder scheduler
        try:
            scheduler = init_scheduler(app)
        except Exception as e:
            print(f"Failed to initialize scheduler: {e}")

    # Run the application
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=app.config['DEBUG'],
        threaded=True
    )

