# NGK's Download Manager - Mobile Version

## Testing on Desktop

First, test the mobile interface on your desktop:

```bash
python test_mobile.py
```

This will run the Kivy mobile interface on your desktop so you can test all functionality before building for Android.

## Building Android APK

### Prerequisites

1. **Install Buildozer** (on Linux/WSL):
   ```bash
   pip install buildozer
   ```

2. **Install Android SDK/NDK** (Buildozer will handle this automatically on first run)

3. **For Windows users**: Use Windows Subsystem for Linux (WSL) as Android building works best on Linux

### Building Steps

1. **Initialize buildozer** (first time only):
   ```bash
   buildozer init
   ```
   This creates buildozer.spec (already provided)

2. **Build debug APK**:
   ```bash
   buildozer android debug
   ```
   This will:
   - Download Android SDK/NDK if needed
   - Download Python-for-Android
   - Compile your app and dependencies
   - Create an APK file

3. **Build release APK** (for distribution):
   ```bash
   buildozer android release
   ```

### Output

The APK file will be created in:
- `bin/ngkdownloader-1.0-arm64-v8a-debug.apk` (debug)
- `bin/ngkdownloader-1.0-arm64-v8a-release-unsigned.apk` (release)

### Installation

Transfer the APK to your Android device and install it. You may need to enable "Install from Unknown Sources" in your Android settings.

## Features in Mobile Version

- **Touch-friendly interface**: Large buttons and input fields
- **All download types supported**: YouTube, HuggingFace, direct downloads
- **Quality selection**: Simple dropdown with 5 clear options
- **Progress tracking**: Real-time progress bars for each download
- **Mobile storage**: Downloads go to `/storage/emulated/0/Download/NGK_Downloads`
- **Background downloads**: Downloads continue even when app is minimized
- **Same quality**: Includes metadata embedding and proper file naming

## Troubleshooting

### Common Issues

1. **Import errors during testing**:
   ```bash
   pip install kivy requests yt-dlp pillow
   ```

2. **Buildozer fails on Windows**:
   - Use WSL (Windows Subsystem for Linux)
   - Install buildozer inside WSL

3. **Android permissions**:
   - The app requests storage permissions automatically
   - Grant permissions when prompted on first run

4. **Large APK size**:
   - The APK will be 50-100MB due to yt-dlp and dependencies
   - This is normal for Python-based Android apps

### Build Environment Setup (WSL)

If using Windows, set up WSL first:

```bash
# In PowerShell (as Administrator)
wsl --install

# After reboot, in WSL terminal:
sudo apt update
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade buildozer cython virtualenv

# Navigate to your project directory and build
cd /mnt/c/Users/suppo/Desktop/NGKsSystems/NGKs\ DL\ Manager/
buildozer android debug
```

## Differences from Desktop Version

- **Touch UI**: Larger touch targets, mobile-optimized layout
- **File storage**: Uses Android's Download folder instead of user's Downloads
- **Simplified menus**: Context menus replaced with touch gestures
- **Mobile permissions**: Handles Android storage permissions
- **Performance**: Optimized for mobile CPU/memory constraints

The core download functionality remains identical to the desktop version, including:
- YouTube downloads with metadata and album art embedding
- "Artist - Title.mp3" naming convention
- All supported quality options
- HuggingFace and direct download support