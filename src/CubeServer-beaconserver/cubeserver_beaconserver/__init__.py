import logging
from cubeserver_common import configure_db, init_logging

init_logging()

logging.debug("Initializing db connection")
configure_db()
