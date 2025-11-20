"""
Find all non-ASCII characters in filenames
"""
import os

download_dir = r"C:\Users\suppo\Downloads\NGK_Downloads"

print("🔍 Analyzing all characters in filenames...")

for filename in os.listdir(download_dir):
    unusual_chars = []
    for i, char in enumerate(filename):
        # Check for non-basic ASCII or quotes
        if ord(char) > 127 or char in ['"', "'", '"', '"', '`']:
            unusual_chars.append((i, char, ord(char), hex(ord(char))))
    
    if unusual_chars:
        print(f"\n📁 {filename}")
        for pos, char, decimal, hexval in unusual_chars:
            print(f"   Pos {pos}: '{char}' (decimal: {decimal}, hex: {hexval})")
    elif any(suspect in filename for suspect in ['"', "'", '`']):
        print(f"\n📁 Contains quote-like char: {filename}")
        
print("\n" + "="*50)
print("Raw filename bytes:")
for filename in os.listdir(download_dir)[:3]:  # First 3 files
    print(f"\n{filename}")
    print(f"Bytes: {filename.encode('utf-8')}")
    print(f"Repr:  {repr(filename)}")

input("\nPress Enter to exit...")