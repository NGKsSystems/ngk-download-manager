    def _cleanup_metadata_files(self, destination, filename):
        """Clean up separate metadata and thumbnail files after embedding"""
        import glob
        
        try:
            # Clean up info.json files
            json_pattern = os.path.join(destination, f"{filename}.info.json")
            for json_file in glob.glob(json_pattern):
                if os.path.exists(json_file):
                    os.remove(json_file)
                    print(f"Cleaned up: {json_file}")
            
            # Clean up thumbnail files (.webp, .jpg, .png)
            thumbnail_extensions = ['webp', 'jpg', 'png', 'jpeg']
            for ext in thumbnail_extensions:
                thumbnail_pattern = os.path.join(destination, f"{filename}.{ext}")
                for thumb_file in glob.glob(thumbnail_pattern):
                    if os.path.exists(thumb_file):
                        os.remove(thumb_file)
                        print(f"Cleaned up: {thumb_file}")
                        
        except Exception as e:
            print(f"Warning: Could not clean up metadata files: {e}")
            # Don't fail the download if cleanup fails