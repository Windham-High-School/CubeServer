"""Describes the protocol to be used when contacting a reference station

Request:
    <Version Byte> <id> <signal> <cmd> <param> <EOT>
Response:
    <Version Byte> <signal> <length> <struct_type> <response bytes> <EOT>

"""

import dataclasses
import enum
import socket
import logging
import struct


from cubeserver_common.models.datapoint import DataClass, DataPoint


REFERENCECOM_VERSION: bytes = b'\x01'
"""A single-byte version number on both the reference and client devices"""

class ProtocolError(Exception):
    """Raised when the protocol is violated"""
    pass

@enum.unique
class MeasurementType(enum.Enum):
    TEMP      = b'\x01'
    PRES      = b'\x02'

    _dc_map = {
            DataClass.TEMPERATURE: TEMP,
            DataClass.PRESSURE: PRES
        }

    @classmethod
    def from_DataClass(cls, od: DataClass):
        """Converts from DataClass to MeasurementType"""
        return cls._dc_map[od]
    
    def to_DataClass(self):
        """Returns the equivalent DataClass"""
        return {v: k for k, v in self._dc_map.items()}[self]

class ReferenceSignal(enum.Enum):
    NUL  = b'\x00'
    ACK  = b'\x06'
    NAK  = b'\x15'
    EOT  = b'\x04'
    ENQ  = b'\x05'

class ReferenceCommand(enum.Enum):
    NULL = b'\x00'
    MEAS = b'\x01'
    NOOP = b'\x02'
    STAT = b'\x03'

@dataclasses.dataclass
class ReferenceRequest:
    """A 5-byte command to be sent to a reference station
    <version><id><signal><cmd><param><EOT>
    """
    id:      bytes            = bytes(1)
    signal:  ReferenceSignal  = ReferenceSignal.NUL
    command: ReferenceCommand = ReferenceCommand.NULL
    param:   bytes            = bytes(1)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'ReferenceRequest':
        """Generates request object from byte string"""
        if data[-1] != ReferenceSignal.EOT.value[0]:
            raise ProtocolError("Invalid request - missing EOT")
        if data[0] != REFERENCECOM_VERSION[0]:
            raise ProtocolError("Invalid request - wrong version")
        return cls(
            id      = data[1:2],
            signal  = ReferenceSignal(data[2:3]),
            command = ReferenceCommand(data[3:4]),
            param   = data[4:-1]
        )
    
    @property
    def routing_id(self):
        """Returns the routing ID for the request"""
        return self.id[0]

    def dump(self) -> bytes:
        """Dumps the request to a byte string"""
        dumped_bytes = b''.join([
            REFERENCECOM_VERSION,
            self.id,
            self.signal.value,
            self.command.value,
            self.param,
            ReferenceSignal.EOT.value
        ])
        if len(dumped_bytes) != 6:
            logging.error(f"Malformed request: {dumped_bytes}")
            raise ProtocolError("Invalid request - wrong length")
        return dumped_bytes

@dataclasses.dataclass
class ReferenceResponse:
    """A response from the reference station
    <version><signal><length><struct_type><response><EOT>
    """
    signal:      ReferenceSignal = ReferenceSignal.NUL
    length:      bytes           = bytes(1)
    struct_type: bytes           = bytes(1)
    response:    bytes           = bytes(0)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'ReferenceResponse':
        """Generates response object from byte string"""
        if data[-1] != ReferenceSignal.EOT.value[0]:
            raise ProtocolError("Invalid response - missing EOT")
        if data[0] != REFERENCECOM_VERSION[0]:
            raise ProtocolError("Invalid response - wrong version")
        return cls(
            signal      = ReferenceSignal(data[1:2]),
            length      = data[2:3],
            struct_type = data[3:4],
            response    = data[4:-1]
        )

    def dump(self) -> bytes:
        """Dumps the response to a byte string"""
        return b''.join([
            REFERENCECOM_VERSION,
            self.signal.value,
            self.length,
            self.struct_type,
            self.response,
            ReferenceSignal.EOT
        ])
    
    def get_value(self) -> bytes | int | bool | float:
        """Unpacks the response value and returns it"""
        return struct.unpack(
            self.struct_type,
            self.response
        )

    def set_value(self, format: str | bytes, value: bytes | int | bool | float) -> None:
        """Packs the given value and encodes it into this response object"""
        self.response = struct.pack(
            self.struct_type,
            value
        )
        self.struct_type = format

    @classmethod
    def from_socket(self, socket: socket.socket) -> 'ReferenceResponse':
        """Reads a response from the given socket"""
        # <version><signal><length><struct_type><response><EOT>
        version = socket.recv(1)
        if version != REFERENCECOM_VERSION:
            socket.sendall(ReferenceSignal.NAK.value)
            return
        signal = socket.recv(1)
        if signal != ReferenceSignal.ACK.value:
            socket.sendall(ReferenceSignal.NAK.value)
            return
        length = int.from_bytes(self.rx_bytes(1), 'big')
        struct_type = socket.recv(1)
        response = socket.recv(length)
        eot = socket.recv(1)
        if eot != ReferenceSignal.EOT.value:
            socket.sendall(ReferenceSignal.NAK.value)
            return
        
        # Package response
        return ReferenceResponse(
            signal=signal,
            length=length,
            struct_type=struct_type,
            response=response
        )