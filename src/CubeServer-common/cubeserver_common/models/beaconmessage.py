"""Handling messages sent and to be sent by the beacon
"""

import logging
from enum import Enum, unique
from typing import Optional, Union, Mapping
from datetime import datetime
from pprint import pformat

from .utils.modelutils import PyMongoModel
from .team import TeamLevel

from cubeserver_common._version import __version__ as VERSION
from cubeserver_common.config import SHORT_TITLE


MAX_INT_BYTES: int = 256
"""Maximum number of bytes to encode an integer to"""

@unique
class OutputDestination(Enum):
    """IR or RED"""
    IR  = "Infrared"
    RED = "Visible"

@unique
class SentStatus(Enum):
    """Updated by the beacon server"""
    QUEUED       = "Queued"
    SCHEDULED    = "Scheduled"
    TRANSMITTED  = "Transmitted"
    TRANSMITTING = "Transmitting..."
    MISSED       = "Missed"
    FAILED       = "Failed"

@unique
class BeaconMessageEncoding(Enum):
    """Types of encodings for beacon messages
    """
    ASCII      = "ascii"
    UTF8       = "utf-8"
    HEX        = "hex dump"
    INTEGER    = "integer"

    def encode(self, message: Union[str, bytes]) -> bytes:
        """Encodes a message according to the encoding of this enum value

        Returns the parameter unchanged if already bytes.

        Args:
            message (str | bytes): The message to encode
        """
        if type(message) == bytes:
            return message
        if self in [self.UTF8, self.ASCII]:
            return message.encode(self.value)
        elif self == self.HEX:
            return bytes.fromhex(message)
        elif self == self.INTEGER:
            num_bytes = 1
            while num_bytes < MAX_INT_BYTES:
                try:
                    return int(message).to_bytes(num_bytes, 'big')
                except OverflowError:
                    num_bytes += 1
                    continue
            raise OverflowError(
                f"Could not fit specified integer in {MAX_INT_BYTES} bytes."
            )


class BeaconMessage(PyMongoModel):
    """Class for describing and serializing messages
    
    Example message (byte string transmitted by the beacon; "\\r\\n" line terminator):
    ```
    \\x07\\x07\\x07\\x07
    CSMSG/1.0
    Division: Lumen
    Server: CubeServer/0.5.3
    Content-Length: 37
    Checksum: 123

    Hello World!
    This is a test message!

    ```
    
    The protocol used is modeled after HTTP server responses.
    """

    def __init__(
        self,
        instant: datetime = datetime.now(),
        division: TeamLevel = TeamLevel.PSYCHO_KILLER,
        message: Union[bytes, str] = b'',
        line_term: bytes = b'\r\n',
        additional_headers: Mapping[str, str] = {},
        encoding: Optional[BeaconMessageEncoding] = BeaconMessageEncoding.ASCII,
        destination: OutputDestination = OutputDestination.IR,
        intensity: int = 255,
        past: bool = False,
        misfire_grace: int = 30,
        status: Optional[SentStatus] = None,
        prefix: bytes = b''
    ):
        """
        Args:
            message (Union[bytes, str]): The message to send
            encoding (Optional[BeaconMessageEncoding], optional): Must be specified if message is not given as bytes object. Defaults to None.
        """

        if isinstance(message, str) and not isinstance(encoding, BeaconMessageEncoding):
            raise TypeError("For str messages, you MUST specify the encoding properly.")

        super().__init__()

        self.ignore_attribute('message')
        self.ignore_attribute('prefix')
        self.ignore_attribute('suffix')
        self.ignore_attribute('line_term')

        self.send_at = instant
        self.division = division

        self.prefix = prefix
        self.message = message
        self.message_encoding = encoding
        self.line_term = line_term
        self.additional_headers = additional_headers
        self.destination = destination
        self.intensity = intensity
        self.past = past
        self.misfire_grace = misfire_grace

        self.full_message_bytes_stored = self.full_message_bytes

        self.status = status
        if self.status is None:
            self.set_untransmitted()

        #self.register_field('full_message_bytes_stored', self.full_message_bytes)

    def set_untransmitted(self):
        """Automatically determines if this message has been missed"""
        logging.debug("Setting message as untransmitted...")
        self.status = SentStatus.MISSED \
                        if (
                            datetime.now() > self.send_at and
                            (datetime.now()-self.send_at).seconds > self.misfire_grace
                        ) \
                            else SentStatus.QUEUED
        logging.debug(f"+Now: {datetime.now()}; Scheduled for: {self.send_at}")
        logging.debug(f"+-> Status: {self.status}")

    @property
    def message_bytes(self) -> bytes:
        """Returns the message, given as bytes
        """
        if self.message_encoding is None:
            return self.message
        return self.message_encoding.encode(self.message)

    @property
    def headers(self) -> Mapping[bytes, bytes]:
        """Returns all headers
        """
        return {
            b'Division': self.division.value.encode('ascii'),
            b'Server': SHORT_TITLE.encode('ascii') + b'/' + VERSION.encode('ascii'),
            b'Content-Length': str(len(self.message_bytes)).encode('ascii'),
            b'Checksum': str(self.checksum).encode('ascii')
        } | self.additional_headers

    @property
    def headers_bytes(self) -> bytes:
        """Returns headers str as bytes
        """
        return self.line_term.join(
            header + b': ' + value
                for header, value in self.headers.items()
        )

    @property
    def full_message_bytes(self):
        """Returns the message as bytes with headers, etc.
        """
        if self._id:  # If this came from the database, don't regen
            return self.full_message_bytes_stored
        return self.prefix + b'CSMSG/1.1' + self.line_term + \
            self.line_term.join([
                self.headers_bytes,
                self.line_term,
                self.message_bytes,
                self.line_term
            ])
    
    @property
    def full_message_bytes_p(self):
        """Pretty-printed full message"""
        return pformat(self.full_message_bytes)

    @property
    def checksum(self):
        """Calculates a simple checksum"""
        sum = 0
        for i, byte in enumerate(self.message_bytes):
            sum += int(byte) ^ (i*8)
        return sum % 255

    @property
    def str_status(self):
        return self.status.value

    @classmethod
    def find_by_status(cls, status: SentStatus) -> 'BeaconMessage':
        """Returns all messages that have a given status"""
        return cls.find({'status': status.value})
