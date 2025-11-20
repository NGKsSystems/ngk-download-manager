"""
Check download state to see what the expected size should be
"""

import os
import json

state_file = os.path.expanduser("~/.ngk_download_manager/downloads.json")

print("=" * 60)
print("DOWNLOAD STATE CHECK")
print("=" * 60)

if os.path.exists(state_file):
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    print(f"\nFound {len(state)} downloads in state file:\n")
    
    for download_id, info in state.items():
        print(f"URL: {info['url']}")
        print(f"File: {info['filepath']}")
        print(f"Total size: {info['total_size']:,} bytes ({info['total_size']/1024/1024:.1f} MB)")
        print(f"Downloaded: {info['downloaded_size']:,} bytes ({info['downloaded_size']/1024/1024:.1f} MB)")
        print(f"Chunks: {info['chunks']}")
        print(f"Status: {info['status']}")
        print(f"Started: {info['started_at']}")
        print(f"Last update: {info.get('last_update', 'N/A')}")
        
        # Check actual file
        filepath = info['filepath']
        if os.path.exists(filepath):
            actual_size = os.path.getsize(filepath)
            print(f"\nActual file size: {actual_size:,} bytes ({actual_size/1024/1024:.1f} MB)")
            missing = info['total_size'] - actual_size
            print(f"Missing: {missing:,} bytes ({missing/1024/1024:.1f} MB)")
            if missing > 0:
                print(f"⚠️  INCOMPLETE - Need to download {missing:,} more bytes")
        print()
else:
    print("No state file found!")

print("=" * 60)
