<!-- markdownlint-disable MD004 MD009 MD012 MD022 MD024 MD026 MD028 MD029 MD032 MD047 MD031 MD033 MD034 MD036 MD040 MD041 MD058-->

# GitHub Actions APK Build Guide

## What This Does
Automatically builds your Android APK using GitHub's free cloud servers - **no local installation needed!**

## Setup Steps

### 1. Create GitHub Repository

If you don't have one yet:

1. Go to https://github.com/new
2. Repository name: `ngk-download-manager` (or your choice)
3. Set to **Public** or **Private** (both work)
4. Click **Create repository**

### 2. Push Your Code to GitHub

Open PowerShell in your project folder:

```powershell
cd "c:\Users\suppo\Desktop\NGKsSystems\NGKs DL Manager"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit with mobile app and GitHub Actions"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ngk-download-manager.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** If you get authentication errors, use a Personal Access Token instead of password:
- GitHub → Settings → Developer settings → Personal access tokens → Generate new token
- Use token as password when prompted

### 3. Trigger the Build

The APK will build automatically when you push code. You can also trigger manually:

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Click **Build Android APK** workflow
4. Click **Run workflow** button
5. Click green **Run workflow**

### 4. Download Your APK

After ~30-60 minutes (first build):

1. Go to **Actions** tab
2. Click on the completed workflow run
3. Scroll to **Artifacts** section
4. Download **NGKs-Download-Manager-APK.zip**
5. Extract and install the APK on your Android device

## Build Times

- **First build:** 30-60 minutes (GitHub downloads SDK/NDK)
- **Subsequent builds:** 10-20 minutes (uses cache)

## Updating the APK

After making changes to your code:

```powershell
# Stage changes
git add .

# Commit changes
git commit -m "Update download manager features"

# Push to GitHub (triggers automatic build)
git push
```

GitHub will automatically build a new APK!

## Viewing Build Progress

1. Go to **Actions** tab in your repository
2. Click on the running workflow
3. Click **build** job
4. Expand steps to see real-time logs

## Troubleshooting

### Build Fails

Check the **Actions** tab for error logs. Common issues:

- **Buildozer spec errors:** Check `buildozer.spec` syntax
- **Missing dependencies:** Workflow installs all needed packages
- **Timeout:** First build can take 60+ min, GitHub may timeout (just re-run)

### Can't Push to GitHub

```powershell
# If remote already exists
git remote set-url origin https://github.com/YOUR_USERNAME/ngk-download-manager.git

# Force push if needed
git push -f origin main
```

### Build Succeeds but No APK

The APK is in the **Artifacts** section at the bottom of the workflow run page, not in the repository files.

## Creating Releases (Optional)

To create downloadable releases:

```powershell
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0
```

GitHub will automatically create a release with the APK attached!

## Cost

**FREE!** GitHub Actions provides:
- 2,000 minutes/month for private repos
- Unlimited minutes for public repos

Each build uses ~30-60 minutes, so you can build **many times** per month.

## Advanced: Build on Every Commit

The workflow is already configured to build on:
- ✅ Push to `main` or `master` branch
- ✅ Pull requests
- ✅ Manual trigger
- ✅ Tag pushes (creates releases)

## File Structure

```
NGKs DL Manager/
├── .github/
│   └── workflows/
│       └── build-apk.yml    ← GitHub Actions workflow
├── mobile_app.py            ← Your Kivy app
├── buildozer.spec           ← APK configuration
└── (all other files)
```

## Security Notes

- The workflow file (`.github/workflows/build-apk.yml`) is safe to commit
- No secrets or API keys needed for basic builds
- APK artifacts auto-delete after 30 days (configurable)

## Quick Reference

```powershell
# Push code → triggers build
git add .
git commit -m "Your message"
git push

# Create release with APK
git tag v1.0.1
git push origin v1.0.1

# Check build status
# Go to: https://github.com/YOUR_USERNAME/ngk-download-manager/actions
```

## Next Steps

1. Push your code to GitHub
2. Go to **Actions** tab and watch the build
3. Download the APK from **Artifacts**
4. Install on your Android device
5. Make changes and push again - automatic builds! 🚀

---

**No Windows downloads needed!** GitHub does all the heavy lifting in the cloud.
