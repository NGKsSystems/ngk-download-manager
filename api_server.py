"""
REST API Server for Download Manager
Runs on GCE VM, controlled remotely by phone app
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import threading
from pathlib import Path
import mimetypes

# Import existing download manager components
from youtube_downloader import YouTubeDownloader
from huggingface_downloader import HuggingFaceDownloader
from download_manager import DownloadManager
from downloads_database import DownloadsDatabase
from utils import URLDetector

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app

# Initialize components
downloads_db = DownloadsDatabase()
url_detector = URLDetector()
downloaders = {
    'youtube': YouTubeDownloader(),
    'hf': HuggingFaceDownloader(),
    'direct': DownloadManager()
}

# Configuration
DOWNLOAD_DIR = os.path.expanduser("~/Downloads/NGK_Downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Active downloads tracking
active_downloads = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'NGK Download Manager API',
        'version': '1.0'
    })

@app.route('/download', methods=['POST'])
def queue_download():
    """
    Queue a new download
    
    Body:
        {
            "url": "https://youtube.com/watch?v=...",
            "quality": "best" | "720p" | "480p" | "audio",
            "filename": "optional_custom_name"
        }
    """
    data = request.json
    url = data.get('url')
    quality = data.get('quality', 'best')
    custom_filename = data.get('filename')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Detect URL type
    url_type = url_detector.detect_url_type(url)
    
    # Generate download ID
    from datetime import datetime
    download_id = f"dl_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(active_downloads)}"
    
    # Add to database
    downloads_db.add_download(
        download_id=download_id,
        url=url,
        filename=custom_filename or "Preparing...",
        destination=DOWNLOAD_DIR,
        url_type=url_type
    )
    
    # Start download in background thread
    thread = threading.Thread(
        target=download_worker,
        args=(download_id, url, url_type, quality),
        daemon=True
    )
    thread.start()
    
    return jsonify({
        'download_id': download_id,
        'url': url,
        'type': url_type,
        'status': 'queued'
    }), 201

def download_worker(download_id, url, url_type, quality):
    """Background worker to handle downloads"""
    def progress_callback(progress_info):
        # Update database with progress
        update_data = {}
        if 'filename' in progress_info:
            update_data['filename'] = progress_info['filename']
        if 'progress' in progress_info:
            try:
                progress_text = progress_info['progress']
                if progress_text.endswith('%'):
                    update_data['progress_percent'] = float(progress_text[:-1])
            except:
                pass
        if 'speed' in progress_info:
            update_data['speed'] = progress_info['speed']
        if 'status' in progress_info:
            update_data['status'] = progress_info['status']
        
        if update_data:
            downloads_db.update_download(download_id, **update_data)
    
    try:
        active_downloads[download_id] = {'status': 'downloading'}
        
        if url_type == "YouTube":
            audio_only = quality == "audio"
            result = downloaders['youtube'].download(
                url, DOWNLOAD_DIR, progress_callback,
                extract_audio=audio_only,
                auto_quality=True
            )
        elif url_type == "Hugging Face":
            result = downloaders['hf'].download(url, DOWNLOAD_DIR, progress_callback)
        else:
            result = downloaders['direct'].download(url, DOWNLOAD_DIR, progress_callback)
        
        # Mark as completed
        downloads_db.update_download(
            download_id,
            status='completed',
            progress_percent=100,
            filename=result.get('filename') if isinstance(result, dict) else None
        )
        active_downloads[download_id] = {'status': 'completed', 'result': result}
        
    except Exception as e:
        downloads_db.update_download(
            download_id,
            status='failed',
            error=str(e)
        )
        active_downloads[download_id] = {'status': 'failed', 'error': str(e)}

@app.route('/status/<download_id>', methods=['GET'])
def get_download_status(download_id):
    """Get status of a specific download"""
    download_info = downloads_db.get_download(download_id)
    
    if not download_info:
        return jsonify({'error': 'Download not found'}), 404
    
    return jsonify(download_info)

@app.route('/downloads', methods=['GET'])
def list_downloads():
    """List all downloads"""
    status_filter = request.args.get('status')  # Optional: filter by status
    
    all_downloads = downloads_db.get_all_downloads()
    
    if status_filter:
        filtered = {
            did: info for did, info in all_downloads.items()
            if info.get('status') == status_filter
        }
        return jsonify(filtered)
    
    return jsonify(all_downloads)

@app.route('/files', methods=['GET'])
def list_files():
    """List downloaded files"""
    try:
        files = []
        download_path = Path(DOWNLOAD_DIR)
        
        for file_path in download_path.rglob('*'):
            if file_path.is_file() and not file_path.name.endswith('.part'):
                stat = file_path.stat()
                files.append({
                    'name': file_path.name,
                    'path': str(file_path.relative_to(download_path)),
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'url': f'/files/{file_path.relative_to(download_path)}'
                })
        
        # Sort by modified time, newest first
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'directory': DOWNLOAD_DIR,
            'count': len(files),
            'files': files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files/<path:filepath>', methods=['GET'])
def download_file(filepath):
    """Download a specific file (with range request support for streaming)"""
    try:
        file_path = Path(DOWNLOAD_DIR) / filepath
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Security check: ensure file is within download directory
        if not str(file_path.resolve()).startswith(str(Path(DOWNLOAD_DIR).resolve())):
            return jsonify({'error': 'Access denied'}), 403
        
        # Support range requests for video streaming
        range_header = request.headers.get('Range')
        if range_header:
            return send_file_with_range(file_path, range_header)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_path.name
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_file_with_range(file_path, range_header):
    """Send file with range support for streaming"""
    file_size = file_path.stat().st_size
    
    # Parse range header
    byte_range = range_header.replace('bytes=', '').split('-')
    start = int(byte_range[0]) if byte_range[0] else 0
    end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else file_size - 1
    length = end - start + 1
    
    # Read requested chunk
    with open(file_path, 'rb') as f:
        f.seek(start)
        data = f.read(length)
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = 'application/octet-stream'
    
    response = app.response_class(
        data,
        206,  # Partial Content
        mimetype=content_type,
        direct_passthrough=True
    )
    response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
    response.headers.add('Accept-Ranges', 'bytes')
    response.headers.add('Content-Length', str(length))
    
    return response

@app.route('/delete/<download_id>', methods=['DELETE'])
def delete_download(download_id):
    """Delete a download from database"""
    success = downloads_db.delete_download(download_id)
    
    if success:
        return jsonify({'message': 'Download deleted'})
    else:
        return jsonify({'error': 'Download not found'}), 404

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get download statistics"""
    stats = downloads_db.get_statistics()
    return jsonify(stats)

if __name__ == '__main__':
    print(f"Starting Download Manager API Server")
    print(f"Download directory: {DOWNLOAD_DIR}")
    print(f"Listening on http://0.0.0.0:5000")
    
    # Run on all interfaces so it's accessible from network
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
