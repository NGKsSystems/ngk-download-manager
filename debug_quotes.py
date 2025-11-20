"""
Debug script to check quote characters
"""
import os
import unicodedata

download_dir = r"C:\Users\suppo\Downloads\NGK_Downloads"

print("🔍 Analyzing filenames for quote characters...")

quote_chars = ['"', "'", '"', '"']

for filename in os.listdir(download_dir):
    if any(c in filename for c in quote_chars):
        print(f"\n📁 File: {filename}")
        for i, char in enumerate(filename):
            if char in quote_chars:
                print(f"   Position {i}: '{char}' (Unicode: U+{ord(char):04X}, Name: {unicodedata.name(char, 'UNKNOWN')})")

input("\nPress Enter to exit...")