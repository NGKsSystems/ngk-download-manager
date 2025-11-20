"""
NGK's Download Manager - Mobile (Kivy) Version
Android-compatible version with touch-friendly interface
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
import threading
import os
import sys

# Import your existing download modules
from youtube_downloader import YouTubeDownloader
from huggingface_downloader import HuggingFaceDownloader
from download_manager import DownloadManager
from utils import URLDetector

class DownloadScreen(Screen):
    """Main download screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.downloaders = {
            'youtube': YouTubeDownloader(),
            'hf': HuggingFaceDownloader(),
            'direct': DownloadManager()
        }
        self.url_detector = URLDetector()
        self.active_downloads = {}
        self.download_counter = 0
        
        self.build_ui()
    
    def build_ui(self):
        """Build the mobile-friendly UI"""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text="NGK's Download Manager",
            font_size='24sp',
            size_hint_y=None,
            height=60,
            bold=True
        )
        main_layout.add_widget(title)
        
        # URL Input Section
        url_section = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
        
        url_label = Label(text="Enter URL:", size_hint_y=None, height=30, halign='left')
        url_section.add_widget(url_label)
        
        self.url_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=50,
            hint_text="Paste YouTube, HuggingFace, or direct URL here"
        )
        self.url_input.bind(text=self.on_url_change)
        url_section.add_widget(self.url_input)
        
        self.url_info_label = Label(
            text="",
            size_hint_y=None,
            height=30,
            color=(0, 0.5, 1, 1)  # Blue color
        )
        url_section.add_widget(self.url_info_label)
        
        main_layout.add_widget(url_section)
        
        # Quality Selection
        quality_section = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        quality_label = Label(text="Quality:", size_hint_x=None, width=80)
        quality_section.add_widget(quality_label)
        
        self.quality_spinner = Spinner(
            text='Auto',
            values=['Best Quality', '720p', '480p', 'Audio Only (MP3)', 'Auto'],
            size_hint_x=1
        )
        quality_section.add_widget(self.quality_spinner)
        
        main_layout.add_widget(quality_section)
        
        # Download Button
        self.download_btn = Button(
            text="Download",
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.8, 0.2, 1)  # Green
        )
        self.download_btn.bind(on_press=self.start_download)
        main_layout.add_widget(self.download_btn)
        
        # Progress Section
        progress_label = Label(
            text="Downloads:",
            size_hint_y=None,
            height=40,
            halign='left'
        )
        main_layout.add_widget(progress_label)
        
        # Scrollable download list
        scroll = ScrollView()
        self.download_list = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.download_list.bind(minimum_height=self.download_list.setter('height'))
        scroll.add_widget(self.download_list)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def on_url_change(self, instance, text):
        """Handle URL input change"""
        if text.strip():
            url_type = self.url_detector.detect_url_type(text.strip())
            self.url_info_label.text = f"Detected: {url_type}"
        else:
            self.url_info_label.text = ""
    
    def start_download(self, instance):
        """Start download process"""
        url = self.url_input.text.strip()
        if not url:
            self.show_popup("Error", "Please enter a URL")
            return
        
        # Detect URL type
        url_type = self.url_detector.detect_url_type(url)
        quality = self.quality_spinner.text
        
        # Create download entry
        download_id = self.download_counter
        self.download_counter += 1
        
        # Create progress widget
        progress_widget = self.create_progress_widget(download_id, url, url_type)
        self.download_list.add_widget(progress_widget)
        
        # Store download info
        self.active_downloads[download_id] = {
            'widget': progress_widget,
            'url': url,
            'type': url_type,
            'quality': quality
        }
        
        # Start download in thread
        if url_type == "YouTube":
            thread = threading.Thread(
                target=self.youtube_download_worker,
                args=(download_id, url, quality),
                daemon=True
            )
        elif url_type == "Hugging Face":
            thread = threading.Thread(
                target=self.hf_download_worker,
                args=(download_id, url),
                daemon=True
            )
        else:
            thread = threading.Thread(
                target=self.direct_download_worker,
                args=(download_id, url),
                daemon=True
            )
        
        thread.start()
        
        # Clear input
        self.url_input.text = ""
        self.url_info_label.text = ""
    
    def create_progress_widget(self, download_id, url, url_type):
        """Create a progress display widget"""
        widget = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            spacing=5
        )
        
        # Info row
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        
        filename_label = Label(
            text="Preparing...",
            size_hint_x=0.7,
            halign='left'
        )
        info_layout.add_widget(filename_label)
        
        type_label = Label(
            text=url_type,
            size_hint_x=0.3,
            halign='right'
        )
        info_layout.add_widget(type_label)
        
        widget.add_widget(info_layout)
        
        # Progress bar
        progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=20
        )
        widget.add_widget(progress_bar)
        
        # Status row
        status_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        
        progress_label = Label(
            text="0%",
            size_hint_x=0.3,
            halign='left'
        )
        status_layout.add_widget(progress_label)
        
        speed_label = Label(
            text="0 B/s",
            size_hint_x=0.4,
            halign='center'
        )
        status_layout.add_widget(speed_label)
        
        status_label = Label(
            text="Starting",
            size_hint_x=0.3,
            halign='right'
        )
        status_layout.add_widget(status_label)
        
        widget.add_widget(status_layout)
        
        # Store references for updates
        widget._filename_label = filename_label
        widget._progress_bar = progress_bar
        widget._progress_label = progress_label
        widget._speed_label = speed_label
        widget._status_label = status_label
        
        return widget
    
    def update_progress(self, download_id, progress_info):
        """Update progress display"""
        if download_id not in self.active_downloads:
            return
        
        widget = self.active_downloads[download_id]['widget']
        
        # Update filename if available
        if 'filename' in progress_info:
            widget._filename_label.text = progress_info['filename'][:50] + "..." if len(progress_info['filename']) > 50 else progress_info['filename']
        
        # Update progress
        if 'progress' in progress_info:
            progress_text = progress_info['progress']
            if progress_text.endswith('%'):
                try:
                    progress_value = float(progress_text[:-1])
                    widget._progress_bar.value = progress_value
                except:
                    pass
            widget._progress_label.text = progress_text
        
        # Update speed
        if 'speed' in progress_info:
            widget._speed_label.text = progress_info['speed']
        
        # Update status
        if 'status' in progress_info:
            widget._status_label.text = progress_info['status']
    
    def youtube_download_worker(self, download_id, url, quality):
        """Worker for YouTube downloads"""
        try:
            def progress_callback(progress_info):
                Clock.schedule_once(lambda dt: self.update_progress(download_id, progress_info))
            
            # Map quality selection
            audio_only = (quality == "Audio Only (MP3)")
            
            # Get download directory (use app's directory on mobile)
            download_dir = self.get_download_directory()
            
            result = self.downloaders['youtube'].download(
                url, download_dir, progress_callback,
                extract_audio=audio_only,
                auto_quality=True
            )
            
            Clock.schedule_once(lambda dt: self.download_completed(download_id, result))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.download_failed(download_id, str(e)))
    
    def hf_download_worker(self, download_id, url):
        """Worker for HuggingFace downloads"""
        try:
            def progress_callback(progress_info):
                Clock.schedule_once(lambda dt: self.update_progress(download_id, progress_info))
            
            download_dir = self.get_download_directory()
            
            result = self.downloaders['hf'].download(
                url, download_dir, progress_callback
            )
            
            Clock.schedule_once(lambda dt: self.download_completed(download_id, result))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.download_failed(download_id, str(e)))
    
    def direct_download_worker(self, download_id, url):
        """Worker for direct downloads"""
        try:
            def progress_callback(progress_info):
                Clock.schedule_once(lambda dt: self.update_progress(download_id, progress_info))
            
            download_dir = self.get_download_directory()
            
            result = self.downloaders['direct'].download(
                url, download_dir, progress_callback
            )
            
            Clock.schedule_once(lambda dt: self.download_completed(download_id, result))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.download_failed(download_id, str(e)))
    
    def get_download_directory(self):
        """Get appropriate download directory for platform"""
        if hasattr(sys, '_MEIPASS'):  # Running as compiled app
            # For Android, use external storage
            download_dir = "/storage/emulated/0/Download"
        else:
            # For desktop testing, use same subfolder as desktop app currently uses
            download_dir = os.path.expanduser("~/Downloads/NGK_Downloads")
        
        os.makedirs(download_dir, exist_ok=True)
        return download_dir
    
    def download_completed(self, download_id, result):
        """Handle download completion"""
        if download_id in self.active_downloads:
            widget = self.active_downloads[download_id]['widget']
            widget._progress_bar.value = 100
            widget._progress_label.text = "100%"
            widget._status_label.text = "Completed"
            
            if isinstance(result, dict) and result.get('filename'):
                widget._filename_label.text = result['filename']
    
    def download_failed(self, download_id, error):
        """Handle download failure"""
        if download_id in self.active_downloads:
            widget = self.active_downloads[download_id]['widget']
            widget._status_label.text = "Failed"
            widget._speed_label.text = ""
        
        self.show_popup("Download Failed", f"Error: {error}")
    
    def show_popup(self, title, message):
        """Show popup message"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class NGKDownloadApp(App):
    """Main Kivy application"""
    
    def build(self):
        """Build the app"""
        sm = ScreenManager()
        download_screen = DownloadScreen(name='download')
        sm.add_widget(download_screen)
        return sm

if __name__ == '__main__':
    NGKDownloadApp().run()