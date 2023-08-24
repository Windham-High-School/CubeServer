"""The blueprints that make up each separate piece of the web app"""

from . import home
from . import about
from . import login
#from . import admin
from . import client_setup
from . import team

#__all__ = ['register_all', 'about', 'admin', 'client_setup', 'login', 'team']

def register_all(app) -> None:
    """Registers all blueprints to the app
    These are loaded in order of priority, so that an error in the init stage
    would disrupt as little functionality as possible
    """
    # Basic user interface pages
    app.register_blueprint(home.bp)
    app.register_blueprint(about.bp)
    app.register_blueprint(login.bp)


    # Team pages
    app.register_blueprint(client_setup.bp)
    app.register_blueprint(team.bp)
