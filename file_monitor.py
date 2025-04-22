import os
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ====== CONFIGURATION ======
monitored_folder = "D:\\usb detection project"
LOG_FILE = "log.txt"

# Email setup (optional toggle)
ENABLE_EMAIL_ALERTS = False
SENDER_EMAIL = "accessguard.file@gmail.com"
APP_PASSWORD = "qwfx jdmw cane tgev"
RECIPIENT_EMAIL = "8904subhamd@gmail.com"

# ====== FUNCTIONS ======

def log_event(message):
    """Logs message with timestamp and emoji."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

def send_email_alert(subject, body):
    """Sends an email alert (optional)."""
    if not ENABLE_EMAIL_ALERTS:
        return

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
        print("📧 Email alert sent.")
    except Exception as e:
        print(f"❗ Email sending failed: {e}")

# ====== MAIN MONITORING ======
if not os.path.exists(monitored_folder):
    log_event(f"❗ Monitored folder '{monitored_folder}' does not exist.")
    exit()

files_state = {}
for file in os.listdir(monitored_folder):
    full_path = os.path.join(monitored_folder, file)
    if os.path.isfile(full_path):
        files_state[file] = os.stat(full_path).st_mtime

log_event(f"🟡 Started monitoring files in '{monitored_folder}'.")

while True:
    try:
        current_files_state = {}
        for file in os.listdir(monitored_folder):
            full_path = os.path.join(monitored_folder, file)
            if os.path.isfile(full_path):
                current_files_state[file] = os.stat(full_path).st_mtime

        # Check for new or modified files
        for file, mtime in current_files_state.items():
            if file not in files_state:
                msg = f"✅ New file detected: {file}"
                log_event(msg)
                send_email_alert("New File Detected", msg)
            elif files_state[file] != mtime:
                msg = f"✏️ File modified: {file}"
                log_event(msg)
                send_email_alert("File Modified", msg)

        # Check for deleted files
        for file in files_state:
            if file not in current_files_state:
                msg = f"❌ File deleted: {file}"
                log_event(msg)
                send_email_alert("File Deleted", msg)

        files_state = current_files_state
        time.sleep(5)

    except Exception as e:
        log_event(f"❗ Monitoring error: {e}")
        time.sleep(5)