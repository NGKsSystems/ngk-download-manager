# VM API Server Setup

## What This Does
REST API server that runs on your GCE VM, allowing the phone app to:
- Queue downloads
- Check download progress
- List downloaded files
- Download files to phone

## Installation on VM

### 1. SSH into your VM
```bash
gcloud compute ssh instance-20251120-182738 --zone=us-central1-a
```

### 2. Install Dependencies
```bash
# Update system
sudo apt update

# Install Python and pip if not already installed
sudo apt install python3-pip -y

# Navigate to your download manager directory
cd /path/to/NGKs\ DL\ Manager

# Install Flask and CORS
pip3 install flask flask-cors
```

### 3. Configure Firewall
```bash
# Allow port 5000 from anywhere
gcloud compute firewall-rules create allow-download-api \
    --allow=tcp:5000 \
    --source-ranges=0.0.0.0/0 \
    --description="Allow Download Manager API access"
```

### 4. Create Systemd Service (Auto-start on boot)

Create service file:
```bash
sudo nano /etc/systemd/system/download-api.service
```

Paste this content:
```ini
[Unit]
Description=NGK Download Manager API
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/NGKs DL Manager
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/NGKs DL Manager/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME` with your actual username!**

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable download-api
sudo systemctl start download-api
```

### 5. Check Status
```bash
# Check if service is running
sudo systemctl status download-api

# View logs
sudo journalctl -u download-api -f
```

## Testing

### From VM itself:
```bash
# Health check
curl http://localhost:5000/health

# List downloads
curl http://localhost:5000/downloads

# List files
curl http://localhost:5000/files
```

### From your phone/computer (replace with your VM's IP):
```bash
# Health check
curl http://136.114.215.21:5000/health

# Queue a download
curl -X POST http://136.114.215.21:5000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "quality": "best"}'

# Check status
curl http://136.114.215.21:5000/status/dl_20251120_120000_0

# List files
curl http://136.114.215.21:5000/files
```

## API Endpoints

### `GET /health`
Health check

### `POST /download`
Queue a new download
```json
{
  "url": "https://youtube.com/watch?v=...",
  "quality": "best|720p|480p|audio",
  "filename": "optional_custom_name"
}
```

### `GET /status/<download_id>`
Get download progress

### `GET /downloads`
List all downloads
- Optional query param: `?status=completed|active|failed`

### `GET /files`
List all downloaded files

### `GET /files/<path>`
Download a specific file
- Supports range requests for video streaming

### `DELETE /delete/<download_id>`
Remove download from database

### `GET /stats`
Get download statistics

## Stopping the Service

```bash
sudo systemctl stop download-api
```

## Updating the Code

```bash
# Pull latest changes
git pull

# Restart service
sudo systemctl restart download-api
```

## Troubleshooting

### Port already in use
```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill it
sudo kill -9 <PID>
```

### Permission errors
```bash
# Make sure downloads directory exists and is writable
mkdir -p ~/Downloads/NGK_Downloads
chmod 755 ~/Downloads/NGK_Downloads
```

### Check logs
```bash
sudo journalctl -u download-api -n 100 --no-pager
```
