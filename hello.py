from flask import Flask
from flask import request, redirect, make_response, abort
# from flask.ext.script import Manager // depricated
# from flask_script import Manager

app = Flask(__name__)
# manager = Manager(app)


@app.route('/')
def index():
    return '<h1>Hello Roland!</h1>'

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
def get_user(id):
    user = id
    # user = load_user(id)
    if not user:
        print('ERROR')
        abort(500)
    return 'Hello %s!' % id

if __name__ == '__main__':
    app.run(debug=True)
    # manager.run()