"""
Manual script to clean existing filenames with quotes
"""
import os
import re

def sanitize_filename(filename):
    """Remove quotes and other problematic characters from filename"""
    # Remove quotes and other problematic characters
    filename = re.sub(r'["\'""]', '', filename)  # Remove all types of quotes
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # Remove Windows invalid chars
    filename = re.sub(r'\s+', ' ', filename)  # Replace multiple spaces with single space
    return filename.strip()

def clean_existing_files():
    """Clean existing files in the download directory"""
    download_dir = r"C:\Users\suppo\Downloads\NGK_Downloads"
    
    if not os.path.exists(download_dir):
        print(f"Directory not found: {download_dir}")
        return
    
    cleaned_count = 0
    
    for filename in os.listdir(download_dir):
        filepath = os.path.join(download_dir, filename)
        
        # Skip directories
        if os.path.isdir(filepath):
            continue
        
        # Split name and extension
        name, ext = os.path.splitext(filename)
        
        # Clean the filename
        clean_name = sanitize_filename(name)
        
        # Only rename if the name changed
        if clean_name != name:
            new_filename = clean_name + ext
            new_filepath = os.path.join(download_dir, new_filename)
            
            # Avoid conflicts
            if not os.path.exists(new_filepath):
                try:
                    os.rename(filepath, new_filepath)
                    print(f"✅ Cleaned: {filename} -> {new_filename}")
                    cleaned_count += 1
                except OSError as e:
                    print(f"❌ Failed to rename {filename}: {e}")
            else:
                print(f"⚠️  Skipped {filename} (target exists)")
    
    print(f"\n🎉 Cleaned {cleaned_count} files!")

if __name__ == "__main__":
    print("🧹 Cleaning existing files with quotes...")
    clean_existing_files()
    input("\nPress Enter to exit...")