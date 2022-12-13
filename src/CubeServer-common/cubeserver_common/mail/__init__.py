"""Handles sending emails"""

import smtplib
from email.mime.text import MIMEText

class Message:
    """Describes an email to be sent"""

    def __init__(
        self,
        from_name: str,
        from_addr: str,
        to: list[str],
        subject: str,
        message: str
    ) -> None:
        self.message = MIMEText(message)
        self.message['Subject'] = subject
        self.message['From'] = f"{from_name} <{from_addr}>"
        self.message['To'] = to

        self.from_addr = from_addr
        self.to_addrs = to

    def send(self) -> bool:
        """Sends the message.
        Or at least tries to.
        Returns True if we think it worked."""
        success = True
        s = smtplib.SMTP()
        s.connect()
        try:
            s.ehlo_or_helo_if_needed()
            s.starttls()
            s.sendmail(self.from_addr, self.to_addrs, self.message.as_string())
        except smtplib.SMTPHeloError:
            print("we had a little oopsie with the SMTP server...")
            success = False
        finally:
            s.quit()
            s.close()
        return success
