"""
Deep file verification - checks if tar.gz is actually valid
"""

import os
import tarfile
from pathlib import Path

file_path = os.path.expanduser("~/Downloads/NGK_Downloads/backup.tar.gz")

print("=" * 60)
print("DEEP FILE VERIFICATION")
print("=" * 60)

print(f"\nFile: {file_path}")
print(f"Exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    file_size = os.path.getsize(file_path)
    print(f"Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    
    # Try to open as tar.gz
    print("\n--- Checking if valid TAR.GZ ---")
    try:
        with tarfile.open(file_path, 'r:gz') as tar:
            members = tar.getmembers()
            print(f"✓ Valid TAR.GZ file!")
            print(f"  Contains: {len(members)} files/folders")
            
            # Show first few files
            print(f"\n  First 10 items:")
            for i, member in enumerate(members[:10]):
                print(f"    {i+1}. {member.name} ({member.size} bytes)")
            
            if len(members) > 10:
                print(f"    ... and {len(members) - 10} more items")
            
            # Check total size
            total_size = sum(m.size for m in members)
            print(f"\n  Total extracted size: {total_size:,} bytes ({total_size/1024/1024/1024:.1f} GB)")
            
    except tarfile.ReadError as e:
        print(f"✗ NOT a valid TAR.GZ file!")
        print(f"  Error: {e}")
    except Exception as e:
        print(f"✗ Error reading file!")
        print(f"  Error: {e}")
else:
    print("File not found!")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
