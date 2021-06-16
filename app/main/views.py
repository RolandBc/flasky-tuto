from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from . import main
from .forms import NameForm
# from .. import db
# from ..models import User

@main.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
            oldName = session.get('name')
            if(form.name.data is not None and form.name.data != oldName):
                flash('Looks like you changed your name')
            session['name'] = form.name.data
            form.name.data = ''
            return redirect(url_for('.index'))
    return render_template('index.html', form=form, name=session.get('name'))
    # return '<h1>Hello %s!</h1>' % current_user.group
