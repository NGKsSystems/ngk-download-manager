# Download Resume Feature

## Overview
The download manager now includes persistent download state tracking, allowing you to resume incomplete downloads even after closing the application.

## How It Works

### 1. State Persistence
When you start a download, the download manager automatically saves:
- Download URL
- Destination file path
- Total file size
- Downloaded bytes so far
- Number of chunks downloaded
- Download status (started, downloading, paused, completed)
- Timestamp

This information is stored in: `~/.ngk_download_manager/downloads.json`

### 2. Partial Files
When a download is interrupted:
- The partial file is saved with a `.part` extension
- The download state is preserved in the JSON file
- Both the `.part` file and state file act as markers for resumable downloads

### 3. Resume Detection
When you restart the application:
1. The app scans for `.part` files
2. It checks the saved download state
3. If a partial download is found, a dialog appears showing:
   - Filename
   - Progress percentage
   - Size downloaded vs total size
   - Number of chunks completed

4. You can choose to resume or start fresh

### 4. Resume Process
When resuming:
- The app sends an HTTP `Range` header to the server: `bytes=<existing_size>-`
- The server responds with HTTP 206 (Partial Content)
- Downloads continue from where it left off
- Progress updates show "Resuming from X%" status

## Chunk Tracking

Downloads are split into **1MB chunks** for better performance:
- Each chunk is tracked in the download state
- Progress display shows: "Downloading (Chunk N)"
- This provides smooth progress updates even on slow connections

## File Structure

```
~/.ngk_download_manager/
└── downloads.json          # Persistent state file
    └── download_id: {
        "url": "...",
        "filepath": "...",
        "total_size": 123456789,
        "downloaded_size": 67890,
        "chunks": 68,
        "status": "downloading",
        "started_at": "2025-11-12T...",
        "last_update": "2025-11-12T..."
    }

~/Downloads/NGK_Downloads/
├── video.mp4              # Completed download
└── backup.tar.gz.part     # Partial download (will be resumed)
```

## Example Scenario

**Scenario: Download interrupted at 32%**

1. You start downloading `backup.tar.gz` (100 MB)
2. After downloading 32 MB (chunk 32), you close the app
3. Files created:
   - `~/Downloads/NGK_Downloads/backup.tar.gz.part` (32 MB)
   - `~/.ngk_download_manager/downloads.json` (state saved)

4. You restart the app
5. Resume dialog appears showing: "backup.tar.gz - 32% complete (32 MB of 100 MB)"
6. Click "Yes" to resume
7. App sends: `Range: bytes=33554432-` (continue from 32 MB)
8. Download resumes and completes
9. Final file: `~/Downloads/NGK_Downloads/backup.tar.gz` (100 MB)

## Supported Downloaders

Resume works with:
- ✅ Direct HTTP/HTTPS downloads (via `download_manager.py`)
- ✅ HuggingFace downloads (via `huggingface_downloader.py`)
- ⚠️ YouTube downloads (limited - yt-dlp uses fragment-based streaming)

## Progress Updates

Progress is reported more frequently now:
- Every 0.3 seconds (previously 0.5s)
- OR every 5 chunks (whichever comes first)
- Shows "Downloading (Chunk N)" for visual feedback

This provides smooth UI updates even on slow connections.

## Troubleshooting

### Download doesn't resume
**Problem**: Partial file exists but resume shows 0% progress  
**Solution**: Server may not support Range requests. Check if file was downloaded from a CDN with no resume support.

### State file corrupted
**Problem**: `~/.ngk_download_manager/downloads.json` error  
**Solution**: Delete the corrupted file and restart the app. Old downloads won't be resumable but new downloads will work fine.

### Too many resumable downloads listed
**Problem**: Many old downloads showing in resume dialog  
**Solution**: Clean up old `.part` files in your download directory manually, then restart the app.

## Best Practices

1. **For large files**: Downloads will show chunk progress - wait for "Downloading (Chunk N)" status
2. **On unstable connections**: The app will automatically detect interruptions and offer resume
3. **Manual cleanup**: Completed `.part` files are removed automatically when download finishes
4. **State file**: Don't manually edit `downloads.json` - it's managed by the app

## Technical Details

### Download ID
Each download is identified by: `{url}_{filepath}`

This ensures:
- Same URL to different locations creates separate state
- Same file location from different URLs creates separate state
- Prevents conflicts between similar downloads

### Chunk Size
1 MB chunks were chosen because:
- Efficient for network I/O (1024 × 1024 bytes)
- Balance between responsiveness and overhead
- Good for both fast and slow connections
- Visible progress updates (1MB chunks on 1Mbps = 8 second chunks)

### State Save Frequency
Download state is saved:
- At download start
- After every chunk (immediate persistence)
- At download completion
- This ensures resumability even on crash

## Future Improvements

Potential enhancements:
- [ ] UI button to manually resume downloads
- [ ] Pause/resume from UI (not just app restart)
- [ ] Download queue with multiple simultaneous downloads
- [ ] Better cleanup of old state entries
- [ ] Bandwidth limiting
