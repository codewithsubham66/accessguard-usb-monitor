import os
import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
import subprocess  # Required for retrieving USB serial numbers

# Email Config
sender_email = "accessguard.file@gmail.com"
app_password = "qwfx jdmw cane tgev"
recipient_email = "8904subhamd@gmail.com"

system_id = os.environ.get("COMPUTERNAME", "Hp pavilion laptop 15")
user_id = os.environ.get("USERNAME", "LAPTOP-48T8EO3C")

monitored_folder = "D:\\usb detection project"
files_state = {}
WHITELIST_FILE = "usb_whitelist.txt"  # Ensure this file exists with whitelisted serials

# Log Function
def write_log(message):
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Email Function
def send_email(subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    html_body = f"""
    <html>
      <body>
        <h2 style="color: red;">AccessGuard Alert 🚨</h2>
        <p><strong>System ID:</strong> {system_id}<br>
           <strong>User ID:</strong> {user_id}<br>
           <strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>{body}</p>
        <p style="color:gray;">AccessGuard - USB & File Monitoring System</p>
      </body>
    </html>
    """
    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("📧 Email sent!")
        write_log(f"[EMAIL SENT] {subject}")
    except Exception as e:
        print(f"❌ Email failed: {e}")
        write_log(f"[EMAIL FAILED] {subject} | Error: {e}")

# Check if USB device is whitelisted
def is_whitelisted(serial_number):
    try:
        with open(WHITELIST_FILE, "r") as file:
            whitelisted = [line.strip() for line in file if line.strip()]
        return serial_number in whitelisted
    except FileNotFoundError:
        print("Whitelist file not found.")
        return False

# Get USB Serial Numbers (Function Added)
def get_usb_serials():
    """Retrieve the serial numbers of connected USB devices using WMIC."""
    try:
        result = subprocess.check_output('wmic diskdrive get DeviceID,SerialNumber,InterfaceType', shell=True).decode()
        lines = result.strip().split('\n')[1:]
        serials = {}
        for line in lines:
            if 'USB' in line:
                parts = line.strip().split()
                if len(parts) >= 2:
                    serial = parts[-1]
                    serials[serial] = parts[0]  # mapping serial to device ID
        return serials
    except Exception as e:
        print(f"❗ Failed to get USB serials: {e}")
        return {}

# Main Function to Detect USB and Monitor Files
def detect_usb_and_monitor_files():
    print("🔄 AccessGuard Running... Waiting for USBs and File Changes")
    initial_devices = {part.device for part in psutil.disk_partitions()}

    while True:
        # USB Detection
        current_devices = {part.device for part in psutil.disk_partitions()}
        new_devices = current_devices - initial_devices

        for device in new_devices:
            # Retrieve the serial numbers of connected USB devices
            serials = get_usb_serials()  # This function is now implemented
            device_is_whitelisted = False
            
            for serial, dev_id in serials.items():
                if is_whitelisted(serial):
                    device_is_whitelisted = True
                    break

            if device_is_whitelisted:
                body = f"A whitelisted USB device has been inserted: <b>{device}</b>."
                send_email("🔌 Whitelisted USB Device Detected", body)
                write_log(f"[USB DETECTED] Whitelisted device: {device}")
            else:
                body = f"An unauthorized USB device has been inserted: <b>{device}</b>."
                send_email("🚨 Unauthorized USB Device Detected", body)
                write_log(f"[USB DETECTED] Unauthorized device: {device}")

        initial_devices = current_devices

        # File Monitoring
        try:
            if not os.path.exists(monitored_folder):
                raise FileNotFoundError

            current_files_state = {}
            for file in os.listdir(monitored_folder):
                file_path = os.path.join(monitored_folder, file)
                try:
                    mtime = os.stat(file_path).st_mtime
                    current_files_state[file] = mtime
                except FileNotFoundError:
                    continue  # File might have been deleted while looping
                except PermissionError:
                    write_log(f"[PERMISSION ERROR] {file_path}")
                    continue

            # Detect Add or Modify
            for file, mtime in current_files_state.items():
                if file not in files_state:
                    send_email("🆕 New File Detected", f"New file added: <b>{file}</b>")
                    write_log(f"[FILE ADDED] {file}")
                elif files_state[file] != mtime:
                    send_email("✏️ File Modified", f"File modified: <b>{file}</b>")
                    write_log(f"[FILE MODIFIED] {file}")

            # Detect Delete
            deleted_files = set(files_state.keys()) - set(current_files_state.keys())
            for file in deleted_files:
                send_email("🗑️ File Deleted", f"The file <b>{file}</b> was deleted.")
                write_log(f"[FILE DELETED] {file}")

            files_state.clear()
            files_state.update(current_files_state)

        except FileNotFoundError:
            print(f"⚠️ Folder not found: {monitored_folder}")
            write_log(f"[FOLDER MISSING] {monitored_folder}")

        time.sleep(5)

# Run
if __name__ == "__main__":
    detect_usb_and_monitor_files()
