"""
Quick test for Hugging Face URL parsing fix
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from huggingface_downloader import HuggingFaceDownloader

def test_hf_url_parsing():
    """Test the fixed HF URL parsing"""
    hf_downloader = HuggingFaceDownloader()
    
    test_urls = [
        "https://huggingface.co/suno/bark/resolve/main/fine_2.pt",
        "https://huggingface.co/microsoft/DialoGPT-medium",
        "https://huggingface.co/datasets/squad",
        "https://huggingface.co/spaces/huggingface/CodeBERTa"
    ]
    
    print("Testing Hugging Face URL Parsing:")
    print("=" * 50)
    
    for url in test_urls:
        result = hf_downloader._parse_hf_url(url)
        print(f"\nURL: {url}")
        if result:
            print(f"  ✓ Repo ID: {result['repo_id']}")
            print(f"  ✓ Type: {result['repo_type']}")
            print(f"  ✓ Filename: {result.get('filename', 'None (full repo)')}")
        else:
            print(f"  ✗ Failed to parse")
    
    print("\n" + "=" * 50)
    print("URL parsing test completed!")

if __name__ == "__main__":
    test_hf_url_parsing()