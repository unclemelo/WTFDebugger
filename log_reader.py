import json
import time
import re
from pathlib import Path
from colorama import Fore

class LogReader:
    JSON_REGEX = re.compile(r"JSON\((.*?)\)JSON", re.DOTALL)

    def __init__(self, log_path, callback=None, cooldown=0.5):
        self.log_path = Path(log_path)
        self.callback = callback
        self.cooldown = cooldown
        self.last_read_time = 0
        self.last_size = 0

    def update(self):
        """Read new log lines safely with cooldown and parse JSON blocks."""
        now = time.time()
        if now - self.last_read_time < self.cooldown:
            return
        self.last_read_time = now

        if not self.log_path.exists():
            print(f"[LogReader] File not found: {self.log_path}")
            return

        try:
            current_size = self.log_path.stat().st_size

            if current_size < self.last_size:
                # File was reset (game restarted)
                self.last_size = 0

            if current_size == self.last_size:
                return

            with self.log_path.open("r", encoding="utf-8", errors="ignore") as f:
                f.seek(self.last_size)
                new_text = f.read()
                self.last_size = f.tell()

            for line in new_text.splitlines():
                # Send plain line
                if self.callback:
                    self.callback(line)

                # Extract JSON blocks if they exist
                for match in self.JSON_REGEX.findall(line):
                    try:
                        data = json.loads(match)
                        if self.callback:
                            self.callback(data)
                    except Exception as e:
                        print(f"[LogReader] JSON parse error: {e}\n{match[:200]}")

        except Exception as e:
            print(f"[LogReader] Error reading: {e}")
