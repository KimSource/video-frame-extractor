# Video Frame Extractor

A small Windows GUI for extracting frames from video files with FFmpeg.

Read this in other languages: [English](README.md), [한국어](README.ko-KR.md)

## Features

- Extract every Nth frame or a list of specific frames.
- Save frames as JPG, PNG, or WebP.
- Adjust JPG and WebP quality, including lossless WebP output.
- Preview the FFmpeg command before extraction.

## Requirements

- Windows
- FFmpeg at `ffmpeg\bin\ffmpeg.exe`
- Python with Tkinter when running from source

The application always looks for FFmpeg at the relative path above. The expected layout is:

```text
video-frame-extractor/
├─ main.py
└─ ffmpeg/
   └─ bin/
      └─ ffmpeg.exe
```

## Running from Source

1. Install Python and make sure `python` is available on `PATH`.
2. Download a Windows build of [FFmpeg](https://ffmpeg.org/download.html) and place it in the layout shown above.
3. Create the virtual environment:

   ```powershell
   .\setup-venv.bat
   ```

4. Run the application:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

The application itself uses only the Python standard library.

## Building the Executable

Activate the virtual environment and install PyInstaller:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install pyinstaller
```

Then run:

```powershell
.\build.bat
```

The executable is created at `dist\main.exe`. Copy the `ffmpeg` directory next to it before running the packaged application:

```text
dist/
├─ main.exe
└─ ffmpeg/
   └─ bin/
      └─ ffmpeg.exe
```

Prebuilt versions are available on the [Releases page](https://github.com/KimSource/video-frame-extractor/releases).
