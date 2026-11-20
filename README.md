# Video-to-GIF Converter

## Description

Video-to-GIF Converter is a Python desktop application that allows users to convert selected segments of video files into animated GIFs.

The application uses FFprobe to extract video metadata, FFmpeg to perform conversions, and PyQt6 to provide an interactive graphical interface.

## Features

- **Video-to-GIF Conversion:** Convert a selected segment of a video into an animated GIF using FFmpeg.
- **Video Preview:** Preview the selected video using the built-in media player.
- **Clip Selection:** Choose the starting point and duration of the GIF.
- **Frame Rate Control:** Adjust the output frame rate between 1 and 60 FPS.
- **Output Resolution:** Select the GIF width in pixels.
- **Live Conversion Progress:** Monitor conversion progress through a progress bar.
- **Asynchronous Conversion:** FFmpeg runs separately from the GUI, allowing the interface to remain responsive.
- **Cancellation:** Cancel an ongoing conversion without leaving incomplete GIF files behind.
- **Dark-Themed Interface:** A PyQt6 interface with a charcoal background and amber accents.

## Technologies

**Language:** Python\
**GUI:** PyQt6\
**External tools:** FFmpeg, FFprobe\
**Version control:** Git

## Prerequisites  

### External Dependency: FFmpeg

This application requires **FFmpeg** and **FFprobe** to be installed separately from the Python dependencies.

- **FFmpeg** converts video clips into GIF files.
- **FFprobe** extracts video metadata, including duration, resolution and codec information.

Both executables must be accessible through the system's `PATH` environment variable.

#### Installing FFmpeg on Windows

1. Visit the [official FFmpeg download page](https://ffmpeg.org/download.html) and select the Windows builds from **gyan.dev**.  
2. Download the **Essentials Build** from the release builds section.
3. Extract the archive to a permanent directory, such as `C:\ffmpeg`.
4. Locate the `bin` folder containing `ffmpeg.exe` and `ffprobe.exe`.
5. Add the full path to that `bin` folder to your Windows `PATH` environment variable.
6. Restart your terminal or IDE to apply the updated environment variable.

#### Verifying the Installation

Open PowerShell or Command Prompt and execute:

```powershell
ffmpeg -version
ffprobe -version
```

Both commands should display version information.

If either command is not recognised, verify that the corresponding executable exists and that its `bin` directory has been added to `PATH`.

**Note:** Installing the Python packages using `pip install -r requirements.txt` does not install FFmpeg or FFprobe. These external tools must be configured separately before running the application.

## Installation

1. Download or clone the repository and open its project directory

2. Create a Python virtual environment:
`python -m venv .venv`

3. Activate the virtual environment in Windows Powershell:
`.\.venv\Scripts\Activate.ps1`

4. Install the required dependencies:
`python pip install -r requirements.txt`

5. Launch the Video-to-GIF Converter:
`python main.py`


## Usage

1. Launch the Video-to-GIF Converter.
2. Click **Select Video** and choose a supported video file (`.mp4`, `.mov`, `.mkv` or `.avi`).
3. Preview the video using the built-in player and timeline controls.
4. Select the desired starting time and clip duration.
5. Configure the GIF's frame rate (FPS) and output width.
6. Click **Select Output** and choose the location and filename for the GIF.
7. Click **Convert to GIF** to begin the conversion.
8. Monitor the progress bar until conversion finishes.

**Note:** You may cancel an ongoing conversion using **Cancel GIF**. Incomplete output files are removed when cancellation is completed.

## Screenshots

![Video-to-GIF Converter interface](screenshots\converter_gui.png)

## Development Status

Version 1.0.0 -- First Stable release.