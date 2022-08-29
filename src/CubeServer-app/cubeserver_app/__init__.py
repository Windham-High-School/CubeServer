"""A web application for software to manage, store, score,
and publish data received from Wifi-equipped microcontrollers for a school contest"""

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from cubeserver_common import config
from cubeserver_common.gensecret import check_secrets
from cubeserver_common import configure_db

from ._version import *

# Configure application:
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder="templates")

# Bootstrap:
Bootstrap(app)

# Configure MongoDB:
configure_db(app)

# Import models ONLY AFTER the db is configured:
from cubeserver_common.models.config.conf import Conf

# Load configuration:
app.config['CONSTANTS'] = config
db_config = Conf.retrieve_instance()
app.config['CONFIGURABLE'] = db_config
#app.config['REGISTRATION_OPEN'] = db_config.registration_open

# Load SECRET_KEY:
# Double-check that the secret_file is actually there...
app.config['SECRET_KEY'] = check_secrets()

# Login Manager:
login_manager = LoginManager()
login_manager.init_app(app)
