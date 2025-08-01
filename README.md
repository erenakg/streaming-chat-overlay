# Streaming Chat Overlay

A transparent, always-on-top, click-through overlay window for displaying chat widgets during live streams. Built with Python using Tkinter and PyWebView.

## Features

- **Transparent Overlay**: Nearly invisible background that doesn't interfere with your stream
- **Always On Top**: Stays above all other windows
- **Click-Through**: Mouse clicks pass through the overlay to underlying applications
- **Fullscreen**: Automatically sizes to your screen resolution
- **Keyboard Controls**: Easy shortcuts to control the overlay
- **Web-Based**: Loads any web-based chat widget (default: Botrix)

## Requirements

- Python 3.7 or higher
- Windows OS (uses win32gui for click-through functionality)

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd streaming-chat-overlay
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: If you encounter issues with `pywin32`, you might need to install it separately:
   ```bash
   pip install pywin32
   python -m pywin32_postinstall
   ```

## Usage

### Basic Usage (Default Botrix Chat)
```bash
python main.py
```

### Custom Chat URL
```bash
python main.py "https://your-chat-widget-url.com"
```

### Examples with Popular Chat Services

**Streamlabs:**
```bash
python main.py "https://streamlabs.com/widgets/chatbox"
```

**StreamElements:**
```bash
python main.py "https://streamelements.com/widgets/chatbox"
```

**Botrix (default):**
```bash
python main.py "https://botrix.live/embed/chat"
```

## Controls

Once the overlay is running, you can use these keyboard shortcuts:

- **Ctrl + T**: Toggle click-through mode on/off
- **Ctrl + Q**: Close the overlay
- **Escape**: Close the overlay

## How It Works

1. **Tkinter Window**: Creates a frameless, topmost window
2. **Win32 API**: Uses Windows API to set transparency and click-through flags
3. **PyWebView**: Embeds a web browser to display the chat widget
4. **Threading**: Runs the webview in a separate thread for better performance

## Configuration

You can modify the overlay behavior by editing `main.py`:

- **Default URL**: Change the `default_url` variable in the `main()` function
- **Window Size**: The overlay automatically uses full screen, but you can modify the geometry in `create_overlay_window()`
- **Transparency**: Adjust the alpha value in `create_overlay_window()` (0.01 = nearly transparent)
- **Keyboard Shortcuts**: Modify the key bindings in `setup_keyboard_shortcuts()`

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Try installing pywin32 separately: `pip install pywin32`

2. **Window not click-through**
   - The click-through is applied after 1 second delay
   - Use Ctrl+T to toggle click-through mode
   - Check Windows permissions for the application

3. **Chat widget not loading**
   - Verify the URL is correct and accessible
   - Check your internet connection
   - Some widgets may have CORS restrictions

4. **Overlay not visible**
   - The overlay has very low opacity by design
   - Look for the chat content, not the window background
   - Try pressing Ctrl+T to toggle click-through and see if you can interact with it

### Performance Tips

- Close other resource-intensive applications when streaming
- Use a dedicated URL for your chat widget to reduce loading time
- Consider using a lighter chat widget if you experience performance issues

## Customization

### Adding More Chat Services

To add support for more chat services, simply run the application with their embed URL:

```bash
python main.py "https://chat-service.com/embed/your-channel"
```

### Modifying Window Properties

Edit the `create_overlay_window()` method in `main.py` to adjust:
- Window transparency
- Window size and position
- Background color

### Adding More Controls

Edit the `setup_keyboard_shortcuts()` method to add more keyboard shortcuts for controlling the overlay.

## License

This project is open source. Feel free to modify and distribute as needed.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the overlay functionality.

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all dependencies are correctly installed
3. Make sure you're running on Windows (required for click-through functionality)
4. Check the console output for error messages
