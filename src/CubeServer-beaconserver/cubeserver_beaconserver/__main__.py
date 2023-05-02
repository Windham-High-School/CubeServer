""" This is executed within the CubeServer-beaconserver container
"""

import logging
import atexit
import threading
from typing import List
from sys import argv, exit

from apscheduler.schedulers.background import BackgroundScheduler
from cubeserver_common.models.beaconmessage import BeaconMessage, SentStatus
from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.team import Team
from cubeserver_common.config import LOGGING_LEVEL

from .beacon.beaconserver import BeaconServer, BeaconCommand

from .reference.referencedispatcher import ReferenceDispatcherServer
from .reference.referenceserver import ReferenceServer


def mark_unscheduled():
    """Marks all messages as not yet scheduled"""
    logging.debug("Marking all messages as not yet scheduled")
    for msg in (
          BeaconMessage.find_by_status(SentStatus.SCHEDULED)
        + BeaconMessage.find_by_status(SentStatus.TRANSMITTING)
    ):
        msg.set_untransmitted()
        msg.save()

mark_unscheduled()


logging.debug("Initializing APScheduler")
scheduler = BackgroundScheduler()
# Make APScheduler a little quieter:
logging.getLogger('apscheduler.executors.default').setLevel(LOGGING_LEVEL + 10)

server = BeaconServer(
    host=argv[1],
    port=int(argv[2])
)

def transmit_message(message: BeaconMessage) -> bool:
    if message.status == SentStatus.TRANSMITTED:
        logging.warning("Tried to transmit already-sent message.")
        return False
    logging.info("Transmitting message...")
    message.status = SentStatus.TRANSMITTING
    message.save()
    if server.send_cmd(BeaconCommand.from_BeaconMessage(message)):
        message.status = SentStatus.TRANSMITTED
        message.save()
        logging.info("Transmission succeeded.")
        return True
    logging.warning("Transmission failed.")
    message.status = SentStatus.FAILED
    message.save()
    return False

@atexit.register
def shutdown_hook():
    """Runs before closing..."""
    logging.info("Preparing for exit...")
    logging.debug("Shutting down scheduler")
    scheduler.shutdown()
    mark_unscheduled()
    logging.info("Ready for exit.")


quit_signal = threading.Event()

def load_packets_from_db():
    """Loads the current database into the jobs"""
    if server.is_stale and server.running:
        logging.warning("Connection is stale!")
        try:
            mark_unscheduled()
        finally:
            quit_signal.set()
    logging.debug("Polling scheduled jobs...")
    scheduled = [job.name for job in scheduler.get_jobs()]
    logging.debug(scheduled)
    jobs: List[BeaconMessage] = BeaconMessage.find_by_status(SentStatus.QUEUED)
    logging.debug(jobs)
    for job in jobs:
        if str(job.id) not in scheduled:
            logging.debug(f"Adding job: {job.full_message_bytes}")
            scheduler.add_job(
                transmit_message,
                'date', run_date=job.send_at,
                args=[job],
                name=str(job.id),
                misfire_grace_time=job.misfire_grace
            )
            job.status = SentStatus.SCHEDULED
            job.save()

load_packets_from_db()

# Poll to get new packets
scheduler.add_job(
    load_packets_from_db,
    'interval',
    seconds=Conf.retrieve_instance().beacon_polling_period,
    name='db_updater'
)

logging.debug("Starting scheduler")
scheduler.start()

# Start the beacon server:
def beacon_server_target():
    """Runs the server"""
    logging.debug("Starting server")
    try:
        server.run()
    except Exception as e:
        logging.exception(e)
    finally:
        quit_signal.set()

beacon_server_thread = threading.Thread(target=beacon_server_target, daemon=True)
beacon_server_thread.start()

# Generate the reference server dispatching table:
reference_teams = Team.find_references()
logging.debug(f"Reference teams: {reference_teams}")

reference_routing_table = {}
for team in reference_teams:
    logging.debug(f"Creating reference server for {team.name}")
    reference_routing_table[team.reference_id] = ReferenceServer(team)

# Start the reference servers:
for reference_id, reference_server in reference_routing_table.items():
    logging.debug(f"Starting reference server for #{reference_id}")
    reference_server_thread = threading.Thread(target=reference_server.run, daemon=True)
    reference_server_thread.start()

# Start the reference dispatcher:
def reference_dispatcher_target():
    """Runs the dispatcher"""
    logging.debug("Starting dispatcher")
    try:
        ReferenceDispatcherServer(reference_routing_table).run()
    except Exception as e:
        logging.exception(e)
    finally:
        quit_signal.set()

reference_dispatcher_thread = threading.Thread(target=reference_dispatcher_target, daemon=True)
reference_dispatcher_thread.start()

quit_signal.wait()
logging.info("Preparing for exit...")
shutdown_hook()
exit()
