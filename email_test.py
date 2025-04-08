import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Sender and recipient details
sender_email = "accessguard.file@gmail.com"
app_password = "qwfx jdmw cane tgev"  # Replace with your actual App Password
recipient_email = "8904subhamd@gmail.com"

subject = "Test Email from AccessGuard"
body = "This is a test email to verify the email setup in AccessGuard project."

# Function to log email status
def write_log(message):
    with open("log.txt", "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Compose the email
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = recipient_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

# Send the email
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

    print("Email sent successfully!")
    write_log(f"[EMAIL TEST] Email sent successfully to {recipient_email}")
except Exception as e:
    print(f"Failed to send email: {e}")
    write_log(f"[EMAIL TEST FAILED] Error: {e}")
