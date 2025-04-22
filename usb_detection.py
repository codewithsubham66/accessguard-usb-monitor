import psutil
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess

# -------- CONFIGURATION --------
LOG_FILE = "usb_logs.txt"
WHITELIST_FILE = "usb_whitelist.txt"

# Email setup
SENDER_EMAIL = "accessguard.file@gmail.com"
APP_PASSWORD = "qwfx jdmw cane tgev"  # Use your actual App Password
RECIPIENT_EMAIL = "8904subhamd@gmail.com"

# -------- FUNCTIONS --------

def log_event(event_type, device_name):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    clean_event_type = event_type.encode("ascii", "ignore").decode()

    with open(LOG_FILE, "a", encoding='utf-8') as log_file:
        log_file.write(f"[{current_time}] {clean_event_type}: {device_name}\n")

    print(f"[{current_time}] {event_type}: {device_name}")

def get_usb_devices():
    devices = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if 'removable' in partition.opts or 'cdrom' in partition.opts:
            devices.append(partition.device)
    return devices

def send_email_alert(device_name):
    subject = "\ud83d\udea8 Unauthorized USB Detected!"
    body = f"An unauthorized USB device ({device_name}) was detected on the system at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
        print("\ud83d\udce7 Email alert sent.")
    except Exception as e:
        print(f"\u2757 Failed to send email alert: {e}")

def get_usb_serials():
    try:
        result = subprocess.check_output('wmic diskdrive get DeviceID,SerialNumber,InterfaceType', shell=True).decode()
        lines = result.strip().split('\n')[1:]
        serials = {}
        for line in lines:
            if 'USB' in line:
                parts = line.strip().split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    serial = parts[-1]
                    serials[serial] = device_id  # reverse dictionary for easier lookup
        return serials
    except Exception as e:
        print(f"Failed to get serial numbers: {e}")
        return {}

def is_whitelisted(serial_number):
    try:
        with open(WHITELIST_FILE, "r") as file:
            whitelisted = [line.strip() for line in file if line.strip()]
        return serial_number in whitelisted
    except FileNotFoundError:
        return False

# -------- MAIN MONITORING LOOP --------

if __name__ == "__main__":
    print("🔄 Monitoring for USB devices...")
    previous_devices = set(get_usb_devices())

    while True:
        time.sleep(2)
        current_devices = set(get_usb_devices())

        new_devices = current_devices - previous_devices
        removed_devices = previous_devices - current_devices

        if new_devices:
            print("\ud83d\udcce New devices detected:", new_devices)

        serials = get_usb_serials()
        print("🔄 Monitoring for USB devices...")

        for device in new_devices:
            found = False
            for serial, dev_id in serials.items():
                if is_whitelisted(serial):
                    log_event("\u2705 Whitelisted USB Connected", f"{device} (Serial: {serial})")
                    found = True
                    break
            if not found:
                log_event("\u274c Unauthorized USB Detected", f"{device} (No matching whitelisted serial)")
                send_email_alert(f"{device} (No matching whitelisted serial)")

        for device in removed_devices:
            log_event("\ud83d\udce4 USB Removed", device)

        previous_devices = current_devices
