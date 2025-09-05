#!/usr/bin/env python3
"""
Test script for contact form functionality
"""

import requests
import json

def test_contact_form():
    """Test the contact form submission"""
    url = "http://127.0.0.1:5000/contact"
    
    # Test data
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'message': 'This is a test message from the contact form.'
    }
    
    print("Testing contact form submission...")
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, data=data)
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message', 'No message')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the Flask application. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_contact_form()
