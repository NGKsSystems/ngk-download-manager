"""
Direct file renaming script using Python
"""
import os

def clean_quotes_from_files():
    download_dir = r"C:\Users\suppo\Downloads\NGK_Downloads"
    
    if not os.path.exists(download_dir):
        print(f"Directory not found: {download_dir}")
        return
    
    renamed_count = 0
    
    for filename in os.listdir(download_dir):
        if '"' in filename:
            old_path = os.path.join(download_dir, filename)
            
            # Replace quotes with nothing
            new_filename = filename.replace('"', '')
            new_path = os.path.join(download_dir, new_filename)
            
            if not os.path.exists(new_path):
                try:
                    os.rename(old_path, new_path)
                    print(f"✅ Renamed: {filename}")
                    print(f"   -> {new_filename}")
                    renamed_count += 1
                except Exception as e:
                    print(f"❌ Failed to rename {filename}: {e}")
            else:
                print(f"⚠️  Target already exists: {new_filename}")
    
    print(f"\n🎉 Successfully renamed {renamed_count} files!")

if __name__ == "__main__":
    print("🧹 Removing quotes from filenames...")
    clean_quotes_from_files()
    input("\nPress Enter to exit...")