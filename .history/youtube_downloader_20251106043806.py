"""
YouTube and Multi-Site Video Downloader
Uses yt-dlp for downloading videos from YouTube, Twitter, Instagram, TikTok, etc.
"""

import os
import yt_dlp
import threading
import time
from pathlib import Path
import json

class YouTubeDownloader:
    def __init__(self):
        self.active_downloads = {}
        
    def download(self, url, destination, progress_callback=None, extract_audio=False, auto_quality=True, quality="best"):
        """
        Download video from supported sites using yt-dlp
        
        Args:
            url: Video URL
            destination: Destination folder
            progress_callback: Function to call with progress updates
            extract_audio: Extract audio only
            auto_quality: Auto-select best quality
            quality: Quality preference if not auto
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # Create destination directory
            os.makedirs(destination, exist_ok=True)
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(destination, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'extract_flat': False,
                'writethumbnail': True,
                'writeinfojson': True,
            }
            
            # Configure quality settings
            if extract_audio:
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                if auto_quality:
                    ydl_opts['format'] = 'best[height<=1080]/best'
                else:
                    ydl_opts['format'] = quality
            
            # Store callback for this download
            self.current_callback = progress_callback
            self.current_filename = "Preparing..."
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                self.current_filename = info.get('title', 'Unknown')
                
                if progress_callback:
                    progress_callback({
                        'filename': self.current_filename,
                        'progress': "0%",
                        'speed': "0 B/s",
                        'status': 'Starting'
                    })
                
                # Download video
                ydl.download([url])
            
            if progress_callback:
                progress_callback({
                    'filename': self.current_filename,
                    'progress': "100%",
                    'speed': "0 B/s",
                    'status': 'Completed'
                })
            
            # Return proper result dictionary
            return {
                'status': 'success',
                'filepath': destination,
                'filename': self.current_filename,
                'url': url
            }
            
        except Exception as e:
            error_msg = str(e)
            if progress_callback:
                progress_callback({
                    'filename': getattr(self, 'current_filename', 'Unknown'),
                    'progress': "0%",
                    'speed': "0 B/s",
                    'status': f'Error: {error_msg}'
                })
            return {
                'status': 'error',
                'error': error_msg,
                'filename': getattr(self, 'current_filename', 'Unknown'),
                'url': url
            }
    
    def _progress_hook(self, d):
        """Progress hook for yt-dlp"""
        if not hasattr(self, 'current_callback') or not self.current_callback:
            return
        
        if d['status'] == 'downloading':
            filename = os.path.basename(d.get('filename', self.current_filename))
            
            # Calculate progress
            if 'total_bytes' in d and d['total_bytes']:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                progress_str = f"{progress:.1f}%"
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                progress_str = f"{progress:.1f}%"
            else:
                progress_str = f"{self._format_size(d.get('downloaded_bytes', 0))}"
            
            # Calculate speed
            speed_str = "0 B/s"
            if 'speed' in d and d['speed']:
                speed_str = f"{self._format_size(d['speed'])}/s"
            
            self.current_callback({
                'filename': filename,
                'progress': progress_str,
                'speed': speed_str,
                'status': 'Downloading'
            })
        
        elif d['status'] == 'finished':
            filename = os.path.basename(d.get('filename', self.current_filename))
            self.current_callback({
                'filename': filename,
                'progress': "100%",
                'speed': "0 B/s",
                'status': 'Processing'
            })
    
    def get_video_info(self, url):
        """Get video information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract relevant information
                video_info = {
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': []
                }
                
                # Get available formats
                if 'formats' in info:
                    for fmt in info['formats']:
                        if fmt.get('vcodec') != 'none':  # Video formats
                            format_info = {
                                'format_id': fmt.get('format_id', ''),
                                'ext': fmt.get('ext', ''),
                                'quality': fmt.get('height', 0),
                                'fps': fmt.get('fps', 0),
                                'filesize': fmt.get('filesize', 0),
                                'vcodec': fmt.get('vcodec', ''),
                                'acodec': fmt.get('acodec', ''),
                                'format_note': fmt.get('format_note', '')
                            }
                            video_info['formats'].append(format_info)
                
                return video_info
                
        except Exception as e:
            return None
    
    def get_supported_sites(self):
        """Get list of supported sites"""
        try:
            return yt_dlp.extractor.gen_extractors()
        except:
            # Return common supported sites
            return [
                'YouTube', 'Twitter', 'Instagram', 'TikTok', 'Facebook',
                'Vimeo', 'Dailymotion', 'Reddit', 'Twitch', 'SoundCloud'
            ]
    
    def is_supported_url(self, url):
        """Check if URL is supported by yt-dlp"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Try to extract info without downloading
                ydl.extract_info(url, download=False)
                return True
        except:
            return False
    
    def get_available_qualities(self, url):
        """Get available video qualities for a URL"""
        try:
            video_info = self.get_video_info(url)
            if not video_info or not video_info.get('formats'):
                return []
            
            qualities = []
            seen_qualities = set()
            
            for fmt in video_info['formats']:
                quality = fmt.get('quality', 0)
                if quality > 0 and quality not in seen_qualities:
                    quality_str = f"{quality}p"
                    if fmt.get('fps', 0) > 30:
                        quality_str += f" {fmt['fps']}fps"
                    
                    qualities.append({
                        'format_id': fmt.get('format_id'),
                        'quality': quality_str,
                        'filesize': self._format_size(fmt.get('filesize', 0)) if fmt.get('filesize') else 'Unknown',
                        'ext': fmt.get('ext', ''),
                        'vcodec': fmt.get('vcodec', ''),
                        'acodec': fmt.get('acodec', '')
                    })
                    seen_qualities.add(quality)
            
            # Sort by quality (highest first)
            qualities.sort(key=lambda x: int(x['quality'].split('p')[0]), reverse=True)
            
            return qualities
            
        except Exception as e:
            return []
    
    def _format_size(self, bytes_size):
        """Format file size in human readable format"""
        if not bytes_size:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
    
    def download_with_format(self, url, destination, format_id, progress_callback=None):
        """Download video with specific format"""
        try:
            os.makedirs(destination, exist_ok=True)
            
            ydl_opts = {
                'outtmpl': os.path.join(destination, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'format': format_id,
                'writethumbnail': True,
                'writeinfojson': True,
            }
            
            self.current_callback = progress_callback
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.current_filename = info.get('title', 'Unknown')
                
                if progress_callback:
                    progress_callback({
                        'filename': self.current_filename,
                        'progress': "0%",
                        'speed': "0 B/s",
                        'status': 'Starting'
                    })
                
                ydl.download([url])
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback({
                    'filename': getattr(self, 'current_filename', 'Unknown'),
                    'progress': "0%",
                    'speed': "0 B/s",
                    'status': f'Error: {str(e)}'
                })
            return False