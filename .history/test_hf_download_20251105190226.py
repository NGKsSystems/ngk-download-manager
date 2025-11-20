"""
Test the fixed Hugging Face downloader
"""

import sys
import os
import tempfile
import shutil

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from huggingface_downloader import HuggingFaceDownloader

def test_progress_callback(progress_info):
    """Test progress callback"""
    print(f"Progress: {progress_info['filename']} - {progress_info['progress']} - {progress_info['speed']} - {progress_info['status']}")

def test_hf_download():
    """Test Hugging Face download with progress"""
    print("Testing Hugging Face Download with Progress")
    print("=" * 50)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Test download directory: {temp_dir}")
    
    try:
        # Initialize downloader
        hf_downloader = HuggingFaceDownloader()
        
        # Test URL parsing
        test_url = "https://huggingface.co/suno/bark/resolve/main/fine_2.pt"
        parsed = hf_downloader._parse_hf_url(test_url)
        
        print(f"\nURL: {test_url}")
        print(f"Parsed: {parsed}")
        
        if parsed:
            print(f"Repo ID: {parsed['repo_id']}")
            print(f"Filename: {parsed['filename']}")
            print(f"Type: {parsed['repo_type']}")
            
            # Test single file download method
            print("\nTesting single file download method...")
            success = hf_downloader._download_single_file(
                repo_id=parsed['repo_id'],
                filename=parsed['filename'],
                destination=temp_dir,
                repo_type=parsed['repo_type'],
                progress_callback=test_progress_callback
            )
            
            if success:
                print("✅ Download test completed successfully!")
                
                # Check if file was created
                expected_file = os.path.join(temp_dir, parsed['filename'])
                if os.path.exists(expected_file):
                    file_size = os.path.getsize(expected_file)
                    print(f"✅ File created: {expected_file} ({file_size} bytes)")
                else:
                    print("❌ File was not created")
            else:
                print("❌ Download test failed")
        else:
            print("❌ URL parsing failed")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up test directory: {temp_dir}")
        except:
            pass
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_hf_download()