"""
Email Service Abstraction Layer
Supports console logging (dev), Mailgun, Brevo, and AWS SES
"""
import os
from abc import ABC, abstractmethod
from typing import Optional, List
from enum import Enum
import structlog

logger = structlog.get_logger()


class EmailProvider(str, Enum):
    CONSOLE = "console"  # FREE - just logs to console
    SMTP = "smtp"  # FREE - Gmail/custom SMTP
    MAILGUN = "mailgun"  # FREE tier: 5,000 emails/month
    BREVO = "brevo"  # FREE tier: 300 emails/day
    MAILERSEND = "mailersend"  # FREE tier: 12,000 emails/month
    SES = "ses"  # PAID - AWS SES


class EmailMessage:
    """Standard email message structure"""

    def __init__(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ):
        self.to = to
        self.subject = subject
        self.html_body = html_body
        self.text_body = text_body
        self.from_email = from_email
        self.reply_to = reply_to
        self.cc = cc or []
        self.bcc = bcc or []


class BaseEmailProvider(ABC):
    """Abstract base class for email providers"""

    @abstractmethod
    async def send_email(self, message: EmailMessage) -> bool:
        """Send a single email"""
        pass

    @abstractmethod
    async def send_batch(self, messages: List[EmailMessage]) -> dict:
        """Send multiple emails"""
        pass


class ConsoleEmailProvider(BaseEmailProvider):
    """
    Console email provider (FREE - for development)
    Just logs email details instead of sending
    """

    async def send_email(self, message: EmailMessage) -> bool:
        """Log email instead of sending"""
        logger.info(
            "email_would_be_sent",
            to=message.to,
            subject=message.subject,
            from_email=message.from_email,
            body_preview=message.html_body[:200] + "..."
        )
        print("\n" + "="*80)
        print(f"📧 EMAIL WOULD BE SENT")
        print("="*80)
        print(f"To: {message.to}")
        print(f"From: {message.from_email}")
        print(f"Subject: {message.subject}")
        print("-"*80)
        print(f"HTML Body Preview:\n{message.html_body[:500]}")
        print("="*80 + "\n")
        return True

    async def send_batch(self, messages: List[EmailMessage]) -> dict:
        """Log batch of emails"""
        for message in messages:
            await self.send_email(message)
        return {"sent": len(messages), "failed": 0}


class SMTPProvider(BaseEmailProvider):
    """
    SMTP email provider (FREE - works with Gmail, etc.)
    Supports standard SMTP protocol
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        use_tls: bool = True
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls

    async def send_email(self, message: EmailMessage) -> bool:
        """Send email via SMTP"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = message.from_email or self.smtp_username
            msg['To'] = message.to

            # Add both plain text and HTML parts
            if message.text_body:
                text_part = MIMEText(message.text_body, 'plain')
                msg.attach(text_part)

            html_part = MIMEText(message.html_body, 'html')
            msg.attach(html_part)

            # Connect and send
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)

            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(msg['From'], [message.to], msg.as_string())
            server.quit()

            logger.info("email_sent_via_smtp", to=message.to, subject=message.subject)
            return True

        except Exception as e:
            logger.error("smtp_send_failed", error=str(e), to=message.to)
            return False

    async def send_batch(self, messages: List[EmailMessage]) -> dict:
        """Send batch via SMTP"""
        sent = 0
        failed = 0
        for message in messages:
            success = await self.send_email(message)
            if success:
                sent += 1
            else:
                failed += 1
        return {"sent": sent, "failed": failed}


class MailgunProvider(BaseEmailProvider):
    """
    Mailgun email provider
    FREE tier: 5,000 emails/month for 3 months, then $35/month
    """

    def __init__(self, api_key: str, domain: str):
        import httpx
        self.api_key = api_key
        self.domain = domain
        self.client = httpx.AsyncClient(
            base_url=f"https://api.mailgun.net/v3/{domain}",
            auth=("api", api_key)
        )

    async def send_email(self, message: EmailMessage) -> bool:
        """Send email via Mailgun"""
        try:
            response = await self.client.post(
                "/messages",
                data={
                    "from": message.from_email or f"noreply@{self.domain}",
                    "to": message.to,
                    "subject": message.subject,
                    "html": message.html_body,
                    "text": message.text_body or "",
                }
            )
            response.raise_for_status()
            logger.info("email_sent_via_mailgun", to=message.to, subject=message.subject)
            return True
        except Exception as e:
            logger.error("mailgun_send_failed", error=str(e), to=message.to)
            return False

    async def send_batch(self, messages: List[EmailMessage]) -> dict:
        """Send batch via Mailgun"""
        sent = 0
        failed = 0
        for message in messages:
            success = await self.send_email(message)
            if success:
                sent += 1
            else:
                failed += 1
        return {"sent": sent, "failed": failed}


