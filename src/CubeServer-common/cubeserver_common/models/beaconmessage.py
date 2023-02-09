"""Handling messages sent and to be sent by the beacon
"""

from enum import Enum, unique
from typing import Optional, Union, Mapping
from datetime import datetime

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
class BeaconMessageEncoding(Enum):
    """Types of encodings for beacon messages
    """
    UTF8       = "utf-8"
    ASCII      = "ascii"
    HEX        = "hex dump"
    INTEGER    = "integer"

    def encode(self, message: str) -> bytes:
        """Encodes a message according to the encoding of this enum value
        Args:
            message (str): The message to encode
        """
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
    ================INCOMING=MESSAGE================
    CSMSG/1.0
    Division: Lumen
    Server: CubeServer/0.5.3
    Content-Length: 37
    Checksum: 123

    Hello World!
    This is a test message!

    ===================END===MESSAGE================
    ```
    
    The protocol used is modeled after HTTP server responses.
    """

    def __init__(
        self,
        instant: datetime = datetime.now(),
        division: TeamLevel = TeamLevel.PSYCHO_KILLER,
        message: Union[bytes, str] = b'',
        prefix: bytes = b'================INCOMING=MESSAGE================',
        suffix: bytes = b'===================END===MESSAGE================',
        line_term: bytes = b'\r\n',
        additional_headers: Mapping[str, str] = {},
        encoding: Optional[BeaconMessageEncoding] = None,
        destination: OutputDestination = OutputDestination.IR,
        intensity: int = 255
    ):
        """
        Args:
            message (Union[bytes, str]): The message to send
            encoding (Optional[BeaconMessageEncoding], optional): Must be specified if message is not given as bytes object. Defaults to None.
        """

        if isinstance(message, str) and not isinstance(encoding, BeaconMessageEncoding):
            raise TypeError("For str messages, you MUST specify the encoding properly.")

        super().__init__()

        self.send_at = instant
        self.division = division
        self.prefix = prefix
        self.suffix = suffix
        self.message = message
        self.message_encoding = encoding
        self.line_term = line_term
        self.additional_headers = additional_headers
        self.destination = destination
        self.intensity = intensity
    
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
            b'Division': self.division.value,
            b'Server': SHORT_TITLE.encode('ascii') + b'/' + VERSION.encode('ascii'),
            b'Content-Length': str(len(self.message_bytes)).encode('ascii'),
            b'Checksum': str(self.checksum).encode('ascii')
        } + self.additional_headers

    @property
    def headers_bytes(self) -> bytes:
        """Returns headers str as bytes
        """
        return self.line_term.join(
            f"{header}: {value}"
                for header, value in self.headers.values()
        )

    @property
    def full_message_bytes(self):
        """Returns the message as bytes with headers, etc.
        """
        return self.line_term.join([
            self.prefix,
            b'CSMSG/1.0',
            self.headers,
            self.line_term,
            self.message_bytes,
            self.line_term,
            self.suffix
        ])

    @property
    def checksum(self):
        """Calculates a simple checksum"""
        sum = 0
        for i, byte in enumerate(self.message_bytes):
            sum += int(byte) ^ (i*8)
        return sum % 255
