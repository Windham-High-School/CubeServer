"""Allows running/serving the web application."""

from flask import render_template

from app import app
from .blueprints import home, admin, team, about


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


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=8080)
