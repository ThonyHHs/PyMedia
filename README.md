# PyMedia
**PyMedia** is a tool for downloading YouTube videos and audio, available in both GUI (Graphical User Interface) and CLI (Command Line Interface) modes.

## Features
- **Video and audio support:** Download videos and audio separately or merge them into a single file.

- **Format selection:**
    - **Videos:** `.mp4`
    - **Audio:** `.mp3`

- **GUI Mode:**
    - Search and validate YouTube urls.
    - Display media details, including thumbnails, title, channel, and duration.
    - Toggle between video and audio download modes.

- **CLI Mode:**
    - Command-line options to specify url, file type, name, and save path.
    - FFMPEG Integration: Used for merging video and audio or converting audio to `.mp3`.


# Requirements
## Python Dependencies
- `tkinter`
- `ttkbootstrap` 1.10.1
- `Pillow` 11.0.0
- `pytubefix` 8.3.0

## Other
- FFMPEG (place the executable in `ffmpeg/bin`)

# Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/media-downloader.git
   cd media-downloader
   ```

2. **Install dependencies**: Ensure you have Python 3.12 and [pip](https://pip.pypa.io/en/stable/) installed, then install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure FFMPEG is properly set up and adjust the path in the code if needed.


# Usage
## GUI Mode
1. **Run the application:**
    ```bash
    python App.py
    ```
2. **Available features:**
    - Enter a YouTube url and click Search.
    - View detailed media information.
    - Click Download to save the video or audio.

# CLI Mode
1. **Run the application with the necessary arguments:**
    ```bash
    python Media.py --url <URL> --path <PATH> --name <NAME> [--video | --audio]
    ```
    Examples:
    - **Download a video:**
    ```bash
    python Media.py --url "https://youtu.be/EXAMPLE" --path "./downloads" --name "video" --video
    ```
    - **Download audio:**
    ```bash
    python Media.py --url "https://youtu.be/EXAMPLE" --path "./downloads" --name "audio" --audio
    ```

# Future Improvements
- Playlist support.
- Progress bar during downloads.
- Option to download all added items at once.
- Scroll support for displaying multiple items in the GUI.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
