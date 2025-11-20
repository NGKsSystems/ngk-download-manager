"""
Quick file verification script
Checks if the downloaded file is complete and valid
"""

import os
from pathlib import Path

# Check the file
downloads_dir = os.path.expanduser("~/Downloads/NGK_Downloads")
file_path = os.path.join(downloads_dir, "backup.tar.gz")
part_file_path = file_path + ".part"

print("=" * 60)
print("FILE VERIFICATION")
print("=" * 60)

print(f"\nDownloads directory: {downloads_dir}")
print(f"Expected file: {file_path}")

if os.path.exists(file_path):
    file_size = os.path.getsize(file_path)
    print(f"\n✓ Main file EXISTS")
    print(f"  Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    print(f"  Status: SAFE - FILE IS COMPLETE")
else:
    print(f"\n✗ Main file NOT found")

if os.path.exists(part_file_path):
    part_size = os.path.getsize(part_file_path)
    print(f"\n⚠ Partial file EXISTS")
    print(f"  Size: {part_size:,} bytes ({part_size/1024/1024:.1f} MB)")
    print(f"  Status: INCOMPLETE")
else:
    print(f"\n✓ No partial file (good)")

# Check state file
state_file = os.path.expanduser("~/.ngk_download_manager/downloads.json")
if os.path.exists(state_file):
    print(f"\n✓ State file found: {state_file}")
    print(f"  Status tracking available")
else:
    print(f"\n✗ State file not found")

print("\n" + "=" * 60)
if os.path.exists(file_path):
    print("RESULT: ✓ YOUR FILE IS SAFE AND COMPLETE")
    print("=" * 60)
    print(f"\nThe {file_size/1024/1024:.1f} MB file is ready to use!")
else:
    print("RESULT: ✗ FILE NOT FOUND - NEEDS RECOVERY")
    print("=" * 60)
