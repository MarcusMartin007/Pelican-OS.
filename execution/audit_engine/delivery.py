import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

class EmailDispatcher:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)

    def is_configured(self):
        return all([self.smtp_host, self.smtp_user, self.smtp_pass])

    def send_audit_report(self, to_email: str, business_name: str, pdf_path: str):
        """
        Sends the audit report PDF as an attachment.
        """
        if not self.is_configured():
            print("⚠️ EMAIL DISPATCHER: SMTP not configured. Skipping email delivery.")
            return False

        print(f"📧 EMAIL DISPATCHER: Preparing email for {to_email}...")

        msg = EmailMessage()
        msg['Subject'] = f"Your AI Visibility Audit: {business_name}"
        msg['From'] = f"Pelican Panache Audit System <{self.from_email}>"
        msg['To'] = to_email

        # Email Body
        body = f"""
Hello,

Your AI Visibility Audit for {business_name} is complete.

Attached is your high-level Visibility Summary PDF. 

This report assesses how AI agents (like ChatGPT, Perplexity, and Gemini) currently perceive and trust your brand across 5 critical visibility layers.

If you have any questions about your score or the recommended "Fastest Score Gains," feel free to reach out.

Best regards,
The Pelican Panache Team
        """
        msg.set_content(body)

        # Attach PDF
        try:
            with open(pdf_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(pdf_path)
                msg.add_attachment(
                    file_data,
                    maintype='application',
                    subtype='pdf',
                    filename=file_name
                )
        except Exception as e:
            print(f"❌ EMAIL ERROR: Could not read PDF attachment: {e}")
            return False

        # Send
        try:
            if self.smtp_port == 465:
                # Use SSL for port 465
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                    server.login(self.smtp_user, self.smtp_pass)
                    server.send_message(msg)
            else:
                # Use TLS for other ports (587, 25)
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_pass)
                    server.send_message(msg)
            print(f"✅ EMAIL SENT: Audit report delivered to {to_email}")
            return True
        except Exception as e:
            print(f"❌ EMAIL ERROR: Failed to send via SMTP: {e}")
            return False
