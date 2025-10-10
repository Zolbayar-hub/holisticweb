#!/usr/bin/env python3
"""
Test script to verify audio setup and download a sample relaxing music file
"""
import os
import urllib.request
import sys

def download_sample_music():
    """Download a sample relaxing music file for testing"""
    
    static_path = "/Users/zoloo/project_v2/website/holisticweb/static"
    audio_file = os.path.join(static_path, "calm-music.mp3")
    
    if os.path.exists(audio_file):
        print(f"✅ Audio file already exists: {audio_file}")
        return True
    
    print("🔍 Searching for free sample relaxing music...")
    
    # List of free sample audio URLs (very short samples for testing)
    sample_urls = [
        "https://www.soundjay.com/misc/sounds-1/bell-ringing-05.mp3",  # Short bell sound
        "https://sample-videos.com/zip/10/mp3/mp3-30s/SampleAudio_0.4mb_mp3.mp3"  # Sample audio
    ]
    
    for i, url in enumerate(sample_urls):
        try:
            print(f"📥 Trying to download sample {i+1}...")
            urllib.request.urlretrieve(url, audio_file)
            print(f"✅ Downloaded sample audio to: {audio_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to download from {url}: {e}")
            continue
    
    print("❌ Could not download sample audio. Please add your own calm-music.mp3 file.")
    return False

def check_audio_setup():
    """Check if audio file exists and provide setup instructions"""
    
    static_path = "/Users/zoloo/project_v2/website/holisticweb/static"
    audio_file = os.path.join(static_path, "calm-music.mp3")
    
    print("🎵 AUDIO SETUP CHECKER")
    print("=" * 50)
    
    # Check if static directory exists
    if not os.path.exists(static_path):
        print(f"❌ Static directory not found: {static_path}")
        return False
    
    print(f"✅ Static directory exists: {static_path}")
    
    # Check if audio file exists
    if os.path.exists(audio_file):
        file_size = os.path.getsize(audio_file)
        print(f"✅ Audio file found: {audio_file}")
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        if file_size < 1000:  # Less than 1KB probably not a real audio file
            print("⚠️  Warning: File seems very small, might be corrupted")
        
        return True
    else:
        print(f"❌ Audio file not found: {audio_file}")
        print("\n📋 TO FIX THIS:")
        print("1. Find a relaxing MP3 audio file")
        print("2. Rename it to 'calm-music.mp3'")
        print(f"3. Copy it to: {audio_file}")
        print("\n🌐 Free music sources:")
        print("- https://freemusicarchive.org/")
        print("- https://www.zapsplat.com/")
        print("- https://pixabay.com/music/")
        
        return False

if __name__ == "__main__":
    print("🎶 Background Music Setup Helper")
    print("=" * 50)
    
    if not check_audio_setup():
        response = input("\n❓ Would you like to try downloading a sample audio file? (y/n): ")
        if response.lower() in ['y', 'yes']:
            download_sample_music()
        else:
            print("\n📝 Please add your calm-music.mp3 file manually.")
    
    print("\n🔍 Next steps:")
    print("1. Start your Flask application")
    print("2. Open your website")
    print("3. Press F12 to open Developer Tools")
    print("4. Click the 🎵 button and check Console for debug messages")
