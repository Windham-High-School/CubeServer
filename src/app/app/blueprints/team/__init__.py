from flask import Blueprint, flash, redirect, render_template

from app import app
from app.blueprints.team import registration_form

bp = Blueprint('team', __name__, url_prefix='/team', template_folder='templates')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if app.config['REGISTRATION_OPEN']:
        form = registration_form.RegistrationForm()
        try:
            if form.validate_on_submit():
                return redirect('/success')
        except AttributeError:
            print(dir(form))
        return render_template('register.html.jinja2', form=form)
    else:
        return render_template('regclosed.html.jinja2')

@bp.route('/success')
def success():
    return render_template('success.html.jinja2')

