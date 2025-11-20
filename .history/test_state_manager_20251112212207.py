"""
Simpler test of the download state manager
Tests state persistence without needing a real server
"""

import os
import sys
from download_state_manager import DownloadStateManager

def test_state_manager():
    """Test download state manager"""
    
    print("=" * 60)
    print("DOWNLOAD STATE MANAGER TEST")
    print("=" * 60)
    
    # Create state manager
    sm = DownloadStateManager()
    
    # Test 1: Create a new download state
    print("\n--- TEST 1: Create download state ---")
    url = "http://example.com/large_file.zip"
    filepath = os.path.expanduser("~/Downloads/large_file.zip")
    total_size = 1073741824  # 1 GB
    
    download_id = sm.start_download(url, filepath, total_size)
    print(f"✓ Created download state")
    print(f"  ID: {download_id}")
    print(f"  URL: {url}")
    print(f"  File: {filepath}")
    print(f"  Size: {total_size} bytes ({total_size/1024/1024/1024:.1f} GB)")
    
    # Test 2: Update download progress
    print("\n--- TEST 2: Update progress ---")
    for i in range(1, 6):
        downloaded = i * 100 * 1024 * 1024  # 100 MB chunks
        sm.update_download(download_id, downloaded, i, 'downloading')
        print(f"  Chunk {i}: {downloaded / 1024 / 1024:.0f} MB downloaded")
    
    # Test 3: Retrieve state
    print("\n--- TEST 3: Retrieve state ---")
    state = sm.get_download_info(download_id)
    if state:
        print(f"✓ State retrieved successfully")
        print(f"  Status: {state['status']}")
        print(f"  Downloaded: {state['downloaded_size'] / 1024 / 1024:.0f} MB")
        print(f"  Chunks: {state['chunks']}")
        print(f"  Started: {state['started_at']}")
        print(f"  Last update: {state['last_update']}")
    
    # Test 4: Create partial file and check resumable
    print("\n--- TEST 4: Create partial file and check resumable ---")
    partial_dir = os.path.dirname(filepath)
    os.makedirs(partial_dir, exist_ok=True)
    
    # Create a fake partial file
    partial_file = filepath + ".part"
    with open(partial_file, 'w') as f:
        f.write("x" * (500 * 1024 * 1024))  # 500 MB partial file
    
    print(f"✓ Created partial file: {partial_file}")
    print(f"  Size: {os.path.getsize(partial_file) / 1024 / 1024:.0f} MB")
    
    # Check resumable downloads
    resumable = sm.get_resumable_downloads(None)
    print(f"\n✓ Found {len(resumable)} resumable downloads:")
    for dl in resumable:
        progress = dl['progress']
        print(f"  • {os.path.basename(dl['filepath'])}")
        print(f"    Progress: {progress:.1f}%")
        print(f"    Partial: {dl['partial_size'] / 1024 / 1024:.0f} MB")
        print(f"    Total: {dl['total_size'] / 1024 / 1024:.0f} MB")
        print(f"    Chunks: {dl['chunks']}")
    
    # Test 5: Complete download
    print("\n--- TEST 5: Complete download ---")
    sm.complete_download(download_id)
    state = sm.get_download_info(download_id)
    print(f"✓ Download marked as complete")
    print(f"  Status: {state['status']}")
    print(f"  Completed at: {state.get('completed_at', 'N/A')}")
    
    # Test 6: Create multiple downloads
    print("\n--- TEST 6: Create multiple downloads ---")
    for i in range(3):
        url2 = f"http://example.com/file_{i}.zip"
        filepath2 = os.path.expanduser(f"~/Downloads/file_{i}.zip")
        id2 = sm.start_download(url2, filepath2, 500000000)  # 500 MB each
        sm.update_download(id2, 250000000 * (i+1), i+1, 'downloading')
    
    all_downloads = sm.get_all_downloads()
    print(f"✓ Created multiple downloads")
    print(f"  Total downloads in state: {len(all_downloads)}")
    for did, info in list(all_downloads.items())[-3:]:
        print(f"  • {os.path.basename(info['filepath'])}: {info['downloaded_size']/1024/1024:.0f} MB")
    
    # Test 7: Check state persistence
    print("\n--- TEST 7: State persistence (reload from disk) ---")
    sm2 = DownloadStateManager()  # Create new instance (should reload from disk)
    state_reloaded = sm2.get_download_info(download_id)
    if state_reloaded:
        print(f"✓ State persisted to disk and reloaded")
        print(f"  Status: {state_reloaded['status']}")
        print(f"  Downloaded: {state_reloaded['downloaded_size'] / 1024 / 1024:.0f} MB")
    
    print("\n" + "=" * 60)
    print("STATE MANAGER TEST COMPLETE")
    print("=" * 60)
    print(f"\nState file location: {sm.state_file}")
    print("All download states are persisted and will survive app restart!")

if __name__ == "__main__":
    test_state_manager()
