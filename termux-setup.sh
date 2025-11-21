#!/data/data/com.termux/files/usr/bin/bash
# Termux Setup Script for NGK's Download Manager
# Run this script in Termux to set up everything needed

echo "=========================================="
echo "NGK's Download Manager - Termux Setup"
echo "=========================================="
echo ""

# Update package lists
echo "[1/5] Updating package lists..."
pkg update -y

# Install required packages
echo "[2/5] Installing Python, FFmpeg, and Git..."
pkg install -y python ffmpeg git openssh

# Install Python packages
echo "[3/5] Installing Python dependencies..."
pip install --upgrade pip
pip install yt-dlp requests

# Setup storage access (allows access to phone storage)
echo "[4/5] Setting up storage access..."
termux-setup-storage

# Clone or update repository
echo "[5/5] Repository setup..."
if [ -d "ngk-download-manager" ]; then
    echo "Repository exists, pulling latest changes..."
    cd ngk-download-manager
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/NGKsSystems/ngk-download-manager.git
    cd ngk-download-manager
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To run the download manager:"
echo "  cd ngk-download-manager"
echo "  python download_manager.py"
echo ""
echo "Your downloads will be saved to:"
echo "  ~/storage/downloads/"
echo ""
echo "To access your phone's storage:"
echo "  ~/storage/shared/"
echo ""
