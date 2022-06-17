from flask import Flask

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder="templates")

from .blueprints import home, admin
app.register_blueprint(home.bp)
app.register_blueprint(admin.bp)

from app import views