class BrevoProvider(BaseEmailProvider):
    """
    Brevo (formerly Sendinblue) email provider
    FREE tier: 300 emails/day
    """

    def __init__(self, api_key: str):
        import httpx
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url="https://api.brevo.com/v3",
            headers={"api-key": api_key}
        )

    async def send_email(self, message: EmailMessage) -> bool:
        """Send email via Brevo"""
        try:
            response = await self.client.post(
                "/smtp/email",
                json={
                    "sender": {"email": message.from_email or "noreply@example.com"},
                    "to": [{"email": message.to}],
                    "subject": message.subject,
                    "htmlContent": message.html_body,
                    "textContent": message.text_body or ""
                }
            )
            response.raise_for_status()
            logger.info("email_sent_via_brevo", to=message.to, subject=message.subject)
            return True
        except Exception as e:
            logger.error("brevo_send_failed", error=str(e), to=message.to)
            return False

    async def send_batch(self, messages: List[EmailMessage]) -> dict:
        """Send batch via Brevo"""
        sent = 0
        failed = 0
        for message in messages:
            success = await self.send_email(message)
            if success:
                sent += 1
            else:
                failed += 1
        return {"sent": sent, "failed": failed}


class SESProvider(BaseEmailProvider):
    """
    AWS SES email provider (PAID - for production)
    $0.10 per 1,000 emails
    """

    def __init__(self, aws_access_key: str, aws_secret_key: str, region: str = "us-east-1"):
        import boto3
        self.client = boto3.client(
            'ses',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

    async def send_email(self, message: EmailMessage) -> bool:
        """Send email via AWS SES"""
        try:
            response = self.client.send_email(
                Source=message.from_email or "noreply@example.com",
                Destination={
                    'ToAddresses': [message.to],
                    'CcAddresses': message.cc,
                    'BccAddresses': message.bcc
                },
                Message={
                    'Subject': {'Data': message.subject},
                    'Body': {
                        'Html': {'Data': message.html_body},
                        'Text': {'Data': message.text_body or ''}
                    }
                }
            )
            logger.info("email_sent_via_ses", to=message.to, message_id=response['MessageId'])
            return True
        except Exception as e:
            logger.error("ses_send_failed", error=str(e), to=message.to)
            return False

    async def send_batch(self, messages: List[EmailMessage]) -> dict:
        """Send batch via SES"""
        sent = 0
        failed = 0
        for message in messages:
            success = await self.send_email(message)
            if success:
                sent += 1
            else:
                failed += 1
        return {"sent": sent, "failed": failed}


class EmailProviderFactory:
    """Factory for creating email provider clients"""

    @staticmethod
    def create_client(provider: Optional[str] = None) -> BaseEmailProvider:
        """
        Create an email provider client based on environment configuration

        Args:
            provider: Override the configured provider

        Returns:
            BaseEmailProvider instance
        """
        provider = provider or os.getenv("EMAIL_PROVIDER", "console")

        if provider == EmailProvider.CONSOLE:
            return ConsoleEmailProvider()

        elif provider == EmailProvider.SMTP:
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

            if not smtp_username or not smtp_password:
                raise ValueError("SMTP_USERNAME and SMTP_PASSWORD required")

            return SMTPProvider(
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                smtp_username=smtp_username,
                smtp_password=smtp_password,
                use_tls=use_tls
            )

        elif provider == EmailProvider.MAILGUN:
            api_key = os.getenv("MAILGUN_API_KEY")
            domain = os.getenv("MAILGUN_DOMAIN")
            if not api_key or not domain:
                raise ValueError("MAILGUN_API_KEY and MAILGUN_DOMAIN required")
            return MailgunProvider(api_key=api_key, domain=domain)

        elif provider == EmailProvider.BREVO:
            api_key = os.getenv("BREVO_API_KEY")
            if not api_key:
                raise ValueError("BREVO_API_KEY required")
            return BrevoProvider(api_key=api_key)

        elif provider == EmailProvider.SES:
            aws_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
            region = os.getenv("AWS_REGION", "us-east-1")
            if not aws_key or not aws_secret:
                raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY required")
            return SESProvider(
                aws_access_key=aws_key,
                aws_secret_key=aws_secret,
                region=region
            )

        else:
            raise ValueError(f"Unsupported email provider: {provider}")


# Singleton instance
_email_client: Optional[BaseEmailProvider] = None


def get_email_client() -> BaseEmailProvider:
    """Get or create the global email provider client"""
    global _email_client
    if _email_client is None:
        _email_client = EmailProviderFactory.create_client()
    return _email_client
