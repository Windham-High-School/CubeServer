from apscheduler.schedulers.background import BackgroundScheduler

from cubeserver_common.models.beaconmessage import BeaconMessage

scheduler = BackgroundScheduler()
scheduler.start()

def load_packets_from_db():
    """Loads the current database into the jobs"""
    scheduled = [job.name for job in scheduler.get_jobs()]
    jobs = BeaconMessage.find() # TODO: Find all future not all historical
    for job in jobs:
        if str(job.id) not in scheduled:
            scheduler.add_job(print, 'date', run_date=job.send_at, args=[job], name=str(job.id))

scheduler.add_job(load_packets_from_db, 'interval', seconds=90, name='database')

