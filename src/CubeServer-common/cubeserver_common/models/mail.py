"""Handles sending emails"""

import smtplib
from email.mime.text import MIMEText
from datetime import datetime

from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.utils.modelutils import PyMongoModel
from cubeserver_common.models.utils.dummycodec import DummyCodec

class Message(PyMongoModel):
    """Describes an email to be sent"""

    def __init__(
        self,
        from_name: str = "",
        from_addr: str = "",
        recipients: list[str] = [],
        subject: str = "",
        message: str = ""
    ) -> None:
        super().__init__()
        self.from_addr = from_addr
        self.recipients = recipients
        self.from_name = from_name
        self.subject = subject
        self.message = message

        self.register_field('sent_at', custom_codec=DummyCodec(datetime))
        self._ignored += ['_mimetext']

    @property
    def sender_str(self) -> str:
        return f"{self.from_name} <{self.from_addr}>"

    def send(self) -> bool:
        """Sends the message.
        Or at least tries to.
        Returns True if we think it worked."""

        if self.from_addr is None:
            raise TypeError("Cannot send empty message")

        self._mimetext = MIMEText(self.message)
        self._mimetext['Subject'] = self.subject
        self._mimetext['From'] = self.sender_string
        self._mimetext['To'] = ', '.join(self.recipients)

        success = True
        config: Conf = Conf.retrieve_instance()
        s = smtplib.SMTP(config.smtp_server)
        try:
            s.ehlo_or_helo_if_needed()
            s.starttls()
            if config.smtp_user is not None and config.smtp_user.strip() != '':
                s.login(config.smtp_user, config.smtp_pass)
            s.sendmail(self.from_addr, self.recipients, self._mimetext.as_string())
            self.sent_at = datetime.now()
        except smtplib.SMTPException:
            print("we had a little oopsie with the SMTP server...")
            success = False
        finally:
            s.quit()
            s.close()
        if success:  # Save into database of messages if it sent okay...
            self.save()
        return success
