"""
Test script to verify resume functionality
Simulates an interrupted download and tests resumption
"""

import os
import sys
import time
from download_state_manager import DownloadStateManager
from download_manager import DownloadManager

def test_resume():
    """Test resume functionality"""
    
    print("=" * 60)
    print("DOWNLOAD RESUME TEST")
    print("=" * 60)
    
    # Create test destination
    test_dir = os.path.expanduser("~/Downloads/NGK_DL_Test")
    os.makedirs(test_dir, exist_ok=True)
    
    # Test file info
    test_url = "http://34.11.64.176:9999/backup.tar.gz"
    test_file = os.path.join(test_dir, "backup.tar.gz")
    
    print(f"\nTest URL: {test_url}")
    print(f"Test File: {test_file}")
    
    # Initialize managers
    dm = DownloadManager()
    sm = DownloadStateManager()
    
    print("\n--- STEP 1: Check resumable downloads ---")
    resumable = dm.get_resumable_downloads()
    print(f"Found {len(resumable)} resumable downloads:")
    for dl in resumable:
        print(f"  • {os.path.basename(dl['filepath'])}")
        print(f"    Progress: {dl['progress']:.1f}% ({dl['partial_size']} / {dl['total_size']} bytes)")
    
    print("\n--- STEP 2: Get file info ---")
    file_info = dm.get_file_info(test_url)
    if file_info:
        print(f"✓ File found on server")
        print(f"  Filename: {file_info['filename']}")
        print(f"  Size: {file_info['size_formatted']}")
        print(f"  Supports resume: {file_info['supports_resume']}")
    else:
        print("✗ Could not get file info")
        return
    
    print("\n--- STEP 3: Starting test download (will interrupt after 5 chunks) ---")
    
    chunks_to_download = 0
    max_chunks = 5
    
    def progress_callback(info):
        nonlocal chunks_to_download
        print(f"  {info['status']}: {info['progress']} ({info['speed']})")
        chunks_to_download += 1
        if chunks_to_download >= max_chunks:
            print(f"\n>>> SIMULATING INTERRUPT AFTER {max_chunks} CHUNKS <<<\n")
            raise KeyboardInterrupt("Simulated interrupt")
    
    try:
        dm.download(test_url, test_file, progress_callback=progress_callback)
    except KeyboardInterrupt:
        print("Download interrupted as expected")
    
    # Check partial file
    if os.path.exists(test_file + '.part'):
        partial_size = os.path.getsize(test_file + '.part')
        print(f"\n--- STEP 4: Partial file check ---")
        print(f"✓ Partial file exists: {test_file}.part")
        print(f"  Size: {partial_size} bytes ({partial_size/1024/1024:.1f} MB)")
    
    # Check download state
    download_id = f"{test_url}_{test_file}"
    dl_state = sm.get_download_info(download_id)
    if dl_state:
        print(f"\n--- STEP 5: Download state saved ---")
        print(f"✓ State found for download")
        print(f"  URL: {dl_state['url']}")
        print(f"  Downloaded: {dl_state['downloaded_size']} bytes")
        print(f"  Total: {dl_state['total_size']} bytes")
        print(f"  Chunks: {dl_state['chunks']}")
        print(f"  Status: {dl_state['status']}")
    
    print("\n--- STEP 6: Check resumable downloads again ---")
    resumable = dm.get_resumable_downloads()
    print(f"Found {len(resumable)} resumable downloads:")
    for dl in resumable:
        print(f"  ✓ {os.path.basename(dl['filepath'])}")
        print(f"    Progress: {dl['progress']:.1f}%")
        print(f"    Partial size: {dl['partial_size']} bytes")
        print(f"    Total size: {dl['total_size']} bytes")
        print(f"    Can resume: YES")
    
    print("\n" + "=" * 60)
    print("RESUME TEST COMPLETE")
    print("=" * 60)
    print("\nTo test resume:")
    print("1. Close the download manager app")
    print("2. Restart it")
    print("3. You should see a dialog asking to resume the partial download")
    print("4. Click 'Yes' to resume from where it left off")
    print(f"\nPartial file saved at: {test_file}.part")

if __name__ == "__main__":
    test_resume()
