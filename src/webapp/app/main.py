"""Allows running/serving the web application."""

from app import app
from .blueprints import home, admin, team, about


# Configure blueprints:
app.register_blueprint(home.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(team.bp)
app.register_blueprint(about.bp)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=8080)
