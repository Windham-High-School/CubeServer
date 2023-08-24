"""Flask blueprint managing API client (team) configuration stuff"""

from typing import Optional
import logging
from datetime import datetime
from subprocess import call
from os import mkdir, chdir
from shutil import rmtree
from random import randint, random

from cubeserver_common.config import EnvConfig
from cubeserver_app import settings

from flask import Blueprint, render_template, session, make_response

bp = Blueprint("config", __name__, url_prefix="/setup", template_folder="templates")



pem_cert: Optional[str]
try:
    with open("/etc/ssl/api_cert/server.pem", "r", encoding=EnvConfig.CS_STR_ENCODING) as fh:
        pem_cert = fh.read()
    logging.debug("Loaded server API certificate")
except:
    pem_cert = None


@bp.route("/")
def index():
    """Renders the main page for this blueprint"""
    return render_template("index.html.jinja2", rand=random())


@bp.route("/client_config.h")
def header_file():
    """Renders a configuration header file"""
    team_name = session["team_name"] if "team_name" in session else None
    team_secret = session["team_secret"] if "team_secret" in session else None
    logging.info(f"Rendering client_config.h for {team_name}")
    return render_template(
        "client_config.h.jinja2",
        timestamp=datetime.now().isoformat(),
        team_name=team_name,
        team_secret=team_secret,
        ssid=EnvConfig.CS_AP_SSID,
        common_name=EnvConfig.CS_API_HOST,
        base_url="https://" + EnvConfig.CS_API_ADDR,
        port=EnvConfig.CS_API_PORT,
    )


@bp.route("/client_config.py")
def py_file():
    """Renders a configuration python file"""
    team_name = session["team_name"] if "team_name" in session else None
    team_secret = session["team_secret"] if "team_secret" in session else None
    logging.info(f"Rendering client_config.py for {team_name}")
    return render_template(
        "client_config.py.jinja2",
        timestamp=datetime.now().isoformat(),
        team_name=team_name,
        team_secret=team_secret,
        ssid=EnvConfig.CS_AP_SSID,
        common_name=EnvConfig.CS_API_HOST,
        base_url="https://" + EnvConfig.CS_API_ADDR,
        port=EnvConfig.CS_API_PORT,
        server_cert=pem_cert.replace("\n", "\\n") if pem_cert else None,
    )


# TODO: The library packaging could be written much better
@bp.route("/Arduino_lib.zip")
def package_arduino_lib():
    """Packages and downloads the Arduino ZIP library"""
    logging.info(f"Packing Arduino ZIP")
    working_dir = EnvConfig.CS_TEMP_PATH + f"/lib_pack_{str(randint(100,999))}"
    mkdir(working_dir)
    chdir(working_dir)
    output_path = f"{working_dir}/download.zip"
    client_config_path = f"{working_dir}/client_config.h"
    with open(client_config_path, "w") as fh:
        fh.write(header_file())
    call(
        [
            "/code/package_lib.sh",
            settings.API_WRAPPER_GIT_URL_ARDUINO,
            client_config_path,
            output_path,
        ]
    )
    # TODO: avoid RAM overhead of loading file into memory?
    output_raw = bytes()
    with open(output_path, "rb") as fh:
        output_raw = fh.read()
    # Clean up:
    rmtree(working_dir)
    # Formulate response:
    response = make_response(output_raw)
    response.headers.set("Content-Type", "application/zip")
    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename=settings.API_WRAPPER_ZIP_FILENAME_ARDUINO,
    )
    return response


@bp.route("/CircuitPython_lib.zip")
def package_circuitpython_lib():
    """Packages and downloads the CircuitPython ZIP library"""
    logging.info(f"Packing CircuitPython ZIP")
    working_dir = EnvConfig.CS_TEMP_PATH + f"/lib_pack_{str(randint(100,999))}"
    mkdir(working_dir)
    chdir(working_dir)
    output_path = f"{working_dir}/download.zip"
    client_config_path = f"{working_dir}/client_config.py"
    with open(client_config_path, "w") as fh:
        fh.write(py_file())
    call(
        [
            "/code/package_lib.sh",
            settings.API_WRAPPER_GIT_URL_CIRCUITPYTHON,
            client_config_path,
            output_path,
        ]
    )
    # TODO: avoid RAM overhead of loading file into memory?
    output_raw = bytes()
    with open(output_path, "rb") as fh:
        output_raw = fh.read()
    # Clean up:
    rmtree(working_dir)
    # Formulate response:
    response = make_response(output_raw)
    response.headers.set("Content-Type", "application/zip")
    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename=settings.API_WRAPPER_ZIP_FILENAME_CIRCUITPYTHON,
    )
    return response


# This is more important than you think. Don't remove it. :)
@bp.route("/api_cert.pem")
def api_cert():
    """Downloads the pem file for the cert of the api
    for server verification purposes"""
    logging.info("Downloading api_cert.pem")
    response = make_response(pem_cert)
    response.headers.set("Content-Type", "application/x-pem-file")
    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename=settings.API_WRAPPER_PEM_FILENAME,
    )
    return response