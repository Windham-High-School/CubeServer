"""
"""

from apscheduler.schedulers.background import BackgroundScheduler
from cubeserver_common.models.beaconmessage import BeaconMessage

from .beaconserver import BeaconServer, BeaconCommand
from sys import argv


scheduler = BackgroundScheduler()

server = BeaconServer(
    host=argv[1],
    port=int(argv[2]),
    verbose=True
)

def load_packets_from_db():
    """Loads the current database into the jobs"""
    scheduled = [job.name for job in scheduler.get_jobs()]
    jobs = BeaconMessage.find() # TODO: Find all future not all historical (save time & memory)
    for job in jobs:
        if str(job.id) not in scheduled:
            scheduler.add_job(
                server.send_cmd,
                'date', run_date=job.send_at,
                args=[BeaconCommand.from_BeaconMessage(job)],
                name=str(job.id)
            )

load_packets_from_db()

scheduler.add_job(load_packets_from_db, 'interval', seconds=90, name='db_updater')

scheduler.start()
server.run()
