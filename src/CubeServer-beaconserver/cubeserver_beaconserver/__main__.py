""" This is executed within the CubeServer-beaconserver container
"""

import logging
from typing import List
from sys import argv

from apscheduler.schedulers.background import BackgroundScheduler
from cubeserver_common.models.beaconmessage import BeaconMessage
from cubeserver_common.models.config.conf import Conf

from .beaconserver import BeaconServer, BeaconCommand

logging.debug("Initializing APScheduler")
scheduler = BackgroundScheduler()

server = BeaconServer(
    host=argv[1],
    port=int(argv[2])
)

def load_packets_from_db():
    """Loads the current database into the jobs"""
    logging.debug("Polling scheduled jobs...")
    scheduled = [job.name for job in scheduler.get_jobs()]
    logging.debug(scheduled)
    jobs: List[BeaconMessage] = BeaconMessage.find()
    logging.debug(jobs)
    for job in jobs:
        logging.debug("Potential job-")
        logging.debug(job.full_message_bytes)
        if str(job.id) not in scheduled:
            logging.debug("Adding job")
            scheduler.add_job(
                server.send_cmd,
                'date', run_date=job.send_at,
                args=[BeaconCommand.from_BeaconMessage(job)],
                name=str(job.id),
                misfire_grace_time=job.misfire_grace
            )

load_packets_from_db()

logging.debug("Starting scheduler")
scheduler.start()

# Poll to get new packets
scheduler.add_job(
    load_packets_from_db,
    'interval',
    seconds=Conf.retrieve_instance().beacon_polling_period,
    name='db_updater'
)

logging.info("Starting beacon server")
server.run()
