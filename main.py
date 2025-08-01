#!/usr/bin/env python3
"""
Transparent Streaming Chat Overlay - Resizable & Movable
Creates a small, resizable, movable overlay window that displays a chat widget.
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
    def __init__(self, chat_url="https://kick.com/popout/deashad/chat"):
        self.chat_url = chat_url
        self.root = None
        self.webview_window = None
        self.window_handle = None
        self.is_click_through = False
        self.start_x = 0
        self.start_y = 0
        
    def validate_url(self, url):
        """Validate the provided URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def start_move(self, event):
        """Start window dragging"""
        if not self.is_click_through:
            self.start_x = event.x
            self.start_y = event.y
    
    def on_move(self, event):
        """Handle window dragging"""
        if not self.is_click_through:
            x = self.root.winfo_x() + (event.x - self.start_x)
            y = self.root.winfo_y() + (event.y - self.start_y)
            self.root.geometry(f"+{x}+{y}")
    
    def create_overlay_window(self):
        """Create the main Tkinter overlay window"""
        self.root = tk.Tk()
        
        # Configure window properties
        self.root.title("Chat Overlay")
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.9)  # Semi-transparent
        
        # Set initial size and position
        width = 400
        height = 600
        x_pos = 100  # Sol üstten 100px
        y_pos = 100  # Üstten 100px
        
        self.root.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        
        # Transparent background
        self.root.configure(bg='#000000')
        self.root.attributes('-transparentcolor', '#000000')
        
        # Create a border frame for visibility
        border_frame = tk.Frame(self.root, bg='#333333', bd=1, relief='solid')
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create a header for dragging
        header_frame = tk.Frame(border_frame, bg='#444444', height=25)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Add title and controls to header
        title_label = tk.Label(header_frame, text="Chat Widget", bg='#444444', fg='white', font=('Arial', 8))
        title_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Close button
        close_btn = tk.Button(header_frame, text="×", bg='#ff4444', fg='white', 
                             font=('Arial', 8), width=3, command=self.close_overlay)
        close_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Click-through toggle button
        self.toggle_btn = tk.Button(header_frame, text="🔒", bg='#666666', fg='white', 
                                   font=('Arial', 8), width=3, command=self.toggle_click_through)
        self.toggle_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Resize button
        resize_btn = tk.Button(header_frame, text="⟲", bg='#666666', fg='white', 
                              font=('Arial', 8), width=3, command=self.reset_size)
        resize_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Bind drag events to header
        header_frame.bind("<Button-1>", self.start_move)
        header_frame.bind("<B1-Motion>", self.on_move)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_move)
        
        # Create webview container
        self.webview_frame = tk.Frame(border_frame, bg='#000000')
        self.webview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add resize handles
        self.add_resize_handles()
        
        return width, height
    
    def add_resize_handles(self):
        """Add resize handles to the window"""
        # Bottom-right resize handle
        resize_handle = tk.Frame(self.root, bg='#666666', cursor='size_nw_se')
        resize_handle.place(relx=1.0, rely=1.0, anchor='se', width=15, height=15)
        
        resize_handle.bind("<Button-1>", self.start_resize)
        resize_handle.bind("<B1-Motion>", self.on_resize)
    
    def start_resize(self, event):
        """Start window resizing"""
        if not self.is_click_through:
            self.start_x = event.x_root
            self.start_y = event.y_root
            self.start_width = self.root.winfo_width()
            self.start_height = self.root.winfo_height()
    
    def on_resize(self, event):
        """Handle window resizing"""
        if not self.is_click_through:
            new_width = self.start_width + (event.x_root - self.start_x)
            new_height = self.start_height + (event.y_root - self.start_y)
            
            # Minimum size constraints
            new_width = max(200, new_width)
            new_height = max(150, new_height)
            
            self.root.geometry(f"{new_width}x{new_height}")
    
    def reset_size(self):
        """Reset window to default size"""
        self.root.geometry("400x600")
    
    def toggle_click_through(self):
        """Toggle click-through mode"""
        if self.window_handle:
            current_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)
            
            if current_style & win32con.WS_EX_TRANSPARENT:
                # Remove click-through
                new_style = current_style & ~win32con.WS_EX_TRANSPARENT
                win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                self.is_click_through = False
                self.toggle_btn.config(text="🔒", bg='#666666')
                print("🔓 Click-through disabled - You can move and resize the window")
            else:
                # Enable click-through
                new_style = current_style | win32con.WS_EX_TRANSPARENT
                win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                self.is_click_through = True
                self.toggle_btn.config(text="🔓", bg='#ff6666')
                print("🔒 Click-through enabled - Clicks will pass through")
    
    def apply_click_through_on_start(self):
        """Apply Windows-specific flags to make the window click-through on startup"""
        try:
            # Get the window handle
            self.window_handle = win32gui.FindWindow(None, "Chat Overlay")
            
            if self.window_handle:
                # Get current window style
                current_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)
                
                # Add layered flag (needed for transparency)
                new_style = current_style | win32con.WS_EX_LAYERED
                
                # Apply the new style (don't enable click-through on startup)
                win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                
                print("✅ Window setup complete!")
                print("💡 Use the 🔒 button or Ctrl+T to enable click-through")
                return True
            else:
                print("⚠️  Warning: Could not find window handle")
                return False
                
        except Exception as e:
            print(f"❌ Error setting up window: {e}")
            return False
    
    def create_webview(self, width, height):
        """Create the webview in a separate thread"""
        def webview_thread():
            try:
                # Create webview window
                self.webview_window = webview.create_window(
                    title='Chat Widget Content',
                    url=self.chat_url,
                    width=width-20,
                    height=height-50,
                    x=self.root.winfo_x() + 10,
                    y=self.root.winfo_y() + 35,
                    resizable=False,
                    fullscreen=False,
                    shadow=False,
                    on_top=False
                )
                
                # Start webview
                webview.start(debug=False)
                
            except Exception as e:
                print(f"❌ Error creating webview: {e}")
        
        # Start webview in separate thread
        webview_thread_obj = threading.Thread(target=webview_thread, daemon=True)
        webview_thread_obj.start()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for controlling the overlay"""
        def toggle_click_through_key(event=None):
            """Toggle click-through mode via keyboard"""
            self.toggle_click_through()
        
        def close_overlay_key(event=None):
            """Close the overlay via keyboard"""
            self.close_overlay()
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-t>', toggle_click_through_key)  # Ctrl+T
        self.root.bind('<Control-q>', close_overlay_key)  # Ctrl+Q
        self.root.bind('<Escape>', close_overlay_key)  # Escape
        
        # Make sure the window can receive focus for keyboard events
        self.root.focus_force()
    
    def close_overlay(self):
        """Close the overlay"""
        print("🚪 Closing overlay...")
        try:
            if self.webview_window:
                webview.destroy()
        except:
            pass
        self.root.quit()
        sys.exit(0)
    
    def run(self):
        """Start the chat overlay application"""
        print("🚀 Starting Movable Chat Overlay...")
        print(f"🌐 Loading URL: {self.chat_url}")
        
        # Validate URL
        if not self.validate_url(self.chat_url):
            print("❌ Error: Invalid URL provided")
            return
        
        try:
            # Create the overlay window
            width, height = self.create_overlay_window()
            
            # Setup keyboard shortcuts
            self.setup_keyboard_shortcuts()
            
            # Apply window setup after a short delay
            self.root.after(1000, self.apply_click_through_on_start)
            
            # Create webview
            self.create_webview(width, height)
            
            print("\n🎮 Overlay Controls:")
            print("- Drag the header to move the window")
            print("- Drag the bottom-right corner to resize")
            print("- 🔒 button: Toggle click-through mode")
            print("- × button: Close overlay")
            print("- Ctrl+T: Toggle click-through mode")
            print("- Ctrl+Q or Escape: Close overlay")
            
            # Start the Tkinter main loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"❌ Error starting overlay: {e}")
            messagebox.showerror("Error", f"Failed to start overlay: {e}")

def main():
    """Main entry point"""
    # Default to Kick chat URL for deashad
    default_url = "https://kick.com/popout/deashad/chat"
    
    # Check if URL was provided as command line argument
    if len(sys.argv) > 1:
        chat_url = sys.argv[1]
        print(f"🔗 Using provided URL: {chat_url}")
    else:
        chat_url = default_url
        print(f"🔗 Using default Kick chat URL: {chat_url}")
    
    # Create and run the overlay
    overlay = ChatOverlay(chat_url)
    overlay.run()

if __name__ == "__main__":
    main()
