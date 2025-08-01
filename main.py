#!/usr/bin/env python3
"""
Transparent Streaming Chat Overlay - Fixed Main Thread
Creates a small, resizable, movable overlay window with embedded chat.
"""

import tkinter as tk
from tkinter import messagebox
import win32gui
import win32con
import sys
import webbrowser
import webview
import threading
import time
from urllib.parse import urlparse

class ChatOverlay:
    def __init__(self, chat_url="https://kick.com/popout/deashad/chat"):
        self.chat_url = chat_url
        self.root = None
        self.window_handle = None
        self.webview_window = None
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
        self.root.attributes('-alpha', 0.95)  # Semi-transparent
        
        # Set initial size and position
        width = 400
        height = 600
        x_pos = 100
        y_pos = 100
        
        self.root.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        
        # Background color (not transparent to show border)
        self.root.configure(bg='#2a2a2a')
        
        # Create a border frame
        border_frame = tk.Frame(self.root, bg='#444444', bd=1, relief='solid')
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create header for controls
        header_frame = tk.Frame(border_frame, bg='#333333', height=30)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="Kick Chat", bg='#333333', fg='white', 
                              font=('Arial', 9, 'bold'))
        title_label.pack(side=tk.LEFT, padx=8, pady=5)
        
        # Control buttons
        # Close button
        close_btn = tk.Button(header_frame, text="×", bg='#ff4444', fg='white', 
                             font=('Arial', 10, 'bold'), width=3, command=self.close_overlay,
                             relief='flat', bd=0)
        close_btn.pack(side=tk.RIGHT, padx=2, pady=3)
        
        # Click-through toggle
        self.toggle_btn = tk.Button(header_frame, text="🔒", bg='#666666', fg='white', 
                                   font=('Arial', 9), width=3, command=self.toggle_click_through,
                                   relief='flat', bd=0)
        self.toggle_btn.pack(side=tk.RIGHT, padx=2, pady=3)
        
        # Resize button
        resize_btn = tk.Button(header_frame, text="⟲", bg='#666666', fg='white', 
                              font=('Arial', 9), width=3, command=self.reset_size,
                              relief='flat', bd=0)
        resize_btn.pack(side=tk.RIGHT, padx=2, pady=3)
        
        # Start webview button
        webview_btn = tk.Button(header_frame, text="🌐", bg='#0066cc', fg='white', 
                               font=('Arial', 9), width=3, command=self.start_webview,
                               relief='flat', bd=0)
        webview_btn.pack(side=tk.RIGHT, padx=2, pady=3)
        
        # Bind drag events
        header_frame.bind("<Button-1>", self.start_move)
        header_frame.bind("<B1-Motion>", self.on_move)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_move)
        
        # Chat container frame
        self.chat_frame = tk.Frame(border_frame, bg='#1a1a1a')
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=(0,3))
        
        # Instructions
        instructions = """
🎮 Kick Chat Overlay

🌐 Chat'i başlatmak için tıklayın

Kontroller:
• 🌐 = Chat'i ayrı pencerede aç
• 🔒 = Click-through aç/kapat  
• ⟲ = Boyutu sıfırla
• × = Kapat

Klavye:
• Ctrl+T = Click-through
• Ctrl+Q = Kapat
• Escape = Kapat
        """
        
        instruction_label = tk.Label(self.chat_frame, text=instructions.strip(), 
                                   bg='#1a1a1a', fg='#cccccc', font=('Arial', 9),
                                   justify=tk.LEFT)
        instruction_label.pack(expand=True, pady=20)
        
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
            new_width = max(300, new_width)
            new_height = max(200, new_height)
            
            self.root.geometry(f"{new_width}x{new_height}")
    
    def reset_size(self):
        """Reset window to default size"""
        self.root.geometry("400x600")
    
    def start_webview(self):
        """Start webview in a separate process"""
        print("🌐 Chat penceresi açılıyor...")
        try:
            # Close tkinter window first
            overlay_x = self.root.winfo_x()
            overlay_y = self.root.winfo_y()
            overlay_width = self.root.winfo_width()
            overlay_height = self.root.winfo_height()
            
            # Calculate webview position
            webview_x = overlay_x + overlay_width + 10  # Next to overlay
            webview_y = overlay_y
            webview_width = 400
            webview_height = overlay_height
            
            # Start webview in a thread that will handle the main thread requirement
            def webview_starter():
                # This needs to run after tkinter mainloop ends
                self.root.after(100, self.destroy_and_start_webview)
            
            # Schedule webview start
            threading.Thread(target=webview_starter, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Webview başlatılamadı: {e}")
    
    def destroy_and_start_webview(self):
        """Destroy tkinter and start webview"""
        try:
            # Save window properties
            overlay_x = self.root.winfo_x()
            overlay_y = self.root.winfo_y()
            overlay_width = self.root.winfo_width()
            overlay_height = self.root.winfo_height()
            
            # Close tkinter
            self.root.quit()
            self.root.destroy()
            
            # Calculate webview dimensions
            webview_width = overlay_width
            webview_height = overlay_height
            
            print("🎮 Chat yükleniyor...")
            print("✅ Chat penceresini overlay'in yanına konumlandırın")
            print("🔒 Click-through için Ctrl+T kullanın")
            
            # Create webview window
            self.webview_window = webview.create_window(
                title='Kick Chat',
                url=self.chat_url,
                width=webview_width,
                height=webview_height,
                x=overlay_x,
                y=overlay_y,
                resizable=True,
                fullscreen=False,
                shadow=True,
                on_top=True,
                transparent=False
            )
            
            # Start webview (this will block)
            webview.start(debug=False)
            
        except Exception as e:
            print(f"❌ Webview oluşturulamadı: {e}")
    
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
                print("🔓 Click-through kapatıldı")
            else:
                # Enable click-through
                new_style = current_style | win32con.WS_EX_TRANSPARENT
                win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                self.is_click_through = True
                self.toggle_btn.config(text="🔓", bg='#ff6666')
                print("🔒 Click-through aktif")
    
    def apply_window_properties(self):
        """Apply Windows-specific flags to the window"""
        try:
            # Get overlay window handle
            self.window_handle = win32gui.FindWindow(None, "Chat Overlay")
            
            if self.window_handle:
                current_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)
                new_style = current_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST
                win32gui.SetWindowLong(self.window_handle, win32con.GWL_EXSTYLE, new_style)
                
                print("✅ Overlay pencere ayarları tamamlandı!")
                return True
            else:
                print("⚠️  Overlay pencere handle'ı bulunamadı")
                return False
                
        except Exception as e:
            print(f"❌ Pencere ayarları hatası: {e}")
            return False
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        def toggle_click_through_key(event=None):
            self.toggle_click_through()
        
        def close_overlay_key(event=None):
            self.close_overlay()
        
        def start_webview_key(event=None):
            self.start_webview()
        
        # Bind shortcuts
        self.root.bind('<Control-t>', toggle_click_through_key)
        self.root.bind('<Control-q>', close_overlay_key)
        self.root.bind('<Escape>', close_overlay_key)
        self.root.bind('<Control-w>', start_webview_key)
        
        self.root.focus_force()
    
    def close_overlay(self):
        """Close the overlay"""
        print("🚪 Overlay kapatılıyor...")
        try:
            self.root.quit()
            sys.exit(0)
        except:
            sys.exit(0)
    
    def run(self):
        """Start the chat overlay application"""
        print("🚀 Kick Chat Overlay Başlatılıyor...")
        print(f"🌐 Chat URL: {self.chat_url}")
        
        # Validate URL
        if not self.validate_url(self.chat_url):
            print("❌ Hata: Geçersiz URL")
            return
        
        try:
            # Create overlay window
            width, height = self.create_overlay_window()
            
            # Setup keyboard shortcuts
            self.setup_keyboard_shortcuts()
            
            # Apply window properties after delay
            self.root.after(1000, self.apply_window_properties)
            
            print("\n🎮 Overlay Kontrolleri:")
            print("- Header'ı sürükleyerek pencereyi taşıyın")
            print("- Sağ alt köşeden boyutlandırın")
            print("- 🌐 butonu: Chat'i başlat")
            print("- 🔒 butonu: Click-through aç/kapat")
            print("- × butonu: Overlay'i kapat")
            print("- Ctrl+W: Chat'i başlat")
            print("- Ctrl+T: Click-through aç/kapat")
            print("- Ctrl+Q veya Escape: Overlay'i kapat")
            
            # Start Tkinter main loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"❌ Başlatma hatası: {e}")
            messagebox.showerror("Hata", f"Overlay başlatılamadı: {e}")

def main():
    """Main entry point"""
    default_url = "https://kick.com/popout/deashad/chat"
    
    if len(sys.argv) > 1:
        chat_url = sys.argv[1]
        print(f"🔗 Verilen URL kullanılıyor: {chat_url}")
    else:
        chat_url = default_url
        print(f"🔗 Varsayılan Kick chat URL'si kullanılıyor: {chat_url}")
    
    overlay = ChatOverlay(chat_url)
    overlay.run()

if __name__ == "__main__":
    main()
