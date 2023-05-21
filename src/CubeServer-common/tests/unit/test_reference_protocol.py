"""Non-integration unit tests for the reference protocol"""
import pytest
from cubeserver_common.reference_api.protocol import ReferenceRequest, ReferenceResponse, ReferenceSignal, ReferenceCommand, MeasurementType, ProtocolError

class TestReferenceRequest:
    def test_from_bytes(self):
        # <version><id><signal><cmd><param><EOT>
        data = b'\x01\xDE\x05\x01\xAD\x04'
        request = ReferenceRequest.from_bytes(data)
        assert request.id == b'\xDE'
        assert request.signal == ReferenceSignal.ENQ
        assert request.command == ReferenceCommand.MEAS
        assert request.param == b'\xAD'
    
    def test_routing_id(self):
        request = ReferenceRequest(id=b'\x01', signal=ReferenceSignal.ENQ, command=ReferenceCommand.NULL, param=b'\x00')
        assert request.routing_id == 1
    
    def test_from_bytes_invalid_eot(self):
        # EOT is 0x07, should be 0x04
        data = b'\x01\x02\x03\x04\x05\x07'
        with pytest.raises(ProtocolError):
            ReferenceRequest.from_bytes(data)
    
    def test_from_bytes_invalid_version(self):
        # Version is 0xFF, should be 0x01
        data = b'\xFF\xDE\x05\x01\xAD\x04'
        with pytest.raises(ProtocolError):
            ReferenceRequest.from_bytes(data)

    def test_dump(self):
        request = ReferenceRequest(id=b'\xBE', signal=ReferenceSignal.ENQ, command=ReferenceCommand.NOOP, param=b'\xEF')
        expected = b'\x01\xBE\x05\x02\xEF\x04'
        assert request.dump() == expected
