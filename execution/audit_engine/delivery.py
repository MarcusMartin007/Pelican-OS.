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
        self.bcc_email = os.getenv("BCC_EMAIL")

    def is_configured(self):
        return all([self.api_key, self.from_email])

    def send_audit_report(self, to_email: str, business_name: str, pdf_path: str, contact_name: str = None, 
                          score: int = 0, custom_body: str = None, strongest: str = None, bottleneck: str = None):
        """
        Sends the audit report PDF as an attachment using the SendGrid Web API.
        Uses a custom AI-generated body or falls back to a template.
        """
        if not self.is_configured():
            print("⚠️ EMAIL DISPATCHER: SendGrid API not configured (SENDGRID_API_KEY or FROM_EMAIL missing). Skipping email delivery.")
            return False

        first_name = contact_name.split()[0] if contact_name else "Guest"
        
        # Use AI-generated body if provided, otherwise fallback to template
        if custom_body:
            print(f"📧 EMAIL DISPATCHER: Using personalized AI-generated body for {to_email}")
            # Ensure newlines are converted to HTML breaks since SendGrid expects HTML
            html_body = custom_body.replace('\n', '<br>')
        else:
            print(f"📧 EMAIL DISPATCHER: AI generation failed or skipped. Using smart fallback for {to_email}")
            
            # Determine visibility range description
            if score < 25:
                range_desc = "foundational visibility range"
                benchmark_text = "" # Don't show benchmark for very low scores
            elif score <= 75:
                range_desc = "early visibility range"
                benchmark_text = "<p>Most brands scoring between 55 and 75 see meaningful improvement once these gaps are addressed.</p>"
            else:
                range_desc = "advanced visibility range"
                benchmark_text = "<p>Your brand is in a strong position to dominate AI-driven search results.</p>"

            # Smart phrasing for takeaways
            if strongest and "No dominant strengths" not in strongest:
                str_text = f"Your strongest signal is <strong>{strongest}</strong>."
            else:
                str_text = "Your digital presence is currently in a <strong>foundational building phase</strong> (no dominant strengths detected yet)."

            if bottleneck:
                bn_text = f"Your biggest constraint is <strong>{bottleneck}</strong>."
            else:
                bn_text = "Your biggest constraint involves a <strong>lack of verifiable brand authority and semantic structure</strong>."
            
            html_body = f"""
                <p>Hello {first_name},</p>
                
                <p>Your AI Visibility Audit is complete.</p>
                
                <p>Your current AI Visibility Score is <strong>{score}</strong>, which places your brand in the {range_desc}. AI systems can find and understand your business, but they are not yet confident enough to consistently cite or recommend it.</p>
                
                <p>Attached is your AI Visibility Summary PDF. It breaks down how AI agents like ChatGPT, Perplexity, and Gemini interpret your brand across five critical layers.</p>
                
                <p><strong>Here is the key takeaway:</strong></p>
                
                <p>{str_text}<br>
                {bn_text}</p>
                
                <p>This means your systems are ready to convert attention, but AI lacks the clarity and third-party validation required to send that attention consistently.</p>
                
                <p>Inside the report you will find:
                <ul>
                    <li>Your full layer-by-layer score breakdown</li>
                    <li>The primary visibility bottleneck limiting growth</li>
                    <li>The fastest actions to unlock score gains</li>
                </ul></p>
                
                {benchmark_text}
                
                <p>If you would like help turning this score into measurable AI-driven visibility and lead flow, the next step is a short strategy session to map the fastest path forward.</p>
                
                <p>Best regards,<br>
                <strong>Marcus Martin</strong><br>
                Founder, Pelican Panache</p>
            """

        print(f"📧 EMAIL DISPATCHER: Sending SendGrid email to {to_email}...")

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject="Your AI Visibility Score Is Ready",
            html_content=html_body
        )

        if self.bcc_email:
            message.add_bcc(self.bcc_email)

        # Attach PDF
        try:
            with open(pdf_path, 'rb') as f:
                data = f.read()
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
