"""Handles sending emails"""

import smtplib
import logging
from email.mime.text import MIMEText
from datetime import datetime
from typing import Optional, List
from bson.objectid import ObjectId

from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.utils.modelutils import PyMongoModel
from cubeserver_common.models.utils.dummycodec import DummyCodec
#from cubeserver_common.models.team import Team  # Creates circular import; removed

class Message(PyMongoModel):
    """Describes an email to be sent"""

    def __init__(
        self,
        from_name: str = "",
        from_addr: str = "",
        recipients: list[str] = [],
        subject: str = "",
        message: str = "",
        team_identifier: Optional[ObjectId] = None
    ) -> None:
        super().__init__()
        self.from_addr = from_addr
        self.recipients = recipients
        self.from_name = from_name
        self.subject = subject
        self.message = message
        self.team_reference = team_identifier

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
        self._mimetext['From'] = self.sender_str
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
            logging.error("we had a little oopsie with the SMTP server...")
            success = False
        finally:
            s.quit()
            s.close()
        if success:  # Save into database of messages if it sent okay...
            self.save()
        return success

    @classmethod  # TODO: Structure other "find_by..."'s similarly to reduce repetitive code:
    def find_by_team(cls, team: ObjectId | str | None) -> List['Message']:
        """Returns a list of Messages sent by this team"""
        if isinstance(team, ObjectId):
            team_id = team
#        elif isinstance(team, Team):  # Circular import; removed.
#            team_id = team.id         # TODO: Add back in with issue #134
        elif isinstance(team, str):
            team_id = ObjectId(team)
        elif team is None:
            team_id = None
        else:
            raise TypeError("Invalid type with which to filter messages by team")

        return cls.find({"team_reference": team_id})
