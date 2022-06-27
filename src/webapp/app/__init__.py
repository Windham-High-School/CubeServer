"""A web application for software to manage, store, score,
and publish data received from Wifi-equipped microcontrollers for a school contest"""

import os
from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap

from .gensecret import check_secrets
from . import config
from .blueprints import home, admin, team, about

# Configure application:
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder="templates")

# Bootstrap:
Bootstrap(app)

# Configure MongoDB:
app.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] \
    + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] \
        + ':27017/' + os.environ['MONGODB_DATABASE']
mongo = PyMongo(app)

# Load configuration:
app.config['CONSTANTS'] = config
app.config['REGISTRATION_OPEN'] = True  # TODO: Load config from database

# Load SECRET_KEY:
check_secrets() # Double-check that the secret_file is actually there...
with open(config.SECRET_KEY_FILE, "r", encoding=config.SECRET_KEY_FILE_ENCODING) as secret_file:
    app.config['SECRET_KEY'] = secret_file.read()

# Configure blueprints:
app.register_blueprint(home.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(team.bp)
app.register_blueprint(about.bp)

# Error Handlers:
@app.errorhandler(404)
def page_not_found(_):
    """404 handler"""
    return render_template('errorpages/404.html.jinja2'), 404

@app.errorhandler(400)
def bad_request(_):
    """400 handler"""
    return render_template('errorpages/400.html.jinja2'), 400

@app.errorhandler(403)
def forbidden(_):
    """403 handler"""
    return render_template('errorpages/403.html.jinja2'), 403

@app.errorhandler(500)
def server_error(_):
    """500 handler"""
    return render_template('errorpages/500.html.jinja2'), 500

@app.errorhandler(502)
def bad_gateway(_):
    """502 handler"""
    return render_template('errorpages/502.html.jinja2'), 502
