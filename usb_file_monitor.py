import os
import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time

sender_email = "accessguard.file@gmail.com"
app_password = "qwfx jdmw cane tgev"  # Replace with your actual App Password
recipient_email = "8904subhamd@gmail.com"

system_id = os.environ.get("COMPUTERNAME", "Hp pavilion laptop 15")
user_id = os.environ.get("USERNAME", "LAPTOP-48T8EO3C")

# Function to write logs
def write_log(message):
    with open("log.txt", "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Function to send professional email with HTML formatting
def send_email(subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    html_body = f"""
    <html>
      <body>
        <h2 style="color: red;">AccessGuard Alert</h2>
        <p>
          <strong style="color: darkred;">System ID:</strong> {system_id}<br>
          <strong style="color: darkred;">User ID:</strong> {user_id}<br>
          <strong style="color: darkred;">Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        </p>
        <p>{body}</p>
        <p>Please verify the action and ensure no unauthorized activity occurs.</p>
      </body>
    </html>
    """
    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email sent successfully!")
        write_log(f"[EMAIL SENT] Subject: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        write_log(f"[EMAIL FAILED] Subject: {subject} | Error: {e}")

# Function to detect USB insertion and monitor files
def detect_usb_and_monitor_files():
    initial_devices = {part.device for part in psutil.disk_partitions()}
    print("Monitoring for USB device insertion...")

    monitored_folder = "D:\\usb detection project"
    files_state = {}

    while True:
        # Detect new USB devices
        current_devices = {part.device for part in psutil.disk_partitions()}
        new_devices = current_devices - initial_devices

        if new_devices:
            for device in new_devices:
                body = f"A new USB device has been inserted: {device}."
                send_email("USB Device Inserted", body)
                write_log(f"[USB DETECTED] New device inserted: {device}")

        initial_devices = current_devices

        # Monitor folder for file changes
        try:
            current_files_state = {
                file: os.stat(os.path.join(monitored_folder, file)).st_mtime
                for file in os.listdir(monitored_folder)
            }

            for file, last_modified in current_files_state.items():
                file_path = os.path.join(monitored_folder, file)
                if file not in files_state:
                    body = f"A new file has been added: {file}.\nFile path: {file_path}"
                    send_email("New File Detected", body)
                    write_log(f"[FILE ADDED] {file_path}")
                elif files_state[file] != last_modified:
                    body = f"The file {file} has been modified.\nFile path: {file_path}"
                    send_email("File Modified", body)
                    write_log(f"[FILE MODIFIED] {file_path}")

            files_state = current_files_state

        except FileNotFoundError:
            print(f"Folder {monitored_folder} not found for monitoring.")
            write_log(f"[ERROR] Folder not found: {monitored_folder}")

        time.sleep(5)

# Start monitoring
detect_usb_and_monitor_files()
