from flask import render_template
from app import app

@app.errorhandler(404)
def page_not_found(error):
   return render_template('errorpages/404.html.jinja2'), 404

@app.errorhandler(400)
def bad_request(error):
   return render_template('errorpages/400.html.jinja2'), 400

@app.errorhandler(403)
def forbidden(error):
   return render_template('errorpages/403.html.jinja2'), 403

@app.errorhandler(500)
def server_error(error):
   return render_template('errorpages/500.html.jinja2'), 500

@app.errorhandler(502)
def bad_gateway(error):
   return render_template('errorpages/502.html.jinja2'), 502