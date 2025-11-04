"""
SendGrid email service for sending OTP emails.
"""
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SendGridService:
    """Service for sending emails via SendGrid."""

    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None):
        """
        Initialize SendGrid service.

        Args:
            api_key: SendGrid API key (defaults to SENDGRID_API_KEY env var)
            from_email: Sender email address (defaults to SENDGRID_FROM_EMAIL env var)
        """
        self.api_key = api_key or settings.sendgrid_api_key
        self.from_email = from_email or settings.sendgrid_from_email

        if not self.api_key:
            logger.warning("SendGrid API key not configured")
            raise ValueError("SENDGRID_API_KEY environment variable is required")

        self.client = SendGridAPIClient(self.api_key)
        logger.info(f"SendGrid service initialized with from_email: {self.from_email}")

    async def send_otp_email(
        self,
        to_email: str,
        otp_code: str,
        username: Optional[str] = None
    ) -> bool:
        """
        Send OTP verification email.

        Args:
            to_email: Recipient email address
            otp_code: One-time password code
            username: Optional username for personalization

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create email content
            subject = "Your Verification Code"

            # HTML email template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 40px auto;
                        background: #ffffff;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #4169E1 0%, #1E3A8A 100%);
                        color: #ffffff;
                        padding: 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 24px;
                        font-weight: 600;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .greeting {{
                        font-size: 16px;
                        margin-bottom: 20px;
                    }}
                    .otp-box {{
                        background: #f8f9fa;
                        border: 2px dashed #4169E1;
                        border-radius: 8px;
                        padding: 20px;
                        text-align: center;
                        margin: 30px 0;
                    }}
                    .otp-label {{
                        font-size: 14px;
                        color: #666666;
                        margin-bottom: 10px;
                    }}
                    .otp-code {{
                        font-size: 32px;
                        font-weight: bold;
                        letter-spacing: 8px;
                        color: #4169E1;
                        font-family: 'Courier New', monospace;
                    }}
                    .info {{
                        font-size: 14px;
                        color: #666666;
                        line-height: 1.8;
                    }}
                    .warning {{
                        background: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 15px;
                        margin: 20px 0;
                        font-size: 13px;
                        color: #856404;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 20px 30px;
                        text-align: center;
                        font-size: 12px;
                        color: #666666;
                        border-top: 1px solid #e9ecef;
                    }}
                    .footer a {{
                        color: #4169E1;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Email Verification</h1>
                    </div>
                    <div class="content">
                        <div class="greeting">
                            Hello{' ' + username if username else ''},
                        </div>
                        <p class="info">
                            You've requested to sign in to your account. Please use the verification code below to complete your login:
                        </p>
                        <div class="otp-box">
                            <div class="otp-label">Your Verification Code</div>
                            <div class="otp-code">{otp_code}</div>
                        </div>
                        <p class="info">
                            This code will expire in <strong>5 minutes</strong>. Please do not share this code with anyone.
                        </p>
                        <div class="warning">
                            <strong>⚠️ Security Notice:</strong> If you didn't request this code, please ignore this email or contact support if you have concerns about your account security.
                        </div>
                    </div>
                    <div class="footer">
                        <p>
                            This is an automated message. Please do not reply to this email.
                        </p>
                        <p>
                            Need help? Contact us at <a href="mailto:support@yourdomain.com">support@yourdomain.com</a>
                        </p>
                        <p style="margin-top: 15px; color: #999999;">
                            &copy; 2025 Your Company. All rights reserved.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Plain text fallback
            text_content = f"""
            Hello{' ' + username if username else ''},

            Your verification code is: {otp_code}

            This code will expire in 5 minutes.

            If you didn't request this code, please ignore this email.

            ---
            This is an automated message. Please do not reply.
            """

            # Create Mail object
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", text_content),
                html_content=Content("text/html", html_content)
            )

            # Send email
            response = self.client.send(message)

            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"OTP email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send OTP email to {to_email}. Status: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending OTP email to {to_email}: {str(e)}", exc_info=True)
            return False


# Singleton instance
_sendgrid_service: Optional[SendGridService] = None


def get_sendgrid_service() -> SendGridService:
    """Get or create SendGrid service instance."""
    global _sendgrid_service
    if _sendgrid_service is None:
        _sendgrid_service = SendGridService()
    return _sendgrid_service
