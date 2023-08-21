"""Defines & registers the error handlers for this application"""

from random import randint

from flask import render_template, flash
from loguru import logger

from cubeserver_app import app

# Error Handlers:
@app.errorhandler(404)
def page_not_found(_):
    """404 handler"""
    logger.info("Rendering ERROR 404")
    return render_template('errorpages/404.html.jinja2'), 404


@app.errorhandler(400)
def bad_request(_):
    """400 handler"""
    logger.info("Rendering ERROR 400")
    return render_template('errorpages/400.html.jinja2'), 400

@app.errorhandler(403)
def forbidden(_):
    """403 handler"""
    logger.info("Rendering ERROR 403")
    return render_template('errorpages/403.html.jinja2'), 403


@app.errorhandler(500)
def server_error(e, message=""):
    """500 handler"""
    reference = randint(100, 999)  # A reference number with which to grep the logs
    logger.error(f"ERROR 500: Internal server error: {e}")
    logger.error(f"REFERENCE #{reference}")
    logger.info(f"Rendering ERROR 500: {message}")
    flash(f"Your reference number is #{reference}")
    return render_template('errorpages/500.html.jinja2', message=message), 500


@app.errorhandler(502)
def bad_gateway(_):
    """502 handler"""
    logger.info("Rendering ERROR 502")
    return render_template('errorpages/502.html.jinja2'), 502
