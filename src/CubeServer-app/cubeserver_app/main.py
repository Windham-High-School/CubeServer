"""Allows running/serving the web application."""

from flask import redirect, request
from flask_login import login_url

from cubeserver_app import app, login_manager
from cubeserver_app.blueprints import home, admin, team, about, client_setup
from cubeserver_common.models.user import User


# Configure blueprints:
app.register_blueprint(home.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(team.bp)
app.register_blueprint(about.bp)
app.register_blueprint(client_setup.bp)


# Configure flask-login:
login_manager.user_loader(User.find_by_id)
# Handle login redirects:
@login_manager.unauthorized_handler
def login_unauthorized():
    """Redirects the user to a login screen"""
    return redirect(login_url('home.login', next_url=request.url))
