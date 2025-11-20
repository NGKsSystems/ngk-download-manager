"""
Persistent Downloads Database
Stores all downloads (active, completed, failed) across app restarts
"""

import os
import json
from datetime import datetime
from pathlib import Path

class DownloadsDatabase:
    """
    Persistent database for all downloads
    Survives app restart - nothing removed until user explicitly deletes
    """
    
    def __init__(self, db_file="downloads_database.json"):
        self.db_file = db_file
        self.downloads = self._load_database()
    
    def _load_database(self):
        """Load downloads database from disk"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading downloads database: {e}")
                return {}
        return {}
    
    def _save_database(self):
        """Save downloads database to disk"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.downloads, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving downloads database: {e}")
            return False
    
    def add_download(self, download_id, url, filename, destination, url_type):
        """
        Add a new download to the database
        
        Args:
            download_id: Unique identifier for this download
            url: Download URL
            filename: Filename to save as
            destination: Destination folder
            url_type: Type of URL (YouTube, Direct, HF, etc)
        
        Returns:
            dict: The download entry
        """
        entry = {
            'id': download_id,
            'url': url,
            'filename': filename,
            'destination': destination,
            'type': url_type,
            'status': 'queued',
            'progress': 0,
            'speed': '0 B/s',
            'downloaded': 0,
            'total': 0,
            'chunks': 0,
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'error': None
        }
        
        self.downloads[download_id] = entry
        self._save_database()
        return entry
    
    def update_download(self, download_id, **kwargs):
        """
        Update download progress and status
        
        Args:
            download_id: Download ID to update
            **kwargs: Fields to update (progress, speed, status, etc)
        """
        if download_id not in self.downloads:
            return False
        
        download = self.downloads[download_id]
        
        # Update provided fields
        for key, value in kwargs.items():
            download[key] = value
        
        # Set started_at if status changes to downloading
        if kwargs.get('status') == 'downloading' and not download.get('started_at'):
            download['started_at'] = datetime.now().isoformat()
        
        # Set completed_at if status changes to completed
        if kwargs.get('status') == 'completed' and not download.get('completed_at'):
            download['completed_at'] = datetime.now().isoformat()
        
        # Mark as completed if progress is 100
        if kwargs.get('progress') == 100 and download.get('status') != 'completed':
            download['status'] = 'completed'
            download['completed_at'] = datetime.now().isoformat()
        
        self._save_database()
        return True
    
    def get_download(self, download_id):
        """Get a specific download entry"""
        return self.downloads.get(download_id)
    
    def get_all_downloads(self):
        """Get all downloads (ordered by creation date, newest first)"""
        sorted_downloads = sorted(
            self.downloads.values(),
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )
        return sorted_downloads
    
    def get_downloads_by_status(self, status):
        """Get downloads by status (downloading, completed, failed, etc)"""
        return [
            d for d in self.downloads.values()
            if d.get('status') == status
        ]
    
    def delete_download(self, download_id):
        """
        Delete a download from the database
        Only removes when user explicitly deletes
        """
        if download_id in self.downloads:
            del self.downloads[download_id]
            self._save_database()
            return True
        return False
    
    def clear_downloads(self, older_than_days=None):
        """
        Clear downloads from database
        
        Args:
            older_than_days: If set, only clear downloads older than N days
        """
        if older_than_days is None:
            # Clear all
            self.downloads = {}
        else:
            # Clear only old entries
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=older_than_days)
            to_delete = []
            
            for download_id, download in self.downloads.items():
                created = datetime.fromisoformat(download.get('created_at', ''))
                if created < cutoff:
                    to_delete.append(download_id)
            
            for download_id in to_delete:
                del self.downloads[download_id]
        
        self._save_database()
        return True
    
    def get_statistics(self):
        """Get download statistics"""
        downloads = self.downloads.values()
        
        return {
            'total': len(downloads),
            'downloading': len([d for d in downloads if d.get('status') == 'downloading']),
            'completed': len([d for d in downloads if d.get('status') == 'completed']),
            'failed': len([d for d in downloads if d.get('status') == 'failed']),
            'queued': len([d for d in downloads if d.get('status') == 'queued']),
            'total_downloaded': sum(d.get('downloaded', 0) for d in downloads),
            'total_size': sum(d.get('total', 0) for d in downloads)
        }
    
    def export_downloads(self, filepath):
        """Export downloads to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.downloads, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting downloads: {e}")
            return False
    
    def import_downloads(self, filepath):
        """Import downloads from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            # Merge with existing
            self.downloads.update(imported)
            self._save_database()
            return True
        except Exception as e:
            print(f"Error importing downloads: {e}")
            return False
