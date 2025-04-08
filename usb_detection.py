import psutil
import time
from datetime import datetime

# Function to log events
def log_event(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open("log.txt", "a") as log_file:
        log_file.write(f"{timestamp} {message}\n")

def detect_usb():
    initial_devices = {part.device for part in psutil.disk_partitions()}
    print("Monitoring for USB device insertion...")
    log_event("🟡 Started USB monitoring.")

    while True:
        current_devices = {part.device for part in psutil.disk_partitions()}
        new_devices = current_devices - initial_devices

        if new_devices:
            for device in new_devices:
                msg = f"New USB device detected: {device}"
                print(msg)
                log_event(f"✅ {msg}")

        initial_devices = current_devices
        time.sleep(5)

# Start USB detection
detect_usb()
