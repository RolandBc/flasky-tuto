import os
from datetime import datetime
from flask import Flask, render_template
from flask import request, redirect, make_response, abort, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

# --- Forms ---
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required



# from flask.ext.script import Manager // depricated
# from flask_script import Manager

from datetime import datetime

from data import User
current_user = User()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

moment = Moment(app)
bootstrap = Bootstrap(app)
# manager = Manager(app)


# --- SQL DB ---

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

from werkzeug.security import generate_password_hash, check_password_hash

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Role %r>' % self.name
    
    users = db.relationship('User', backref='role')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)

    def __repr__(self) -> str:
        return '<User %r>' % self.username

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))




# --- Form ---

class NameForm(Form):
    name = StringField('What is your name ?', validators=[Required()])
    submit = SubmitField('Submit')


# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    getName = User.query.filter_by(username='susan').first()
    print('$$$$$$$$$$$$$$$$$$')
    print(getName)
    print(getName.username)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    # return render_template('index.html', form=form, name=session.get('name'), known = session.get('known', False))
    return '<h1>Hello %s!</h1>' % getName.username

@app.route('/oldForm', methods=['GET', 'POST'])
def oldForm():
    form = NameForm()
    if form.validate_on_submit():
        oldName = session.get('name')
        if(form.name.data is not None and form.name.data != oldName):
            flash('Looks like you changed your name')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))
    # return '<h1>Hello %s!</h1>' % current_user.group

@app.route('/time')
def time():
    return render_template('time.html', current_time = datetime.utcnow())

@app.route('/redirect')
def test():
    return redirect('http://google.com')

@app.route('/cookie')
def cookie():
    response = make_response('<h1>This docuement carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response

@app.route('/browser')
def browser():
    user_agent = request.headers.get('User-Agent')
    return '<h1>Hello Roland! Your browsers are %s</h1>' % user_agent


@app.route('/user/<id>')
def user(id):
    user = id
    # user = load_user(id)
    if not user:
        print('ERROR')
        abort(500)
    # return 'Hello %s!' % id
    return render_template('user.html', name=id)

@app.errorhandler(404)
def page_not_found(e):
 return render_template('404.html'), 404




if __name__ == '__main__':
    app.run(debug=True)
    # manager.run()