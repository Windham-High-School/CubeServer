"""Flask blueprint managing API client (team) configuration stuff"""

from datetime import datetime
from random import randint
from subprocess import call
from os import environ, mkdir, chdir
from shutil import rmtree

from flask import Blueprint, render_template, session, make_response

bp = Blueprint('config', __name__, url_prefix='/setup', template_folder='templates')


with open("/api_cert/sha1_fingerprint.txt", "r") as fingerprint_file:
    sha_fingerprint = fingerprint_file.read()


@bp.route('/')
def index():
    """Renders the main page for this blueprint"""
    return render_template('index.html.jinja2')

@bp.route('/client_config.h')
def header_file():
    """Renders a configuration header file"""
    return render_template(
        'client_config.h.jinja2',
        timestamp=datetime.now().isoformat(),
        team_name=(session['team_name'] if 'team_name' in session else None),
        team_secret=(session['team_secret'] if 'team_secret' in session else None),
        server_fingerprint=sha_fingerprint.strip()
    )

@bp.route('/client_config.py')
def py_file():
    """Renders a configuration python file"""
    return render_template(
        'client_config.py.jinja2',
        timestamp=datetime.now().isoformat(),
        team_name=(session['team_name'] if 'team_name' in session else None),
        team_secret=(session['team_secret'] if 'team_secret' in session else None),
        server_fingerprint=sha_fingerprint.strip()
    )

# TODO: The library packaging could be written much better
@bp.route('/Arduino_lib.zip')
def package_arduino_lib():
    """Packages and downloads the Arduino ZIP library"""
    working_dir = f"/tmp/lib_pack_{str(randint(100,999))}"
    mkdir(working_dir)
    chdir(working_dir)
    output_path = f"{working_dir}/download.zip"
    client_config_path = f"{working_dir}/client_config.h"
    with open(client_config_path, 'w') as fh:
        fh.write(header_file())
    call([
        "/package_lib.sh",
        environ['API_WRAPPER_GIT_URL_ARDUINO'],
        client_config_path,
        output_path
    ])
    # TODO: avoid RAM overhead of loading file?
    output_raw = bytes()
    with open(output_path, 'rb') as fh:
        output_raw = fh.read()
    # Clean up:
    rmtree(working_dir)
    # Formulate response:
    response = make_response(output_raw)
    response.headers.set('Content-Type', 'application/zip')
    response.headers.set(
        'Content-Disposition', 'attachment',
        filename=environ['API_WRAPPER_ZIP_FILENAME_ARDUINO'])
    return response
