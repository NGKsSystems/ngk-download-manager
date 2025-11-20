# Quick Start - Resume Feature

## What Changed
Your download manager now **automatically remembers partial downloads** even after you close the app!

## What Happens Now

### ✅ Download Interrupted
You were downloading and got to 32%:
```
backup.tar.gz
Status: Downloading (Chunk 33)
Progress: 32% (34 MB / 100 MB)
```

You close the app. Files saved:
- `~/Downloads/NGK_Downloads/backup.tar.gz.part` (32 MB partial file)
- `~/.ngk_download_manager/downloads.json` (state info)

### ✅ Restart App
When you restart:
1. App checks for partial downloads (500ms after startup)
2. Dialog appears:
   ```
   Found incomplete downloads from previous sessions:
   
   • backup.tar.gz
     32% complete (34 MB of 100 MB)
   
   Would you like to resume these downloads?
   ```

3. Click **"Yes"** → Download resumes from 32%!

## How It Works Behind the Scenes

### State Files
**Location**: `~/.ngk_download_manager/downloads.json`

Contains:
- Which downloads were in progress
- How much was downloaded (byte count)
- Number of chunks completed
- Download timestamps

### Partial Files
- While downloading: `backup.tar.gz.part` 
- When complete: `backup.tar.gz` (`.part` removed)

### Resume Process
1. App detects `.part` file
2. Sends HTTP Range header to server
3. Server continues from that byte position
4. No wasted bandwidth!

## Examples

### Scenario 1: Internet Disconnected
```
You: Downloading 500 MB file
    Progress: 45% (225 MB)
    [Internet drops]
    
You: Restart app
    Dialog: Resume? (225 MB of 500 MB)
    
Click "Yes"
    Downloads resume from 225 MB
    Takes 30% less time!
```

### Scenario 2: App Crashed
```
You: Download in progress
    Progress: 68% (68 MB of 100 MB)
    [App crashes]
    
You: Restart app
    Dialog: Resume? (68 MB of 100 MB)
    
Click "Yes"
    Downloads resume from 68 MB
```

### Scenario 3: Manual Close
```
You: Download started
    Progress: 23% 
    [Close app with X button]
    
Later:
You: Restart app
    Dialog: Resume? (23%)
    
Click "Yes"
    Downloads continue!
```

## Important Notes

✓ **Works automatically** - no manual setup needed
✓ **Saves time** - doesn't restart from 0%
✓ **Works across crashes** - app can crash, state survives
✓ **Works across restarts** - works even after computer shutdown
✓ **No user action** - just click "Yes" when prompted

## Limitations

⚠️ **YouTube downloads**: Limited support (uses streaming fragments)
⚠️ **Some CDNs**: Don't support resume (rare)
⚠️ **Manual cleanup**: Old partial files need manual cleanup sometimes

## Clean Up Old Downloads

If you want to clean up old incomplete downloads:

1. Open `~/Downloads/` folder
2. Look for files ending in `.part`
3. Delete them if you don't need to resume
4. App will automatically clean up on next startup

## Progress Display

During download, you'll see:
```
Downloading (Chunk 33) ← Shows which chunk being downloaded
34.5 MB/s ← Speed
43% (43 MB / 100 MB) ← Progress
```

The "Chunk" counter shows real-time progress even on slow connections.

## Troubleshooting

### Q: Resume dialog doesn't appear
- **A**: App only checks on startup. Close and restart the app.

### Q: Download shows 0% when resuming  
- **A**: Some servers don't support resume. Download will start fresh.

### Q: Can't find the `.part` file
- **A**: Check `~/Downloads/NGK_Downloads/` folder
- **A**: Files are hidden on some systems - show hidden files

### Q: Too many old partial downloads listed
- **A**: Delete the old `.part` files manually
- **A**: They're in `~/Downloads/NGK_Downloads/`

## Advanced Info

- **State file**: `~/.ngk_download_manager/downloads.json`
- **Chunk size**: 1 MB per chunk
- **HTTP header used**: `Range: bytes=X-`
- **Check timing**: App checks 500ms after startup

## Summary

You were at **32%** → now you'll be back to **32%** when you restart!

No more wasted download time. Just close the app, restart, and click "Yes" to resume. 🎉
