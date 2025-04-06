import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv


load_dotenv()


def send_email(subject: str, to_email: str, content: str):
    smtp_host = "sandbox.smtp.mailtrap.io"
    smtp_port = 587
    smtp_user = os.getenv("MAILTRAP_USERNAME", "YOUR_MAILTRAP_USERNAME")
    smtp_pass = os.getenv("MAILTRAP_USER_PASSWORD", "YOUR_MAILTRAP_PASSWORD")

    from_email = os.getenv("MAILTRAP_EMAIL", "YOUR_MAILTRAP_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(content, "plain"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")


def send_activation_email(to_email: str, activation_token: str):
    subject = "Activate Your Account"
    content = (f"Use the following token "
               f"to activate your account: {activation_token}")
    send_email(subject, to_email, content)


def send_password_reset_email(to_email: str, reset_token: str):
    subject = "Reset Your Password"
    content = f"Use the following token to reset your password: {reset_token}"
    send_email(subject, to_email, content)
