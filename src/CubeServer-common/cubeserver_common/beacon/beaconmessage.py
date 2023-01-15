"""Handling messages sent and to be sent by the beacon
"""

from enum import Enum, unique
from typing import Optional, Union


MAX_INT_BYTES: int = 256
"""Maximum number of bytes to encode an integer to"""

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


class BeaconMessage:
    """Class for describing messages"""

    def __init__(
        self,
        message: Union[bytes, str],
        encoding: Optional[BeaconMessageEncoding] = None
    ):
        """
        Args:
            message (Union[bytes, str]): The message to send
            encoding (Optional[BeaconMessageEncoding], optional): Must be specified if message is not given as bytes object. Defaults to None.
        """

        if isinstance(message, str) and not isinstance(encoding, BeaconMessageEncoding):
            raise TypeError("For str messages, you MUST specify the encoding properly.")

        self.message = message
        self.message_encoding = encoding
    
    @property
    def message_bytes(self):
        """Returns the message, given as bytes
        """
        if self.message_encoding is None:
            return self.message
        return self.message_encoding.encode(self.message)

    def transmit(self):
        """Transmits the message"""
        # TODO: Implement actual transmission!
        print(f"Beacon Tx: {self.message_bytes}")
