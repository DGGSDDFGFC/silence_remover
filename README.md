# Silence Remover

A simple, clean, and efficient web-based application built with Python and Flask. This tool allows users to upload audio files and automatically remove silent sections longer than a specified duration, based on a configurable volume threshold.

## Features

- **Automated Silence Removal:** Automatically detects and cuts out silence from uploaded audio.
- **Configurable Settings:** Adjustable volume threshold (default: -40dB) and minimum silence duration (default: 0.3s).
- **Web Interface:** User-friendly web UI for easy interaction without needing CLI commands.

## Setup

1. Clone the repository
2. Install the necessary dependencies (e.g. `pip install -r requirements.txt`)
3. Run `python app.py` to start the server!
