"""
Debug dataset URL parsing
"""

from urllib.parse import urlparse

def debug_datasets_url():
    url = "https://huggingface.co/datasets/squad"
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]
    
    print(f"URL: {url}")
    print(f"Path parts: {path_parts}")
    print(f"Length: {len(path_parts)}")
    
    if len(path_parts) > 0:
        print(f"First part: '{path_parts[0]}'")
        print(f"Is 'datasets'?: {path_parts[0] == 'datasets'}")
        
        if path_parts[0] == 'datasets':
            path_parts = path_parts[1:]
            print(f"After removing 'datasets': {path_parts}")
            print(f"Length after: {len(path_parts)}")

if __name__ == "__main__":
    debug_datasets_url()