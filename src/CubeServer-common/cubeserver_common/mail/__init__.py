"""Handles sending emails"""

import smtplib
from email.mime.text import MIMEText

from cubeserver_common.models.config.conf import Conf

class Message:
    """Describes an email to be sent"""

    def __init__(
        self,
        from_name: str,
        from_addr: str,
        recipients: list[str],
        subject: str,
        message: str
    ) -> None:
        self.message = MIMEText(message)
        self.message['Subject'] = subject
        self.message['From'] = f"{from_name} <{from_addr}>"
        self.message['To'] = ', '.join(recipients)

        self.from_addr = from_addr
        self.to_addrs = recipients

    def send(self) -> bool:
        """Sends the message.
        Or at least tries to.
        Returns True if we think it worked."""
        success = True
        config: Conf = Conf.retrieve_instance()
        s = smtplib.SMTP(config.smtp_server)
        try:
            s.ehlo_or_helo_if_needed()
            s.starttls()
            if config.smtp_user is not None and config.smtp_user.strip() != '':
                s.login(config.smtp_user, config.smtp_pass)
            s.sendmail(self.from_addr, self.to_addrs, self.message.as_string())
        except smtplib.SMTPException:
            print("we had a little oopsie with the SMTP server...")
            success = False
        finally:
            s.quit()
            s.close()
        return success
