"""Defines & registers the error handlers for this application"""

import logging
from flask import render_template

from cubeserver_app import app

# Error Handlers:
@app.errorhandler(404)
def page_not_found(_):
    """404 handler"""
    logging.info("Rendering ERROR 404")
    return render_template('errorpages/404.html.jinja2'), 404


@app.errorhandler(400)
def bad_request(_):
    """400 handler"""
    logging.info("Rendering ERROR 400")
    return render_template('errorpages/400.html.jinja2'), 400

@app.errorhandler(403)
def forbidden(_):
    """403 handler"""
    logging.info("Rendering ERROR 403")
    return render_template('errorpages/403.html.jinja2'), 403


@app.errorhandler(500)
def server_error(_, message=""):
    """500 handler"""
    logging.info(f"Rendering ERROR 500: {message}")
    return render_template('errorpages/500.html.jinja2', message=message), 500


@app.errorhandler(502)
def bad_gateway(_):
    """502 handler"""
    logging.info("Rendering ERROR 502")
    return render_template('errorpages/502.html.jinja2'), 502
