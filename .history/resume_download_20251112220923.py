"""
Resume the incomplete backup.tar.gz download
Uses the HTTP Range header to continue from where it left off
"""

import os
import requests
import time

# Download info
url = "http://34.11.64.176:9999/backup.tar.gz"
filepath = os.path.expanduser("~/Downloads/NGK_Downloads/backup.tar.gz")

# Check current file
if os.path.exists(filepath):
    current_size = os.path.getsize(filepath)
    print(f"Found partial file: {current_size:,} bytes ({current_size/1024/1024:.1f} MB)")
else:
    current_size = 0
    print("No partial file found - will start from beginning")

print(f"\nResuming download from byte {current_size:,}...")
print(f"URL: {url}")

# Get total size from server
try:
    response = requests.head(url, allow_redirects=True, timeout=10)
    total_size = int(response.headers.get('content-length', 0))
    print(f"Total file size on server: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    
    # Check if server supports resume
    if 'accept-ranges' in response.headers:
        print(f"✓ Server supports resume (HTTP Range)")
    else:
        print(f"⚠ Server may not support resume")
    
except Exception as e:
    print(f"Error getting file info: {e}")
    exit(1)

# Resume download
print(f"\n--- Starting Resume Download ---")
print(f"Continuing from: {current_size:,} bytes")
print(f"Remaining: {total_size - current_size:,} bytes ({(total_size-current_size)/1024/1024:.1f} MB)")

headers = {'Range': f'bytes={current_size}-'}

try:
    response = requests.get(url, headers=headers, stream=True, timeout=30)
    
    if response.status_code == 206:
        print("✓ Server accepted resume request (HTTP 206)")
    elif response.status_code == 200:
        print("⚠ Server returned full file (HTTP 200) - will overwrite")
        current_size = 0
    else:
        print(f"✗ Unexpected status: {response.status_code}")
        exit(1)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Download with resume
    mode = 'ab' if current_size > 0 else 'wb'
    downloaded = 0
    start_time = time.time()
    chunk_size = 1024 * 1024  # 1MB chunks
    
    with open(filepath, mode) as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                
                # Progress update
                elapsed = time.time() - start_time
                speed = downloaded / elapsed if elapsed > 0 else 0
                progress = ((current_size + downloaded) / total_size) * 100
                
                print(f"  {progress:.1f}% - {downloaded/1024/1024:.0f} MB downloaded - {speed/1024/1024:.1f} MB/s", end='\r')
    
    print(f"\n✓ Download complete!")
    final_size = os.path.getsize(filepath)
    print(f"Final file size: {final_size:,} bytes ({final_size/1024/1024:.1f} MB)")
    
    if final_size == total_size:
        print("✓ File is complete and matches server size!")
    else:
        print(f"⚠ Size mismatch: expected {total_size}, got {final_size}")

except KeyboardInterrupt:
    print("\n\nDownload paused. Run again to resume.")
except Exception as e:
    print(f"\n✗ Error: {e}")
