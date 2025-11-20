"""
Test the context menu functionality
"""

import tkinter as tk
from tkinter import ttk

def test_context_menu():
    root = tk.Tk()
    root.title("Context Menu Test")
    root.geometry("500x300")
    
    def setup_entry_context_menu(entry_widget):
        """Setup right-click context menu for entry widgets"""
        context_menu = tk.Menu(root, tearoff=0)
        
        def copy_text():
            try:
                if entry_widget.selection_present():
                    text = entry_widget.selection_get()
                    root.clipboard_clear()
                    root.clipboard_append(text)
                else:
                    # If no selection, copy all text
                    text = entry_widget.get()
                    root.clipboard_clear()
                    root.clipboard_append(text)
            except tk.TclError:
                pass
        
        def paste_text():
            try:
                clipboard_text = root.clipboard_get()
                if entry_widget.selection_present():
                    # Replace selection
                    entry_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    entry_widget.insert(tk.INSERT, clipboard_text)
                else:
                    # Insert at cursor
                    entry_widget.insert(tk.INSERT, clipboard_text)
            except tk.TclError:
                pass
        
        def cut_text():
            try:
                if entry_widget.selection_present():
                    text = entry_widget.selection_get()
                    root.clipboard_clear()
                    root.clipboard_append(text)
                    entry_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                pass
        
        def select_all():
            entry_widget.select_range(0, tk.END)
            entry_widget.icursor(tk.END)
        
        def clear_text():
            entry_widget.delete(0, tk.END)
        
        # Add menu items
        context_menu.add_command(label="Copy", command=copy_text, accelerator="Ctrl+C")
        context_menu.add_command(label="Paste", command=paste_text, accelerator="Ctrl+V")
        context_menu.add_command(label="Cut", command=cut_text, accelerator="Ctrl+X")
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=select_all, accelerator="Ctrl+A")
        context_menu.add_command(label="Clear", command=clear_text)
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        # Bind right-click to show menu
        entry_widget.bind("<Button-3>", show_context_menu)
        
        # Also add standard keyboard shortcuts
        entry_widget.bind("<Control-c>", lambda e: copy_text())
        entry_widget.bind("<Control-v>", lambda e: paste_text())
        entry_widget.bind("<Control-x>", lambda e: cut_text())
        entry_widget.bind("<Control-a>", lambda e: select_all())
    
    # Create test widgets
    ttk.Label(root, text="Right-click Context Menu Test", font=("Arial", 14, "bold")).pack(pady=20)
    
    ttk.Label(root, text="URL Entry (with context menu):").pack(anchor=tk.W, padx=20, pady=(10, 5))
    url_entry = ttk.Entry(root, width=60)
    url_entry.pack(padx=20, pady=5, fill=tk.X)
    url_entry.insert(0, "https://www.youtube.com/watch?v=example")
    setup_entry_context_menu(url_entry)
    
    ttk.Label(root, text="Token Entry (with context menu):").pack(anchor=tk.W, padx=20, pady=(10, 5))
    token_entry = ttk.Entry(root, width=60, show="*")
    token_entry.pack(padx=20, pady=5, fill=tk.X)
    token_entry.insert(0, "hf_example_token_12345")
    setup_entry_context_menu(token_entry)
    
    ttk.Label(root, text="Instructions:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=20, pady=(20, 5))
    instructions = """
• Right-click on any entry field to see context menu
• Use Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A for standard shortcuts
• Context menu includes: Copy, Paste, Cut, Select All, Clear
• Test by copying text between fields
    """
    ttk.Label(root, text=instructions, justify=tk.LEFT).pack(anchor=tk.W, padx=20, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_context_menu()