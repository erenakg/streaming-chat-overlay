#!/usr/bin/env python3
"""
Transparent Streaming Chat Overlay
Creates an always-on-top, click-through overlay window that displays a chat widget.
"""

import webview
import win32gui
import win32con
import sys
import time
import threading
from urllib.parse import urlparse

class ChatOverlay:
    def __init__(self, chat_url="https://kick.com/popout/deashad/chat"):
        self.chat_url = chat_url
        self.webview_window = None
        self.window_handle = None
        self.click_through_enabled = True
        
    def validate_url(self, url):
        """Validate the provided URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def find_webview_window(self):
        """Find the webview window handle"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if "Chat Widget" in window_text or "pywebview" in window_text.lower():
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows[0] if windows else None
    
    def apply_click_through(self):
        """Apply Windows-specific flags to make the window click-through"""
        attempts = 0
        max_attempts = 10
        
        while attempts < max_attempts:
            self.window_handle = self.find_webview_window()
            
            if self.window_handle:
                try:
                    # Get current window style
                    current_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)
                    
                    # Add layered and transparent flags
                    new_style = current_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
                    
                    # Apply the new style
                    win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                    
                    # Make window always on top
                    win32gui.SetWindowPos(
                        self.window_handle,
                        win32con.HWND_TOPMOST,
                        0, 0, 0, 0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                    )
                    
                    print("✅ Click-through mode activated!")
                    print("✅ Window set to always on top!")
                    return True
                    
                except Exception as e:
                    print(f"❌ Error applying window properties: {e}")
                    
            attempts += 1
            time.sleep(0.5)
        
        print("⚠️  Warning: Could not find webview window for click-through")
        return False
    
    def setup_keyboard_monitoring(self):
        """Setup keyboard monitoring for shortcuts"""
        def monitor_keys():
            import keyboard
            
            def toggle_click_through():
                if self.window_handle:
                    try:
                        current_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)
                        
                        if current_style & win32con.WS_EX_TRANSPARENT:
                            # Remove click-through
                            new_style = current_style & ~win32con.WS_EX_TRANSPARENT
                            win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                            print("🔓 Click-through disabled - You can now interact with the chat")
                            self.click_through_enabled = False
                        else:
                            # Enable click-through
                            new_style = current_style | win32con.WS_EX_TRANSPARENT
                            win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                            print("🔒 Click-through enabled - Clicks will pass through")
                            self.click_through_enabled = True
                    except Exception as e:
                        print(f"❌ Error toggling click-through: {e}")
            
            def close_overlay():
                print("🚪 Closing overlay...")
                webview.destroy()
                sys.exit(0)
            
            # Register hotkeys
            try:
                keyboard.add_hotkey('ctrl+t', toggle_click_through)
                keyboard.add_hotkey('ctrl+q', close_overlay)
                keyboard.add_hotkey('esc', close_overlay)
                print("⌨️  Keyboard shortcuts registered")
            except:
                print("⚠️  Warning: Could not register keyboard shortcuts")
        
        try:
            import keyboard
            thread = threading.Thread(target=monitor_keys, daemon=True)
            thread.start()
        except ImportError:
            print("⚠️  Warning: 'keyboard' module not available. Install with: pip install keyboard")
    
    def run(self):
        """Start the chat overlay application"""
        print("🚀 Starting Kick Chat Overlay...")
        print(f"🌐 Loading URL: {self.chat_url}")
        
        # Validate URL
        if not self.validate_url(self.chat_url):
            print("❌ Error: Invalid URL provided")
            return
        
        try:
            # Get screen dimensions
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            print(f"📱 Screen resolution: {screen_width}x{screen_height}")
            
            # Setup keyboard monitoring
            self.setup_keyboard_monitoring()
            
            # Create webview window
            self.webview_window = webview.create_window(
                title='Chat Widget',
                url=self.chat_url,
                width=screen_width,
                height=screen_height,
                x=0,
                y=0,
                resizable=True,
                fullscreen=False,
                shadow=False,
                on_top=True,
                transparent=False  # We'll handle transparency via Win32 API
            )
            
            print("\n🎮 Overlay Controls:")
            print("- Ctrl+T: Toggle click-through mode")
            print("- Ctrl+Q or Esc: Close overlay")
            print("- Wait 2 seconds for click-through to activate...")
            
            # Apply click-through after webview is created
            def apply_after_delay():
                time.sleep(2)
                self.apply_click_through()
            
            delay_thread = threading.Thread(target=apply_after_delay, daemon=True)
            delay_thread.start()
            
            # Start webview (this will block until window is closed)
            webview.start(debug=False)
            
        except Exception as e:
            print(f"❌ Error starting overlay: {e}")

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
