[app]

# (str) Title of your application
title = NGK's Download Manager

# (str) Package name
package.name = ngkdownloader

# (str) Package domain (needed for android/ios packaging)
package.domain = org.ngks.downloader

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,images/*.png

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
# Mobile app is now a remote controller - no yt-dlp needed
requirements = python3,kivy,requests

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (landscape, sensorLandscape, portrait, sensorPortrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 30

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25c

# (int) Android SDK version to use
android.sdk = 30

# (str) python-for-android bootstrap to use
p4a.bootstrap = sdl2

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Python Service
android.service_main_class = org.kivy.android.PythonService

# (str) Android app theme, default is ok for Kivy-based app
android.theme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
android.whitelist_src = main.py,mobile_app.py

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
android.enable_androidx = True

# (list) Android application meta-data to set (key=value format)
android.meta_data = com.google.android.gms.version=@integer/google_play_services_version

# (list) Gradle dependencies to add
android.gradle_dependencies = 

# (list) add java compile options
android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (list) Gradle repositories to add {can be necessary for some android specific libraries}
android.gradle_repositories = google(), mavenCentral(), maven { url 'https://www.jitpack.io' }

# (str) python-for-android fork to use, defaults to upstream (kivy)
#p4a.fork = kivy

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port =

# Control passing the --private-data-dir to p4a
#p4a.private_data_dir = True

# Pass a custom "--copy-libs" to p4a
#p4a.copy_libs = True

# (bool) Whether or not to run tests
run_tests = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1