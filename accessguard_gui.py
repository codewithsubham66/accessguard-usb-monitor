import os
import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
import threading
import tkinter as tk

sender_email = "accessguard.file@gmail.com"
app_password = "qwfx jdmw cane tgev"  
recipient_email = "8904subhamd@gmail.com"  

system_id = os.environ.get("COMPUTERNAME", "HP Pavilion Laptop 15")  
user_id = os.environ.get("USERNAME", "LAPTOP-48T8EO3C")  

#  This is the Function to send  email
def send_email(subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # this is the  HTML code to format the email content
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
    except Exception as e:
        print(f"Failed to send email: {e}")

#  This is the Function to display a professional alert box
def show_classical_alert(title, message):
    popup = tk.Toplevel()
    popup.title(title)
    popup.geometry("400x200")
    popup.resizable(False, False)  

    popup.config(bg="#F0F0F0")  

    title_label = tk.Label(
        popup, text=title, font=("Helvetica", 16, "bold"), fg="#333333", bg="#F0F0F0"
    )
    title_label.pack(pady=(20, 10))

    message_label = tk.Label(
        popup, text=message, font=("Helvetica", 12), fg="#555555", bg="#F0F0F0", wraplength=360, justify="center"
    )
    message_label.pack(padx=20, pady=(0, 20))

    # OK Button
    close_button = tk.Button(
        popup,
        text="Clear!",
        command=popup.destroy,
        font=("Helvetica", 12),
        bg="#007BFF",
        fg="white",
        activebackground="#0056b3",
        activeforeground="white",
        width=10,
    )
    close_button.pack(pady=(10, 20))

    popup.transient()
    popup.grab_set()
    popup.focus_force()

def detect_usb_and_monitor_files(status_label, stop_event):
    initial_devices = {part.device for part in psutil.disk_partitions()}
    print("Monitoring for USB device insertion...")

    monitored_folder = "D:\\usb detection project"

    # Initialize file state with the folder's current contents
    try:
        files_state = {file: os.stat(os.path.join(monitored_folder, file)).st_mtime
                       for file in os.listdir(monitored_folder)}
    except FileNotFoundError:
        files_state = {}
        print(f"Folder {monitored_folder} not found for monitoring.")

    while not stop_event.is_set():
        #This code is for Detect new USB devices
        current_devices = {part.device for part in psutil.disk_partitions()}
        new_devices = current_devices - initial_devices

        if new_devices:
            for device in new_devices:
                body = f"A new USB device has been inserted: {device}."
                send_email("USB Device Inserted", body)
                show_classical_alert("USB Detected", f"New USB device detected: {device}")

        initial_devices = current_devices

        try:
            current_files_state = {file: os.stat(os.path.join(monitored_folder, file)).st_mtime
                                   for file in os.listdir(monitored_folder)}

            for file, last_modified in current_files_state.items():
                if file not in files_state:
                
                    body = f"A new file has been added: {file}.\nFile path: {os.path.join(monitored_folder, file)}"
                    send_email("New File Detected", body)
                    show_classical_alert("File Added", f"New file detected: {file}")

                elif files_state[file] != last_modified:
                    # This is the Alert for a modified file
                    body = f"The file {file} has been modified.\nFile path: {os.path.join(monitored_folder, file)}"
                    send_email("File Modified", body)
                    show_classical_alert("File Modified", f"File modified: {file}")

            # Update files state
            files_state = current_files_state

        except FileNotFoundError:
            print(f"Folder {monitored_folder} not found for monitoring.")

        time.sleep(5)

# This is the GUI Application with using Tkinter
class AccessGuardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AccessGuard - Monitoring System")
        self.root.geometry("500x300")
        self.root.config(bg="#2E3B4E")  
        self.is_monitoring = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()

        self.label = tk.Label(
            self.root, text="Welcome to AccessGuard!", font=("Helvetica", 18), fg="white", bg="#2E3B4E"
        )
        self.label.pack(pady=20)

        self.start_button = tk.Button(
            self.root, text="Start Monitoring", command=self.start_monitoring, font=("Helvetica", 14), bg="#3F8EFC", fg="white", width=20
        )
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(
            self.root, text="Stop Monitoring", command=self.stop_monitoring, font=("Helvetica", 14), bg="#FC5C65", fg="white", width=20
        )
        self.stop_button.pack(pady=10)
        self.stop_button.config(state=tk.DISABLED)

        self.status_label = tk.Label(
            self.root, text="Status: Not Monitoring", font=("Helvetica", 12), fg="white", bg="#2E3B4E"
        )
        self.status_label.pack(pady=10)

    def start_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.stop_event.clear()
            self.status_label.config(text="Status: Monitoring in Progress", fg="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.monitoring_thread = threading.Thread(
                target=detect_usb_and_monitor_files, args=(self.status_label, self.stop_event)
            )
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()

    def stop_monitoring(self):
        if self.is_monitoring:
            self.is_monitoring = False
            self.stop_event.set()
            self.status_label.config(text="Status: Monitoring Stopped", fg="red")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

# this is the code for Running  the Tkinter app
if __name__ == "__main__":
    root = tk.Tk()
    app = AccessGuardApp(root)
    root.mainloop()
