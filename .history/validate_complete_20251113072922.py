"""
Validate the backup.tar.gz file - check if it's a valid tar archive
"""

import os
import tarfile
import hashlib

filepath = os.path.expanduser("~/Downloads/NGK_Downloads/backup.tar.gz")

print("=" * 70)
print("FULL FILE VALIDATION - backup.tar.gz")
print("=" * 70)

if not os.path.exists(filepath):
    print(f"✗ File not found: {filepath}")
    exit(1)

# Get file size
file_size = os.path.getsize(filepath)
print(f"\n✓ File found")
print(f"  Size: {file_size:,} bytes ({file_size/1024/1024/1024:.2f} GB)")

# Try to extract and verify tar.gz
print("\n--- Validating TAR.GZ Archive ---")
try:
    with tarfile.open(filepath, 'r:gz') as tar:
        members = tar.getmembers()
        print(f"✓ Valid TAR.GZ file!")
        print(f"  Contains: {len(members)} files/folders")
        
        # Show summary
        total_extracted_size = sum(m.size for m in members)
        print(f"  Total extracted size: {total_extracted_size:,} bytes ({total_extracted_size/1024/1024/1024:.2f} GB)")
        
        # List top-level contents
        print(f"\n  Top-level contents:")
        top_level = set()
        for member in members:
            parts = member.name.split('/')
            if parts[0]:
                top_level.add(parts[0])
        
        for i, item in enumerate(sorted(top_level)[:10], 1):
            print(f"    {i}. {item}")
        
        if len(top_level) > 10:
            print(f"    ... and {len(top_level) - 10} more items")
        
        print(f"\n✓ Archive is VALID and COMPLETE!")
        
except tarfile.ReadError as e:
    print(f"✗ Invalid TAR.GZ: {e}")
    exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

print("\n" + "=" * 70)
print("RESULT: ✓ FILE IS COMPLETE AND VALID")
print("=" * 70)
print(f"\nFile is ready to extract at:")
print(f"  {filepath}")
