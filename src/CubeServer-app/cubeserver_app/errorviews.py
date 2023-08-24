"""Error handlers for this application
Nothing special, just themed error pages.

Handles:
- 404 Not Found
- 400 Bad Request
- 403 Forbidden
- 500 Server Error (Provides reference # for non admin, shows traceback for admin)
- 502 Bad Gateway
"""

from random import randint
import traceback

from flask import render_template, flash
from flask_login import current_user
from loguru import logger


# Error Handlers:
def page_not_found(_):
    """404 Not Found handler"""
    logger.info("Rendering ERROR 404")
    return render_template("errorpages/404.html.jinja2"), 404


def bad_request(_):
    """400 Bad Request handler"""
    logger.info("Rendering ERROR 400")
    return render_template("errorpages/400.html.jinja2"), 400


def forbidden(_):
    """403 Forbidden handler"""
    logger.info("Rendering ERROR 403")
    return render_template("errorpages/403.html.jinja2"), 403


def server_error(e: Exception, message: str = ""):
    """500 Server Error handler"""
    reference = randint(100, 999)  # A reference number with which to grep the logs
    try:
        raise e
    except:  # noqa: E722
        tb = traceback.format_exc()
    finally:
        logger.error(f"ERROR 500: Internal server error: {e}")
        logger.error(f"REFERENCE #{reference}")
        logger.trace(tb)
        logger.info(f"Rendering ERROR 500: {message}")
        flash(f"Your reference number is #{reference}")
        if current_user.is_active:
            return (
                render_template(  # Show traceback if user is logged in:
                    "errorpages/500_traceback.html.jinja2",
                    message=message,
                    traceback=tb
                ),
                500,
            )            
        return (
            render_template(
                "errorpages/500.html.jinja2",
                message=message
            ),
            500,
        )


def bad_gateway(_):
    """502 Bad Gateway handler"""
    logger.info("Rendering ERROR 502")
    return render_template("errorpages/502.html.jinja2"), 502


def register_all(app) -> None:
    """Registers all error handlers to the app"""
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(500, server_error)
    app.register_error_handler(502, bad_gateway)

