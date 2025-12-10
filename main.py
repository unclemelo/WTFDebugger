import time
import json
import os
from pathlib import Path
from colorama import Fore, Style, init
from log_reader import LogReader
import platform

CONFIG_PATH = Path("config.json")



DEFAULT_CONFIG = {
    "cooldown": 0.5,
    "show_trash_logs": False,
    "enabled_categories": {
        "PlayerStats": True,
        "Session": True,
        "WeaponStats": True,
        "LevelProgression": True,
        "Matchmaking": True
    }
}

def load_config():
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)

config = load_config()



def find_log_path():
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
        username = os.getenv("USER")
        log_dir = Path(f"/mnt/c/Users/{username}/AppData/Local/Worlds_FPS/Saved/Logs")

    elif system == "Linux":
        log_dir = Path.home() / ".local" / "share" / "Worlds_FPS" / "Saved" / "Logs"

    if log_dir and log_dir.exists():
        logs = list(log_dir.glob("Worlds_FPS*.log"))
        if logs:
            return max(logs, key=lambda f: f.stat().st_mtime)

    return None


LOG_PATH = find_log_path()
if LOG_PATH is None:
    print(Fore.RED + f"Could not find log file for Worlds_FPS on {platform.system()}!")
    exit(1)


def process_log(entry):
    """Print JSON or plain logs with color coding based on config."""
    cfg = config  # shortcut

    # ----- JSON entries -----
    if isinstance(entry, dict):

        if any(k in entry for k in ["LogLyra", "TotalKills", "TotalDeaths"]):
            if cfg["enabled_categories"]["PlayerStats"]:
                print(Fore.CYAN + f"[PlayerStats] {entry}")

        elif "EpicID" in entry:
            if cfg["enabled_categories"]["Session"]:
                print(Fore.GREEN + f"[Session] {entry}")

        elif "WeaponStats" in entry:
            if cfg["enabled_categories"]["WeaponStats"]:
                print(Fore.YELLOW + f"[WeaponStats] {len(entry['WeaponStats'])} weapons")

        elif "LevelProgression" in entry:
            if cfg["enabled_categories"]["LevelProgression"]:
                print(Fore.BLUE + f"[LevelProgression] Received table")

        elif "matchmaking" in str(entry).lower():
            if cfg["enabled_categories"]["Matchmaking"]:
                print(Fore.MAGENTA + f"[MM] {entry}")

        else:
            if cfg["show_trash_logs"]:
                print(Fore.WHITE + f"[JSON] {entry}")

    # ----- Plain log lines -----
    else:
        l = entry.lower()
        color = Fore.WHITE
        prefix = "[LOG]"

        if "error" in l:
            color = Fore.RED
            prefix = "[ERROR]"
        elif "warning" in l:
            color = Fore.YELLOW
            prefix = "[WARN]"
        elif "matchmaking" in l or "wslogtelemetry" in l:
            if config["enabled_categories"]["Matchmaking"]:
                color = Fore.MAGENTA
                prefix = "[MM]"
        elif "ui" in l:
            color = Fore.GREEN
        else:
            if not config["show_trash_logs"]:
                return  # skip trash entirely
            prefix = "[TRASH]"

        print(color + f"{prefix} {entry}")


def show_menu():
    while True:
        print("\n" + Fore.YELLOW + "===== CONFIG MENU =====" + Style.RESET_ALL)
        print("1. Change cooldown")
        print("2. Toggle show trash logs")
        print("3. Toggle category filters")
        print("4. Save config")
        print("5. Start log watcher")
        print("0. Exit")
        choice = input("\nSelect option: ")

        if choice == "1":
            new_cd = input("Enter new cooldown (float): ")
            try:
                config["cooldown"] = float(new_cd)
                print("Cooldown updated.")
            except:
                print("Invalid number.")

        elif choice == "2":
            config["show_trash_logs"] = not config["show_trash_logs"]
            print("Trash logs:", config["show_trash_logs"])

        elif choice == "3":
            print("\nToggle categories:")
            for cat, enabled in config["enabled_categories"].items():
                print(f"- {cat}: {'ON' if enabled else 'OFF'}")

            sel = input("Category name: ")
            if sel in config["enabled_categories"]:
                config["enabled_categories"][sel] = not config["enabled_categories"][sel]
                print(f"{sel} toggled.")
            else:
                print("Invalid category.")

        elif choice == "4":
            save_config(config)
            print("Config saved.")

        elif choice == "5":
            save_config(config)
            print("\nStarting log watcher...\n")
            start_watcher()

        elif choice == "0":
            exit()

        else:
            print("Invalid choice.")

def start_watcher():
    reader = LogReader(LOG_PATH, callback=process_log, cooldown=config["cooldown"])
    try:
        while True:
            reader.update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    show_menu()
