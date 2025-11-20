"""
Resume with retry logic and better error handling
"""

import os
import requests
import time

def resume_download(url, filepath, max_retries=5):
    """Resume download with retry logic"""
    
    # Check current file
    if os.path.exists(filepath):
        current_size = os.path.getsize(filepath)
        print(f"✓ Found partial file: {current_size/1024/1024:.1f} MB")
    else:
        current_size = 0
        print("Starting new download...")
    
    print(f"URL: {url}")
    
    # Get total size
    try:
        print("Getting file info from server...")
        response = requests.head(url, allow_redirects=True, timeout=10)
        total_size = int(response.headers.get('content-length', 0))
        print(f"✓ Total size: {total_size/1024/1024:.1f} MB")
    except Exception as e:
        print(f"✗ Error getting file info: {e}")
        return False
    
    # Resume or start
    if current_size > 0:
        print(f"\n--- Resuming from {current_size/1024/1024:.1f} MB ---")
        remaining = total_size - current_size
        print(f"Remaining: {remaining/1024/1024:.1f} MB ({(remaining/total_size)*100:.1f}%)")
    else:
        print(f"\n--- Starting new download ---")
        remaining = total_size
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Download with retries
    retry_count = 0
    chunk_size = 1024 * 1024  # 1MB
    timeout = 30
    
    while retry_count < max_retries:
        try:
            print(f"\nAttempt {retry_count + 1}/{max_retries}...")
            
            # Set range header for resume
            headers = {'Range': f'bytes={current_size}-'} if current_size > 0 else {}
            
            # Open connection with longer timeout
            response = requests.get(url, headers=headers, stream=True, timeout=timeout)
            
            if response.status_code not in [200, 206]:
                print(f"⚠ Server returned status {response.status_code}")
                if response.status_code == 416:
                    # Requested range not satisfiable - file already complete
                    print("✓ File already complete!")
                    return True
                retry_count += 1
                time.sleep(5)
                continue
            
            # Download chunks
            mode = 'ab' if current_size > 0 else 'wb'
            downloaded_this_attempt = 0
            start_time = time.time()
            
            with open(filepath, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_this_attempt += len(chunk)
                        current_size += len(chunk)
                        
                        # Progress
                        elapsed = time.time() - start_time
                        speed = downloaded_this_attempt / elapsed if elapsed > 0 else 0
                        progress = (current_size / total_size) * 100
                        
                        print(f"  {progress:.1f}% ({current_size/1024/1024:.0f}/{total_size/1024/1024:.0f} MB) - {speed/1024/1024:.2f} MB/s", end='\r')
            
            print(f"\n✓ Download complete!")
            final_size = os.path.getsize(filepath)
            
            if final_size == total_size:
                print(f"✓ File verified: {final_size/1024/1024:.1f} MB matches server size")
                return True
            else:
                print(f"⚠ Size mismatch: got {final_size}, expected {total_size}")
                if final_size >= total_size:
                    print("✓ File is complete (may have extra data)")
                    return True
                else:
                    print("✗ File is still incomplete")
                    retry_count += 1
                    continue
                    
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 5 * retry_count
                print(f"\n✗ Connection error: {e}")
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"\n✗ Max retries reached")
                return False
        except KeyboardInterrupt:
            print(f"\n\nDownload paused at {current_size/1024/1024:.1f} MB")
            print("Run again to resume")
            return False
        except Exception as e:
            print(f"\n✗ Error: {e}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(5)
    
    return False

# Run it
if __name__ == "__main__":
    url = "http://34.11.64.176:9999/backup.tar.gz"
    filepath = os.path.expanduser("~/Downloads/NGK_Downloads/backup.tar.gz")
    
    print("=" * 60)
    print("BACKUP.TAR.GZ RESUME DOWNLOADER")
    print("=" * 60)
    
    success = resume_download(url, filepath, max_retries=3)
    
    print("\n" + "=" * 60)
    if success:
        print("✓ SUCCESS - File is complete!")
        print(f"Location: {filepath}")
    else:
        print("✗ Download incomplete or failed")
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"Current size: {size/1024/1024:.1f} MB")
    print("=" * 60)
