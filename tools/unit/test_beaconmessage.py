"""Tests for the BeaconMessage model."""

from datetime import datetime, timedelta
from cubeserver_common.models.beaconmessage import BeaconMessage, OutputDestination, SentStatus, BeaconMessageEncoding

from cubeserver_common.models.utils.modelutils import PyMongoModel
from cubeserver_common.models.team import TeamLevel
from mongomock import MongoClient as MockMongoClient

def test_message_bytes():
    # Test message as bytes
    message_bytes = b'Hello, world!'
    message = BeaconMessage(message=message_bytes)
    assert message.message_bytes == message_bytes

    # Test message as str with ASCII encoding
    message_str = 'Hello, world!'
    message = BeaconMessage(message=message_str, encoding=BeaconMessageEncoding.ASCII)
    assert message.message_bytes == message_str.encode('ascii')

    # Test message as str with UTF-8 encoding
    message_str = 'Hello, world!'
    message = BeaconMessage(message=message_str, encoding=BeaconMessageEncoding.UTF8)
    assert message.message_bytes == message_str.encode('utf-8')

def test_headers():
    message = BeaconMessage(
        message=b'Hello, world!',
        division=TeamLevel.VARSITY,
        destination=OutputDestination.IR
    )
    headers = message.headers
    assert headers[b'Division'] == b'Lumen'
    assert headers[b'Server'].startswith(b'CubeServer/')
    assert headers[b'Content-Length'] == b'13'
    assert headers[b'Checksum'] == b'124'

def test_full_message_bytes():
    message = BeaconMessage(
        message=b'Hello, world!',
        division=TeamLevel.PSYCHO_KILLER,
        destination=OutputDestination.IR
    )
    full_message_bytes = message.full_message_bytes
    assert message.line_term in full_message_bytes
    assert b'Hello, world!' in full_message_bytes
    assert b'Talking Head' in full_message_bytes
    assert b'CSMSG/1.1' in full_message_bytes  # Please take caution in bumping protocol versions

def test_checksum():
    message = BeaconMessage(message=b'Hello, world!')
    assert message.checksum == 124

def test_set_untransmitted():
    # Test message that should be sent
    message = BeaconMessage(
        message=b'Hello, world!',
        instant=datetime.now() - timedelta(seconds=60),
        misfire_grace=30
    )
    message.set_untransmitted()
    assert message.status == SentStatus.MISSED

    # Test message that should be queued
    message = BeaconMessage(
        message=b'Hello, world!',
        instant=datetime.now() + timedelta(seconds=60),
        misfire_grace=30
    )
    message.set_untransmitted()
    assert message.status == SentStatus.QUEUED

    message = BeaconMessage(
        message=b'Hello, world!',
        instant=datetime.now() + timedelta(seconds=60),
        misfire_grace=30
    )
    message.set_untransmitted()
    assert message.status == SentStatus.QUEUED

# Not yet working (in progress):
# def test_find_by_status():
#     client = MockMongoClient()
#     PyMongoModel.update_mongo_client(client)

#     message1 = BeaconMessage(message=b'Hello, world!', status=SentStatus.QUEUED)
#     message2 = BeaconMessage(message=b'Hello, world!', status=SentStatus.TRANSMITTED)
#     message3 = BeaconMessage(message=b'Hello, world!', status=SentStatus.MISSED)

#     message1.save()
#     message2.save()
#     message3.save()

#     queued_messages = BeaconMessage.find_by_status(SentStatus.QUEUED)
#     assert message1 in queued_messages
#     assert message2 not in queued_messages
#     assert message3 not in queued_messages

#     sent_messages = BeaconMessage.find_by_status(SentStatus.SENT)
#     assert message1 not in sent_messages
#     assert message2 in sent_messages
#     assert message3 not in sent_messages

#     missed_messages = BeaconMessage.find_by_status(SentStatus.MISSED)
#     assert message1 not in missed_messages
#     assert message2 not in missed_messages
#     assert message3 in missed_messages

# def test_find_since():
#     client = MockMongoClient()
#     PyMongoModel.update_mongo_client(client)

#     message1 = BeaconMessage(message=b'Hello, world!', instant=datetime.now() - timedelta(seconds=60))
#     message2 = BeaconMessage(message=b'Hello, world!', instant=datetime.now() - timedelta(seconds=30))
#     message3 = BeaconMessage(message=b'Hello, world!', instant=datetime.now() + timedelta(seconds=30))

#     message1.save()
#     message2.save()
#     message3.save()

#     messages_since_45_seconds_ago = BeaconMessage.find_since(timedelta(seconds=45))
#     assert message1 in messages_since_45_seconds_ago
#     assert message2 in messages_since_45_seconds_ago
#     assert message3 not in messages_since_45_seconds_ago

#     messages_since_15_seconds_ago = BeaconMessage.find_since(timedelta(seconds=15))
#     assert message1 not in messages_since_15_seconds_ago
#     assert message2 in messages_since_15_seconds_ago
#     assert message3 not in messages_since_15_seconds_ago
#     assert False
