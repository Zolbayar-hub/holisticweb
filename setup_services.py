#!/usr/bin/env python3
"""
Script to populate the database with sample services for the booking system.
Run this script to add initial services to your database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_app import app
from db import db
from db.models import Service

def create_sample_services():
    """Create sample services for the booking system."""
    
    services_data = [
        {
            'name': 'Yoga Session',
            'description': 'Relaxing yoga session to restore balance and flexibility. Perfect for beginners and experienced practitioners.',
            'price': 75.0,
            'duration': 60
        },
        {
            'name': 'Guided Meditation',
            'description': 'Deep meditation practice for mental clarity and peace. Learn mindfulness techniques.',
            'price': 50.0,
            'duration': 45
        },
        {
            'name': 'Reiki Healing',
            'description': 'Energy healing session for physical and emotional wellness. Experience the power of healing touch.',
            'price': 90.0,
            'duration': 60
        },
        {
            'name': 'Holistic Massage',
            'description': 'Therapeutic massage combining multiple healing techniques for deep relaxation and healing.',
            'price': 120.0,
            'duration': 90
        },
        {
            'name': 'Aromatherapy Session',
            'description': 'Essential oils therapy to promote relaxation and healing through natural scents.',
            'price': 65.0,
            'duration': 50
        },
        {
            'name': 'Crystal Healing',
            'description': 'Healing session using the power of crystals to balance your energy centers.',
            'price': 80.0,
            'duration': 55
        }
    ]
    
    with app.app_context():
        # Check if services already exist
        existing_services = Service.query.all()
        if existing_services:
            print(f"Found {len(existing_services)} existing services:")
            for service in existing_services:
                print(f"  - {service.name} (${service.price}, {service.duration} min)")
            
            choice = input("\nDo you want to add more services anyway? (y/N): ").lower().strip()
            if choice != 'y':
                print("Skipping service creation.")
                return
        
        print("Creating sample services...")
        
        created_count = 0
        for service_data in services_data:
            # Check if service with this name already exists
            existing = Service.query.filter_by(name=service_data['name']).first()
            if existing:
                print(f"  - Skipping '{service_data['name']}' (already exists)")
                continue
            
            service = Service(
                name=service_data['name'],
                description=service_data['description'],
                price=service_data['price'],
                duration=service_data['duration']
            )
            
            db.session.add(service)
            created_count += 1
            print(f"  + Added '{service_data['name']}'")
        
        try:
            db.session.commit()
            print(f"\nSuccessfully created {created_count} new services!")
            
            # Display all services
            all_services = Service.query.all()
            print(f"\nAll services in database ({len(all_services)} total):")
            for service in all_services:
                print(f"  - {service.name}: ${service.price} ({service.duration} min)")
                print(f"    {service.description}")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error creating services: {e}")

if __name__ == '__main__':
    print("=== Holistic Web Services Setup ===")
    create_sample_services()
    print("\nDone! You can now use the booking system with these services.")
