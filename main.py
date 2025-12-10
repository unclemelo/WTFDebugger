import time
from log_reader import LogReader
from colorama import Fore, Style, init
from pathlib import Path
import os
import platform

COOLDOWN = 0.5

def find_log_path():
    """Find the UE log file for Windows, Linux, or WSL."""
    system = platform.system()
    log_dir = None

    # Detect WSL
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                system = "WSL"
    except FileNotFoundError:
        pass

    if system == "Windows":
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            log_dir = Path(local_appdata) / "Worlds_FPS" / "Saved" / "Logs"
    elif system == "WSL":
        # WSL paths map Windows drives under /mnt/
        username = os.getenv("USER")
        log_dir = Path(f"/mnt/c/Users/{username}/AppData/Local/Worlds_FPS/Saved/Logs")
    elif system == "Linux":
        log_dir = Path.home() / ".local" / "share" / "Worlds_FPS" / "Saved" / "Logs"

    if log_dir and log_dir.exists():
        logs = list(log_dir.glob("Worlds_FPS*.log"))
        if logs:
            return max(logs, key=lambda f: f.stat().st_mtime)  # latest log
    return None

LOG_PATH = find_log_path()
if LOG_PATH is None:
    from colorama import Fore
    print(Fore.RED + f"Could not find log file for Worlds_FPS on {platform.system()}!")
    exit(1)


def process_log(entry):
    """Print JSON or plain logs with color coding and MM filter."""

    # JSON entries
    if isinstance(entry, dict):
        PS = ["LogLyra", "TotalKills", "TotalDeaths"]
        if any(key in entry for key in PS):
            print(Fore.CYAN + f"[PlayerStats] {entry}")
        elif "EpicID" in entry:
            print(Fore.GREEN + f"[Session] {entry}")
        elif "WeaponStats" in entry:
            print(Fore.YELLOW + f"[WeaponStats] {len(entry['WeaponStats'])} weapons")
        elif "LevelProgression" in entry:
            print(Fore.BLUE + f"[LevelProgression] Table received")
        elif "matchmaking" in entry or "queue" in entry:
            print(Fore.MAGENTA + f"[MM] {entry}")
        else:
            print(Fore.WHITE + f"[JSON] {entry}")

    # Plain UE log lines
    else:
        line = entry.lower()
        color = Fore.WHITE
        prefix = "[LOG]"

        if "error" in line or "fatal" in line:
            color = Fore.RED
            prefix = "[ERROR]"
        elif "warning" in line:
            color = Fore.YELLOW
            prefix = "[WARN]"
        elif "matchmaking" in line or "wslogtelemetry" in line or "bp_matchmaker" in line:
            color = Fore.MAGENTA
            prefix = "[MM]"
        elif "blueprint" in line:
            color = Fore.CYAN
        elif "ui" in line:
            color = Fore.GREEN

        print(color + f"{prefix} {entry}")


if __name__ == "__main__":
    reader = LogReader(LOG_PATH, callback=process_log, cooldown=COOLDOWN)
    try:
        while True:
            reader.update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
