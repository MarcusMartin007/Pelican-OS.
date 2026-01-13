import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition
)

class EmailDispatcher:
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL")

    def is_configured(self):
        return all([self.api_key, self.from_email])

    def send_audit_report(self, to_email: str, business_name: str, pdf_path: str):
        """
        Sends the audit report PDF as an attachment using the SendGrid Web API.
        """
        if not self.is_configured():
            print("⚠️ EMAIL DISPATCHER: SendGrid API not configured (SENDGRID_API_KEY or FROM_EMAIL missing). Skipping email delivery.")
            return False

        print(f"📧 EMAIL DISPATCHER: Preparing SendGrid email for {to_email}...")

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=f"Your AI Visibility Audit: {business_name}",
            html_content=f"""
                <p>Hello,</p>
                <p>Your AI Visibility Audit for <strong>{business_name}</strong> is complete.</p>
                <p>Attached is your high-level Visibility Summary PDF.</p>
                <p>This report assesses how AI agents (like ChatGPT, Perplexity, and Gemini) currently perceive and trust your brand across 5 critical visibility layers.</p>
                <p>If you have any questions about your score or the recommended "Fastest Score Gains," feel free to reach out.</p>
                <p>Best regards,<br>
                The Pelican Panache Team</p>
            """
        )

        # Attach PDF
        try:
            with open(pdf_path, 'rb') as f:
                data = f.read()
                f.close()
            encoded_file = base64.b64encode(data).decode()

            attachedFile = Attachment(
                FileContent(encoded_file),
                FileName(os.path.basename(pdf_path)),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            message.attachment = attachedFile
        except Exception as e:
            print(f"❌ EMAIL ERROR: Could not prepare PDF attachment: {e}")
            return False

        # Send
        try:
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            print(f"✅ EMAIL SENT: Audit report delivered to {to_email} (Status Code: {response.status_code})")
            return True
        except Exception as e:
            print(f"❌ EMAIL ERROR: Failed to send via SendGrid API: {e}")
            return False
