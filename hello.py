from datetime import datetime
from flask import Flask, render_template
from flask import request, redirect, make_response, abort, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

# --- Forms ---
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

# --- DynamoDB ---
import boto3

client = boto3.client('dynamodb', aws_access_key_id='fakeMyKeyId', aws_secret_access_key='fakeSecretAccessKey', region_name='eu-central-1', endpoint_url='http://localhost:8000')
music = client.batch_get_item(
    RequestItems={
        'Music': {
            'Keys': [
                {
                    'Artist': {
                        'S': 'No One You Know',
                    },
                    'SongTitle': {
                        'S': 'Call Me Today',
                    },
                }
            ],
            'ProjectionExpression': 'AlbumTitle',
        },
    },
)

user = client.batch_get_item(
    RequestItems={
        'TrainUser': {
            'Keys': [
                {
                    'id': {
                        'N': '3103',
                    },
                    'username': {
                        'S': 'roland@datascientest.com',
                    },
                }
            ],
            'ProjectionExpression': 'username',
        },
    },
)

tables = client.list_tables()
print('--------- -- - -CLIENT DB')
print('user')

print(user)
print('music')
print(music)
print(tables)

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

class NameForm(Form):
    name = StringField('What is your name ?', validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
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