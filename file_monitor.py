import os
import time
from datetime import datetime

monitored_folder = "D:\\usb detection project"

# Function to log events to log.txt
def log_event(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open("log.txt", "a") as log_file:
        log_file.write(f"{timestamp} {message}\n")

# Store initial file states
files_state = {file: os.stat(os.path.join(monitored_folder, file)).st_mtime
               for file in os.listdir(monitored_folder)}

print("Monitoring files...")
log_event("🟡 Started monitoring files in 'D:\\usb detection project'.")

while True:
    current_files_state = {file: os.stat(os.path.join(monitored_folder, file)).st_mtime
                           for file in os.listdir(monitored_folder)}

    for file, last_modified in current_files_state.items():
        if file not in files_state:
            msg = f"New file detected: {file}"
            print(msg)
            log_event(f"✅ {msg}")

        elif files_state[file] != last_modified:
            msg = f"File modified: {file}"
            print(msg)
            log_event(f"✏️ {msg}")

    files_state = current_files_state
    time.sleep(5)
