# Meet2UI

A compact camera control application for USB cameras with PTZ (Pan-Tilt-Zoom) support on Linux.

![Meet2UI Demo](assets/demo.png)

## Features

- **Live Preview**: Real-time camera feed with 16:9 aspect ratio
- **PTZ Controls**: Zoom, Pan, and Tilt sliders
- **Image Adjustments**: Brightness, Contrast, Saturation, Sharpness
- **Autofocus Toggle**: Enable/disable continuous autofocus
- **Face Tracking**: Automatic pan/tilt to keep face centered
- **Presets**: Save and load camera settings
- **Dark Theme**: Modern compact UI with TypeStarOCR font

## Requirements

- Python 3.9+
- Linux with v4l2 support
- USB camera with UVC controls (tested with OBSBOT Meet 2)

## Installation

```bash
# Clone the repository
git clone https://github.com/nrupatunga/meet2ui.git
cd meet2ui

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Dependencies

- **DearPyGui**: GUI framework
- **OpenCV**: Video capture and image processing
- **NumPy**: Array operations
- **v4l2-ctl**: Camera control (system package)

Install v4l2-ctl:
```bash
sudo apt install v4l-utils
```

## Project Structure

```
meet2ui/
├── main.py              # Entry point
├── core/
│   ├── camera.py        # OpenCV video capture
│   ├── tracker.py       # Face detection and tracking
│   └── v4l2.py          # v4l2-ctl wrapper
├── ui/
│   ├── app.py           # Main application window
│   ├── controls.py      # Slider/toggle/button builders
│   ├── preview.py       # Live video preview widget
│   └── theme.py         # Dark theme styling
├── config/
│   └── presets.py       # JSON preset management
├── utils/
│   └── constants.py     # Configuration constants
└── tests/               # Unit tests
```

## Controls

| Control | Range | Description |
|---------|-------|-------------|
| Zoom | 0-100 | Digital/optical zoom |
| Pan | -648000 to 648000 | Horizontal rotation |
| Tilt | -648000 to 648000 | Vertical rotation |
| Brightness | 0-100 | Image brightness |
| Contrast | 0-100 | Image contrast |
| Saturation | 0-100 | Color saturation |
| Sharpness | 0-100 | Image sharpness |

## Development

```bash
# Run tests
pytest

# Run with pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## License

MIT
