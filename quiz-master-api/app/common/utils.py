import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import Config

def send_email(to_email, subject, body):
    """
    Sends an email using Gmail SMTP.
    """
    smtp_user = Config.IITM_EMAIL_USER
    smtp_pass = Config.IITM_EMAIL_PASS
    if not smtp_user or not smtp_pass:
        raise Exception("SMTP credentials not set in environment variables.")
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def make_response(success, message=None, data=None, error_message=None):
    resp = {"success": success}
    if message:
        resp["message"] = message
    if data is not None:
        resp["data"] = data
    if not success and error_message:
        resp["error_message"] = error_message
    from flask import jsonify
    return jsonify(resp)
