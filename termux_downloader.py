#!/usr/bin/env python3
"""
Simple command-line downloader for Termux
No GUI needed - just works!
"""

import sys
import os

def main():
    print("=" * 50)
    print("NGK's Download Manager - Termux Edition")
    print("=" * 50)
    print()
    
    # Get URL from user
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter URL to download: ").strip()
    
    if not url:
        print("No URL provided!")
        return
    
    # Get download location
    download_path = os.path.expanduser("~/storage/downloads")
    if not os.path.exists(download_path):
        download_path = os.path.expanduser("~/downloads")
        os.makedirs(download_path, exist_ok=True)
    
    print(f"\nDownloading to: {download_path}")
    print(f"URL: {url}\n")
    
    # Use yt-dlp for everything (handles YouTube and direct downloads)
    cmd = f'yt-dlp -o "{download_path}/%(title)s.%(ext)s" "{url}"'
    
    print("Starting download...\n")
    os.system(cmd)
    
    print("\n" + "=" * 50)
    print("Download complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
