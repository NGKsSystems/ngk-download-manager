"""
Download State Manager
Saves and restores download progress across app restarts
"""

import os
import json
from pathlib import Path
from datetime import datetime

class DownloadStateManager:
    def __init__(self, state_dir=None):
        if state_dir is None:
            state_dir = os.path.expanduser("~/.ngk_download_manager")
        self.state_dir = state_dir
        self.state_file = os.path.join(state_dir, "downloads.json")
        os.makedirs(state_dir, exist_ok=True)
        self.downloads = self._load_state()
    
    def _load_state(self):
        """Load saved download state from disk"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading download state: {e}")
        return {}
    
    def _save_state(self):
        """Save download state to disk"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.downloads, f, indent=2)
        except Exception as e:
            print(f"Error saving download state: {e}")
    
    def start_download(self, url, filepath, total_size=0):
        """Record a new download"""
        download_id = f"{url}_{filepath}"
        self.downloads[download_id] = {
            'url': url,
            'filepath': filepath,
            'total_size': total_size,
            'downloaded_size': 0,
            'status': 'started',
            'started_at': datetime.now().isoformat(),
            'chunks': 0
        }
        self._save_state()
        return download_id
    
    def update_download(self, download_id, downloaded_size, chunks, status='downloading'):
        """Update download progress"""
        if download_id in self.downloads:
            self.downloads[download_id].update({
                'downloaded_size': downloaded_size,
                'chunks': chunks,
                'status': status,
                'last_update': datetime.now().isoformat()
            })
            self._save_state()
    
    def complete_download(self, download_id):
        """Mark download as complete"""
        if download_id in self.downloads:
            self.downloads[download_id]['status'] = 'completed'
            self.downloads[download_id]['completed_at'] = datetime.now().isoformat()
            self._save_state()
    
    def remove_download(self, download_id):
        """Remove download from state"""
        if download_id in self.downloads:
            del self.downloads[download_id]
            self._save_state()
    
    def get_resumable_downloads(self, destination_dir):
        """Find partial downloads that can be resumed"""
        resumable = []
        
        for download_id, info in self.downloads.items():
            if info['status'] in ['downloading', 'paused']:
                filepath = info['filepath']
                
                # Check if partial file exists
                if os.path.exists(filepath + '.part'):
                    partial_size = os.path.getsize(filepath + '.part')
                    resumable.append({
                        'download_id': download_id,
                        'url': info['url'],
                        'filepath': filepath,
                        'partial_size': partial_size,
                        'total_size': info['total_size'],
                        'chunks': info.get('chunks', 0),
                        'progress': (partial_size / info['total_size'] * 100) if info['total_size'] > 0 else 0
                    })
                elif os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    total = info['total_size']
                    if file_size < total:
                        resumable.append({
                            'download_id': download_id,
                            'url': info['url'],
                            'filepath': filepath,
                            'partial_size': file_size,
                            'total_size': total,
                            'chunks': info.get('chunks', 0),
                            'progress': (file_size / total * 100) if total > 0 else 0
                        })
        
        return resumable
    
    def get_download_info(self, download_id):
        """Get info about a specific download"""
        return self.downloads.get(download_id)
    
    def get_all_downloads(self):
        """Get all downloads"""
        return self.downloads
