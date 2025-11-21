"""
NGK's Download Manager - Mobile Remote Controller
Controls download server running on GCE VM
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
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
import threading
import requests
import os
import sys
from datetime import datetime

# Configuration - Update these with your values
CLOUD_FUNCTION_URL = "https://us-central1-YOUR_PROJECT.cloudfunctions.net/vm-control"
API_KEY = "your-api-key-here"  # From Cloud Function deployment
VM_STATIC_IP = "136.114.215.21"  # Your VM's static IP
VM_API_PORT = "5000"

class MainScreen(Screen):
    """Main screen with tabs for Downloads and Files"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vm_status = 'unknown'
        self.vm_ip = None
        
        self.build_ui()
        
        # Check VM status on startup
        Clock.schedule_once(lambda dt: self.check_vm_status(), 1)
    
    def build_ui(self):
        """Build the main UI"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header with VM control
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
        
        title = Label(
            text="NGK's Download Manager",
            font_size='24sp',
            size_hint_y=None,
            height=40,
            bold=True
        )
        header.add_widget(title)
        
        # VM Status row
        status_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        
        self.vm_status_label = Label(
            text="VM: Checking...",
            size_hint_x=0.5
        )
        status_row.add_widget(self.vm_status_label)
        
        self.start_vm_btn = Button(
            text="Start Server",
            size_hint_x=0.25,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.start_vm_btn.bind(on_press=self.start_vm)
        status_row.add_widget(self.start_vm_btn)
        
        self.stop_vm_btn = Button(
            text="Stop Server",
            size_hint_x=0.25,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        self.stop_vm_btn.bind(on_press=self.stop_vm)
        status_row.add_widget(self.stop_vm_btn)
        
        header.add_widget(status_row)
        main_layout.add_widget(header)
        
        # Tabbed panel
        tabs = TabbedPanel(do_default_tab=False)
        
        # Downloads tab
        downloads_tab = TabbedPanelItem(text='Downloads')
        downloads_tab.add_widget(self.build_downloads_tab())
        tabs.add_widget(downloads_tab)
        
        # Files tab
        files_tab = TabbedPanelItem(text='Files')
        files_tab.add_widget(self.build_files_tab())
        tabs.add_widget(files_tab)
        
        main_layout.add_widget(tabs)
        self.add_widget(main_layout)
    
    def build_downloads_tab(self):
        """Build downloads tab"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # URL Input
        url_section = BoxLayout(orientation='vertical', size_hint_y=None, height=150, spacing=5)
        
        url_label = Label(text="Enter URL:", size_hint_y=None, height=30)
        url_section.add_widget(url_label)
        
        self.url_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=50,
            hint_text="YouTube, HuggingFace, or direct URL"
        )
        url_section.add_widget(self.url_input)
        
        # Quality selector
        quality_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        quality_label = Label(text="Quality:", size_hint_x=0.3)
        quality_row.add_widget(quality_label)
        
        self.quality_spinner = Spinner(
            text='best',
            values=['best', '720p', '480p', 'audio'],
            size_hint_x=0.7
        )
        quality_row.add_widget(self.quality_spinner)
        url_section.add_widget(quality_row)
        
        layout.add_widget(url_section)
        
        # Download button
        self.download_btn = Button(
            text="Queue Download",
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.download_btn.bind(on_press=self.queue_download)
        layout.add_widget(self.download_btn)
        
        # Downloads list
        list_label = Label(text="Active Downloads:", size_hint_y=None, height=30)
        layout.add_widget(list_label)
        
        scroll = ScrollView()
        self.downloads_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.downloads_list.bind(minimum_height=self.downloads_list.setter('height'))
        scroll.add_widget(self.downloads_list)
        layout.add_widget(scroll)
        
        # Refresh button
        refresh_btn = Button(
            text="Refresh Downloads",
            size_hint_y=None,
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        refresh_btn.bind(on_press=lambda x: self.refresh_downloads())
        layout.add_widget(refresh_btn)
        
        return layout
    
    def build_files_tab(self):
        """Build files browser tab"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        files_label = Label(text="Downloaded Files:", size_hint_x=0.7)
        header.add_widget(files_label)
        
        refresh_files_btn = Button(
            text="Refresh",
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        refresh_files_btn.bind(on_press=lambda x: self.refresh_files())
        header.add_widget(refresh_files_btn)
        layout.add_widget(header)
        
        # Files list
        scroll = ScrollView()
        self.files_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.files_list.bind(minimum_height=self.files_list.setter('height'))
        scroll.add_widget(self.files_list)
        layout.add_widget(scroll)
        
        return layout
    
    def check_vm_status(self):
        """Check VM status via Cloud Function"""
        def worker():
            try:
                response = requests.get(
                    f"{CLOUD_FUNCTION_URL}/vm-status",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.vm_status = data.get('status', 'unknown')
                    self.vm_ip = data.get('ip')
                    
                    Clock.schedule_once(lambda dt: self.update_vm_status_ui())
                    
                    # If running, refresh downloads
                    if self.vm_status == 'running':
                        Clock.schedule_once(lambda dt: self.refresh_downloads())
                else:
                    Clock.schedule_once(lambda dt: self.show_error(f"Failed to check VM status: {response.status_code}"))
                    
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(f"Error checking VM: {str(e)}"))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def update_vm_status_ui(self):
        """Update VM status in UI"""
        if self.vm_status == 'running':
            self.vm_status_label.text = f"VM: Running ({self.vm_ip})"
            self.vm_status_label.color = (0, 1, 0, 1)  # Green
            self.start_vm_btn.disabled = True
            self.stop_vm_btn.disabled = False
            self.download_btn.disabled = False
        elif self.vm_status == 'terminated':
            self.vm_status_label.text = "VM: Stopped"
            self.vm_status_label.color = (1, 0, 0, 1)  # Red
            self.start_vm_btn.disabled = False
            self.stop_vm_btn.disabled = True
            self.download_btn.disabled = True
        else:
            self.vm_status_label.text = f"VM: {self.vm_status.title()}"
            self.vm_status_label.color = (1, 1, 0, 1)  # Yellow
            self.start_vm_btn.disabled = True
            self.stop_vm_btn.disabled = True
            self.download_btn.disabled = True
    
    def start_vm(self, instance):
        """Start the VM"""
        def worker():
            try:
                self.show_info("Starting server...")
                
                response = requests.post(
                    f"{CLOUD_FUNCTION_URL}/start-vm",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.show_info("Server starting... Please wait 30-60 seconds"))
                    # Poll for status
                    Clock.schedule_once(lambda dt: self.poll_vm_ready(), 5)
                else:
                    Clock.schedule_once(lambda dt: self.show_error(f"Failed to start: {response.text}"))
                    
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def stop_vm(self, instance):
        """Stop the VM"""
        def worker():
            try:
                response = requests.post(
                    f"{CLOUD_FUNCTION_URL}/stop-vm",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.show_info("Server stopping..."))
                    Clock.schedule_once(lambda dt: self.check_vm_status(), 2)
                else:
                    Clock.schedule_once(lambda dt: self.show_error(f"Failed to stop: {response.text}"))
                    
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def poll_vm_ready(self, attempt=0):
        """Poll until VM is ready"""
        if attempt > 20:  # Max 2 minutes
            self.show_error("VM took too long to start")
            return
        
        def worker():
            try:
                response = requests.get(
                    f"{CLOUD_FUNCTION_URL}/vm-status",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ready'):
                        self.vm_status = 'running'
                        self.vm_ip = data.get('ip')
                        Clock.schedule_once(lambda dt: self.update_vm_status_ui())
                        Clock.schedule_once(lambda dt: self.show_info("Server is ready!"))
                        Clock.schedule_once(lambda dt: self.refresh_downloads())
                    else:
                        # Keep polling
                        Clock.schedule_once(lambda dt: self.poll_vm_ready(attempt + 1), 6)
            except:
                Clock.schedule_once(lambda dt: self.poll_vm_ready(attempt + 1), 6)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def queue_download(self, instance):
        """Queue a download on the server"""
        url = self.url_input.text.strip()
        if not url:
            self.show_error("Please enter a URL")
            return
        
        if self.vm_status != 'running':
            self.show_error("Server is not running. Please start it first.")
            return
        
        def worker():
            try:
                api_url = f"http://{VM_STATIC_IP}:{VM_API_PORT}"
                
                response = requests.post(
                    f"{api_url}/download",
                    json={
                        "url": url,
                        "quality": self.quality_spinner.text
                    },
                    timeout=10
                )
                
                if response.status_code == 201:
                    Clock.schedule_once(lambda dt: self.show_info("Download queued!"))
                    Clock.schedule_once(lambda dt: self.clear_url_input())
                    Clock.schedule_once(lambda dt: self.refresh_downloads(), 1)
                else:
                    Clock.schedule_once(lambda dt: self.show_error(f"Failed: {response.text}"))
                    
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def clear_url_input(self):
        """Clear URL input"""
        self.url_input.text = ""
    
    def refresh_downloads(self):
        """Refresh downloads list"""
        if self.vm_status != 'running':
            return
        
        def worker():
            try:
                api_url = f"http://{VM_STATIC_IP}:{VM_API_PORT}"
                response = requests.get(f"{api_url}/downloads", timeout=10)
                
                if response.status_code == 200:
                    downloads = response.json()
                    Clock.schedule_once(lambda dt: self.update_downloads_ui(downloads))
            except:
                pass  # Silently fail on refresh
        
        threading.Thread(target=worker, daemon=True).start()
    
    def update_downloads_ui(self, downloads):
        """Update downloads list UI"""
        self.downloads_list.clear_widgets()
        
        if not downloads:
            self.downloads_list.add_widget(Label(
                text="No downloads yet",
                size_hint_y=None,
                height=40
            ))
            return
        
        # Sort by most recent
        sorted_downloads = sorted(
            downloads.items(),
            key=lambda x: x[1].get('added_at', ''),
            reverse=True
        )
        
        for download_id, info in sorted_downloads[:20]:  # Show last 20
            item = self.create_download_item(download_id, info)
            self.downloads_list.add_widget(item)
    
    def create_download_item(self, download_id, info):
        """Create download item widget"""
        layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=80,
            padding=5,
            spacing=2
        )
        
        # Filename
        filename = info.get('filename', 'Unknown')
        name_label = Label(
            text=filename[:50] + "..." if len(filename) > 50 else filename,
            size_hint_y=None,
            height=25,
            halign='left'
        )
        layout.add_widget(name_label)
        
        # Progress bar
        progress = info.get('progress_percent', 0)
        progress_bar = ProgressBar(
            max=100,
            value=progress,
            size_hint_y=None,
            height=15
        )
        layout.add_widget(progress_bar)
        
        # Status row
        status_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        
        status = info.get('status', 'unknown')
        status_label = Label(
            text=f"{status.title()} - {progress:.0f}%",
            size_hint_x=0.5,
            halign='left'
        )
        status_row.add_widget(status_label)
        
        speed = info.get('speed', '')
        speed_label = Label(
            text=speed,
            size_hint_x=0.5,
            halign='right'
        )
        status_row.add_widget(speed_label)
        
        layout.add_widget(status_row)
        
        return layout
    
    def refresh_files(self):
        """Refresh files list"""
        if self.vm_status != 'running':
            self.show_error("Server not running")
            return
        
        def worker():
            try:
                api_url = f"http://{VM_STATIC_IP}:{VM_API_PORT}"
                response = requests.get(f"{api_url}/files", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    files = data.get('files', [])
                    Clock.schedule_once(lambda dt: self.update_files_ui(files))
                else:
                    Clock.schedule_once(lambda dt: self.show_error("Failed to fetch files"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def update_files_ui(self, files):
        """Update files list UI"""
        self.files_list.clear_widgets()
        
        if not files:
            self.files_list.add_widget(Label(
                text="No files yet",
                size_hint_y=None,
                height=40
            ))
            return
        
        for file_info in files:
            item = self.create_file_item(file_info)
            self.files_list.add_widget(item)
    
    def create_file_item(self, file_info):
        """Create file item widget"""
        layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            padding=5,
            spacing=10
        )
        
        # File info
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        name = file_info.get('name', 'Unknown')
        name_label = Label(
            text=name[:40] + "..." if len(name) > 40 else name,
            size_hint_y=None,
            height=30,
            halign='left'
        )
        info_layout.add_widget(name_label)
        
        size = file_info.get('size', 0)
        size_mb = size / (1024 * 1024)
        size_label = Label(
            text=f"{size_mb:.1f} MB",
            size_hint_y=None,
            height=30,
            halign='left'
        )
        info_layout.add_widget(size_label)
        
        layout.add_widget(info_layout)
        
        # Download button
        download_btn = Button(
            text="Download",
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 1, 1)
        )
        download_btn.bind(on_press=lambda x: self.download_file(file_info))
        layout.add_widget(download_btn)
        
        return layout
    
    def download_file(self, file_info):
        """Download file from server to phone"""
        self.show_info(f"Downloading {file_info['name']}...")
        # TODO: Implement file download to phone storage
        # This would use requests to fetch the file and save it locally
    
    def show_info(self, message):
        """Show info popup"""
        popup = Popup(
            title='Info',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()

class NGKRemoteApp(App):
    """Main Kivy application"""
    
    def build(self):
        """Build the app"""
        sm = ScreenManager()
        main_screen = MainScreen(name='main')
        sm.add_widget(main_screen)
        return sm

if __name__ == '__main__':
    NGKRemoteApp().run()
