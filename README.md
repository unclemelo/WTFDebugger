# WTF Debugger

A Python-based log reader for **Worlds_FPS** (or other Unreal Engine games), compatible with **Windows, Linux, and WSL**.
It highlights log entries with colors, extracts JSON blocks, and filters for matchmaker, player stats, session info, and more.

---

## Features

* Automatically detects log file path on:

  * Windows (`%LOCALAPPDATA%\Worlds_FPS\Saved\Logs`)
  * Linux (`~/.local/share/Worlds_FPS/Saved/Logs`)
  * WSL (`/mnt/c/Users/<username>/AppData/Local/Worlds_FPS/Saved/Logs`)
* Color-coded console output using `colorama`:

  * Errors ➞ Red
  * Warnings ➞ Yellow
  * Matchmaker / Telemetry ➞ Magenta
  * Player stats ➞ Cyan
  * Weapon stats ➞ Yellow
  * Session info ➞ Green
* Extracts and parses JSON embedded in log lines.
* Handles file resets (game restarts) safely.
* Configurable update cooldown.

---

## Requirements

* Python 3.8+
* [colorama](https://pypi.org/project/colorama/)

Install dependencies:

```bash
pip install colorama
```

---

## Setup

1. Clone or download this repository.
2. Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
# Activate
# Windows CMD: venv\Scripts\activate
# PowerShell: venv\Scripts\Activate.ps1
# WSL/Linux: source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the log reader:

```bash
python main.py
```

The script will:

1. Auto-detect the latest log file for `Worlds_FPS`.
2. Continuously watch for new log lines.
3. Print log entries with color coding.
4. Parse JSON blocks embedded in logs and print them with filters.

Press `Ctrl+C` to exit.

---

## Configuration

* **COOLDOWN**: Minimum time (seconds) between reading the log file. Default: `0.5`.
* **GAME_NAME**: Name of your game folder. Default: `"Worlds_FPS"`. Change if needed.

---

## Project Structure

```
WTFDebugger/
├─ main.py        # Entry point, detects log path and prints log entries
├─ log_reader.py  # Handles reading log files and extracting JSON
├─ requirements.txt
└─ README.md
```

---

## Notes

* Works in **Windows, Linux, and WSL**.
* In WSL, it reads the Windows filesystem via `/mnt/c/...`.
* Make sure the log file exists; the script will fail gracefully if it cannot find it.

---

## License

MIT License
