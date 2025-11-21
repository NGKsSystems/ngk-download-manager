# Mobile Remote Controller Setup

## What Changed
The mobile app is now a **remote controller** that talks to your GCE VM instead of running downloads directly on the phone.

## Features
- ✅ Start/Stop VM remotely via Cloud Function
- ✅ Queue downloads to VM
- ✅ Monitor download progress in real-time
- ✅ Browse downloaded files
- ✅ Download files from VM to phone
- ✅ Works with full yt-dlp on VM (no APK build issues!)

## Before Building APK

### 1. Update Configuration in `main.py`

Edit these lines at the top of `mobile_remote_app.py` (or `main.py`):

```python
CLOUD_FUNCTION_URL = "https://us-central1-YOUR_PROJECT.cloudfunctions.net/vm-control"
API_KEY = "your-api-key-from-cloud-function-deployment"
VM_STATIC_IP = "136.114.215.21"  # Your VM's static IP
VM_API_PORT = "5000"
```

Replace with your actual values from:
- Cloud Function URL (from `gcloud functions describe`)
- API Key (generated during Cloud Function deployment)
- Static IP (from GCP Console or `gcloud compute addresses list`)

### 2. Build APK (GitHub Actions)

Now that requirements are simplified (only kivy + requests), the APK will build successfully!

```powershell
# Commit changes
git add .
git commit -m "Convert mobile app to remote controller"
git push
```

Go to GitHub Actions and watch it build. Should complete in ~20-30 minutes.

### 3. Or Build Locally with Buildozer

If you have WSL set up:

```bash
cd "/mnt/c/Users/suppo/Desktop/NGKsSystems/NGKs DL Manager"
buildozer android debug
```

APK will be in `bin/` folder.

## How to Use

### First Time Setup:
1. Install APK on your phone
2. Open app
3. Tap "Start Server" to boot the VM
4. Wait 30-60 seconds for "Server is ready!"

### Queue a Download:
1. Paste YouTube/HuggingFace/direct URL
2. Select quality
3. Tap "Queue Download"
4. Switch to Downloads tab to see progress

### Browse Files:
1. Switch to Files tab
2. Tap "Refresh"
3. Tap "Download" on any file to save to phone

### When Done:
1. Tap "Stop Server" to shut down VM (saves money!)

## Architecture

```
[Phone App]
    ↓ HTTPS (Cloud Function)
[Google Cloud Function] ← API Key Auth
    ↓ GCP API
[GCE VM] ← Static IP
    ├─ API Server (port 5000)
    ├─ yt-dlp
    ├─ ffmpeg
    └─ Downloads
```

## Benefits vs Standalone APK

| Feature | Standalone | Remote |
|---------|-----------|--------|
| Build complexity | ❌ Very hard | ✅ Easy |
| APK size | ❌ 50+ MB | ✅ ~10 MB |
| YouTube downloads | ❌ Doesn't work | ✅ Full yt-dlp |
| Storage | ❌ Phone only | ✅ VM (unlimited) |
| Processing power | ❌ Phone CPU | ✅ VM CPU |
| Battery usage | ❌ Drains battery | ✅ Minimal |

## Cost Estimate

- **VM running**: ~$0.05/hour
- **VM stopped**: ~$0.002/day (static IP)
- **Cloud Function**: ~$0 (free tier: 2M requests/month)
- **Network egress**: ~$0.12/GB downloaded to phone

**Typical usage**: Start VM → Queue 5 videos → Stop VM = ~$0.10

Much cheaper than always-on server!

## Troubleshooting

### "Failed to check VM status"
- Check Cloud Function URL is correct
- Check API Key is correct
- Check internet connection

### "Server not running"
- VM is stopped - tap "Start Server"
- Wait 30-60 seconds for boot

### "Failed to queue download"
- Check VM is running
- Check Static IP is correct
- Check firewall allows port 5000

### Downloads not appearing
- Tap "Refresh Downloads"
- Check VM API is running: `sudo systemctl status download-api`

## Security Notes

- API Key authenticates phone → Cloud Function
- Cloud Function has GCP credentials (not exposed to phone)
- VM API is open on port 5000 (add auth if needed)
- Static IP is public but requires knowing API endpoints

For production, consider:
- Adding authentication to VM API
- Using VPN or private networking
- Rate limiting on Cloud Function
