"""
Hugging Face Model and Dataset Downloader
Handles authentication and downloads from Hugging Face Hub
"""

import os
import requests
from huggingface_hub import HfApi, hf_hub_download, snapshot_download, login, logout
from huggingface_hub.utils import RepositoryNotFoundError, RevisionNotFoundError
from urllib.parse import urlparse, unquote
import time
import threading
from pathlib import Path
import json

class HuggingFaceDownloader:
    def __init__(self):
        self.api = HfApi()
        self.active_downloads = {}
        
    def download(self, url, destination, progress_callback=None, token=None):
        """
        Download model or dataset from Hugging Face
        
        Args:
            url: Hugging Face URL (model or dataset)
            destination: Destination folder
            progress_callback: Function to call with progress updates
            token: HF authentication token
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # Parse HF URL
            repo_info = self._parse_hf_url(url)
            if not repo_info:
                raise ValueError("Invalid Hugging Face URL")
            
            repo_id = repo_info['repo_id']
            repo_type = repo_info['repo_type']
            filename = repo_info.get('filename')
            
            # Set up authentication if token provided
            if token:
                os.environ['HUGGINGFACE_HUB_TOKEN'] = token
                login(token=token)
            
            # Create destination directory
            repo_dest = os.path.join(destination, repo_id.replace('/', '_'))
            os.makedirs(repo_dest, exist_ok=True)
            
            if progress_callback:
                progress_callback({
                    'filename': repo_id,
                    'progress': "0%",
                    'speed': "0 B/s",
                    'status': 'Initializing'
                })
            
            # Download specific file or entire repository
            if filename:
                success = self._download_single_file(
                    repo_id, filename, repo_dest, repo_type, progress_callback
                )
            else:
                success = self._download_repository(
                    repo_id, repo_dest, repo_type, progress_callback
                )
            
            if success and progress_callback:
                progress_callback({
                    'filename': repo_id,
                    'progress': "100%",
                    'speed': "0 B/s",
                    'status': 'Completed'
                })
            
            return success
            
        except Exception as e:
            if progress_callback:
                progress_callback({
                    'filename': repo_info.get('repo_id', 'Unknown') if 'repo_info' in locals() else 'Unknown',
                    'progress': "0%",
                    'speed': "0 B/s",
                    'status': f'Error: {str(e)}'
                })
            return False
    
    def _download_single_file(self, repo_id, filename, destination, repo_type, progress_callback):
        """Download a single file from HF repository"""
        try:
            file_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                repo_type=repo_type,
                local_dir=destination,
                local_dir_use_symlinks=False
            )
            
            if progress_callback:
                progress_callback({
                    'filename': filename,
                    'progress': "100%",
                    'speed': "0 B/s",
                    'status': 'Downloaded'
                })
            
            return True
            
        except Exception as e:
            return False
    
    def _download_repository(self, repo_id, destination, repo_type, progress_callback):
        """Download entire repository from HF"""
        try:
            # Get repository info
            repo_info = self.get_repository_info(repo_id, repo_type)
            if not repo_info:
                return False
            
            total_files = len(repo_info.get('files', []))
            downloaded_files = 0
            
            def file_progress_callback(file_info):
                nonlocal downloaded_files
                downloaded_files += 1
                progress = (downloaded_files / total_files) * 100 if total_files > 0 else 0
                
                if progress_callback:
                    progress_callback({
                        'filename': repo_id,
                        'progress': f"{progress:.1f}%",
                        'speed': "0 B/s",
                        'status': f'Downloading ({downloaded_files}/{total_files})'
                    })
            
            # Download repository
            snapshot_download(
                repo_id=repo_id,
                repo_type=repo_type,
                local_dir=destination,
                local_dir_use_symlinks=False
            )
            
            return True
            
        except Exception as e:
            return False
    
    def _parse_hf_url(self, url):
        """Parse Hugging Face URL to extract repo info"""
        try:
            parsed = urlparse(url)
            if 'huggingface.co' not in parsed.netloc:
                return None
            
            path_parts = [p for p in parsed.path.split('/') if p]
            
            if len(path_parts) < 2:
                return None
            
            # Determine repo type and remove type indicators from path
            repo_type = 'model'  # default
            if len(path_parts) > 0 and 'datasets' == path_parts[0]:
                repo_type = 'dataset'
                path_parts = path_parts[1:]  # Remove 'datasets' from path
            elif len(path_parts) > 0 and 'spaces' == path_parts[0]:
                repo_type = 'space'
                path_parts = path_parts[1:]  # Remove 'spaces' from path
            
            # Need at least 2 parts for repo_id (org/name)
            if len(path_parts) < 2:
                return None
            
            # Extract repo_id (first two parts: org/repo)
            repo_id = f"{path_parts[0]}/{path_parts[1]}"
            
            # Check for specific file
            filename = None
            if len(path_parts) > 2:
                if 'blob' in path_parts:
                    blob_index = path_parts.index('blob')
                    if blob_index + 2 < len(path_parts):
                        # Skip 'blob' and branch name (usually 'main')
                        filename = '/'.join(path_parts[blob_index + 2:])
                elif 'resolve' in path_parts:
                    resolve_index = path_parts.index('resolve')
                    if resolve_index + 2 < len(path_parts):
                        # Skip 'resolve' and branch name (usually 'main')
                        filename = '/'.join(path_parts[resolve_index + 2:])
            
            return {
                'repo_id': repo_id,
                'repo_type': repo_type,
                'filename': filename
            }
            
        except Exception as e:
            return None
    
    def get_repository_info(self, repo_id, repo_type='model'):
        """Get repository information"""
        try:
            if repo_type == 'model':
                info = self.api.model_info(repo_id)
                files = [f.rfilename for f in info.siblings] if info.siblings else []
            elif repo_type == 'dataset':
                info = self.api.dataset_info(repo_id)
                files = [f.rfilename for f in info.siblings] if info.siblings else []
            else:
                return None
            
            return {
                'repo_id': repo_id,
                'repo_type': repo_type,
                'author': info.author if hasattr(info, 'author') else None,
                'description': getattr(info, 'description', ''),
                'tags': getattr(info, 'tags', []),
                'downloads': getattr(info, 'downloads', 0),
                'likes': getattr(info, 'likes', 0),
                'created_at': getattr(info, 'created_at', None),
                'last_modified': getattr(info, 'last_modified', None),
                'files': files,
                'total_size': sum(getattr(f, 'size', 0) for f in info.siblings) if info.siblings else 0
            }
            
        except Exception as e:
            return None
    
    def validate_token(self, token):
        """Validate Hugging Face token"""
        try:
            # Try to authenticate with the token
            api = HfApi(token=token)
            user_info = api.whoami()
            return user_info is not None
        except Exception as e:
            return False
    
    def search_models(self, query, limit=20):
        """Search for models on Hugging Face"""
        try:
            models = self.api.list_models(search=query, limit=limit)
            results = []
            
            for model in models:
                results.append({
                    'repo_id': model.modelId,
                    'author': model.author,
                    'downloads': model.downloads,
                    'likes': model.likes,
                    'tags': model.tags,
                    'created_at': model.created_at,
                    'last_modified': model.last_modified
                })
            
            return results
            
        except Exception as e:
            return []
    
    def search_datasets(self, query, limit=20):
        """Search for datasets on Hugging Face"""
        try:
            datasets = self.api.list_datasets(search=query, limit=limit)
            results = []
            
            for dataset in datasets:
                results.append({
                    'repo_id': dataset.id,
                    'author': dataset.author,
                    'downloads': dataset.downloads,
                    'likes': dataset.likes,
                    'tags': dataset.tags,
                    'created_at': dataset.created_at,
                    'last_modified': dataset.last_modified
                })
            
            return results
            
        except Exception as e:
            return []
    
    def get_model_card(self, repo_id):
        """Get model card (README) content"""
        try:
            card_data = self.api.model_info(repo_id, files_metadata=True)
            # Try to find README file
            readme_files = [f for f in card_data.siblings if f.rfilename.lower().startswith('readme')]
            
            if readme_files:
                readme_content = hf_hub_download(
                    repo_id=repo_id,
                    filename=readme_files[0].rfilename,
                    repo_type='model'
                )
                
                with open(readme_content, 'r', encoding='utf-8') as f:
                    return f.read()
            
            return None
            
        except Exception as e:
            return None
    
    def is_private_repo(self, repo_id, repo_type='model'):
        """Check if repository is private"""
        try:
            if repo_type == 'model':
                info = self.api.model_info(repo_id)
            elif repo_type == 'dataset':
                info = self.api.dataset_info(repo_id)
            else:
                return False
            
            return getattr(info, 'private', False)
            
        except RepositoryNotFoundError:
            # Might be private and we don't have access
            return True
        except Exception as e:
            return False
    
    def get_download_url(self, repo_id, filename, repo_type='model'):
        """Get direct download URL for a file"""
        try:
            url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
            if repo_type == 'dataset':
                url = f"https://huggingface.co/datasets/{repo_id}/resolve/main/{filename}"
            
            return url
            
        except Exception as e:
            return None
    
    def _format_size(self, bytes_size):
        """Format file size in human readable format"""
        if not bytes_size:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"