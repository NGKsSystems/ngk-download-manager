"""
Test the mobile app on desktop before building for Android
"""

import sys
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mobile_app import NGKDownloadApp
    print("Starting NGK's Download Manager (Mobile Version)...")
    print("This is running the mobile interface on desktop for testing.")
    print("Use touch gestures or mouse to interact.")
    
    NGKDownloadApp().run()
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are available.")
    print("You may need to install dependencies:")
    print("pip install kivy requests yt-dlp pillow")
    
except Exception as e:
    print(f"Error running app: {e}")
    import traceback
    traceback.print_exc()