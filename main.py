#!/usr/bin/env python3
"""
Transparent Streaming Chat Overlay
Creates an always-on-top, click-through overlay window that displays a chat widget.
"""

import tkinter as tk
from tkinter import messagebox
import win32gui
import win32con
import webview
import threading
import sys
import os
from urllib.parse import urlparse

class ChatOverlay:
    def __init__(self, chat_url="https://botrix.live/embed/chat"):
        self.chat_url = chat_url
        self.root = None
        self.webview_window = None
        self.window_handle = None
        
    def validate_url(self, url):
        """Validate the provided URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def create_overlay_window(self):
        """Create the main Tkinter overlay window"""
        self.root = tk.Tk()
        
        # Configure window properties
        self.root.title("Chat Overlay")
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.01)  # Make nearly transparent (can't be 0 or webview won't work)
        
        # Get screen dimensions and make fullscreen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.configure(bg='black')
        
        # Create a frame to hold the webview
        self.webview_frame = tk.Frame(self.root, bg='black')
        self.webview_frame.pack(fill=tk.BOTH, expand=True)
        
        return screen_width, screen_height
    
    def apply_click_through(self):
        """Apply Windows-specific flags to make the window click-through"""
        try:
            # Get the window handle
            self.window_handle = win32gui.FindWindow(None, "Chat Overlay")
            
            if self.window_handle:
                # Get current window style
                current_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)
                
                # Add layered and transparent flags
                new_style = current_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
                
                # Apply the new style
                win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                
                # Set window transparency
                win32gui.SetLayeredWindowAttributes(
                    self.window_handle, 
                    0,  # Color key (not used)
                    255,  # Alpha value (255 = opaque)
                    win32con.LWA_ALPHA
                )
                
                print("Click-through mode activated!")
                return True
            else:
                print("Warning: Could not find window handle")
                return False
                
        except Exception as e:
            print(f"Error applying click-through: {e}")
            return False
    
    def create_webview(self, width, height):
        """Create the webview in a separate thread"""
        def webview_thread():
            try:
                # Create webview window
                self.webview_window = webview.create_window(
                    title='Chat Widget',
                    url=self.chat_url,
                    width=width,
                    height=height,
                    x=0,
                    y=0,
                    resizable=True,
                    fullscreen=False,
                    shadow=False,
                    on_top=True,
                    transparent=True
                )
                
                # Start webview
                webview.start(debug=False)
                
            except Exception as e:
                print(f"Error creating webview: {e}")
                messagebox.showerror("Error", f"Failed to create webview: {e}")
        
        # Start webview in separate thread
        webview_thread_obj = threading.Thread(target=webview_thread, daemon=True)
        webview_thread_obj.start()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for controlling the overlay"""
        def toggle_click_through(event=None):
            """Toggle click-through mode on/off"""
            if self.window_handle:
                current_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)
                
                if current_style & win32con.WS_EX_TRANSPARENT:
                    # Remove click-through
                    new_style = current_style & ~win32con.WS_EX_TRANSPARENT
                    win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                    print("Click-through disabled")
                else:
                    # Enable click-through
                    new_style = current_style | win32con.WS_EX_TRANSPARENT
                    win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                    print("Click-through enabled")
        
        def close_overlay(event=None):
            """Close the overlay"""
            print("Closing overlay...")
            if self.webview_window:
                webview.destroy()
            self.root.quit()
            sys.exit(0)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-t>', toggle_click_through)  # Ctrl+T to toggle click-through
        self.root.bind('<Control-q>', close_overlay)  # Ctrl+Q to quit
        self.root.bind('<Escape>', close_overlay)  # Escape to quit
        
        # Make sure the window can receive focus for keyboard events
        self.root.focus_force()
    
    def run(self):
        """Start the chat overlay application"""
        print("Starting Chat Overlay...")
        print(f"Loading URL: {self.chat_url}")
        
        # Validate URL
        if not self.validate_url(self.chat_url):
            print("Error: Invalid URL provided")
            return
        
        try:
            # Create the overlay window
            width, height = self.create_overlay_window()
            
            # Setup keyboard shortcuts
            self.setup_keyboard_shortcuts()
            
            # Apply click-through after a short delay
            self.root.after(1000, self.apply_click_through)
            
            # Create webview
            self.create_webview(width, height)
            
            print("\nOverlay Controls:")
            print("- Ctrl+T: Toggle click-through mode")
            print("- Ctrl+Q or Escape: Close overlay")
            print("- The overlay should now be visible and click-through")
            
            # Start the Tkinter main loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"Error starting overlay: {e}")
            messagebox.showerror("Error", f"Failed to start overlay: {e}")

def main():
    """Main entry point"""
    # Default to Kick chat URL for deashad
    default_url = "https://kick.com/popout/deashad/chat"
    
    # Check if URL was provided as command line argument
    if len(sys.argv) > 1:
        chat_url = sys.argv[1]
        print(f"Using provided URL: {chat_url}")
    else:
        chat_url = default_url
        print(f"Using default Kick chat URL: {chat_url}")
    
    # Create and run the overlay
    overlay = ChatOverlay(chat_url)
    overlay.run()

if __name__ == "__main__":
    main()
