from flask import Flask, request, jsonify, make_response, render_template, session
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

'''
app.config['SECRET_KEY']= 'hanghae'
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request/args.get('token')
        if not token:
            return json({'토큰이 없습니다!'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return json({'사용불가능한 토큰입니다.!'})
    return decorated

def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return '이미 로그인 되어있습니다.'
    
@app.route('/puiblic')
def public():
    return 'for public'

@app.route('/auth')
@token_required
def aut():
    return ' 로그인 완료.'

@app.route('/login', methods =['POST'])
def login():
    if request.form['username'] and request.form['password'] =='12345':
        session['logged_in'] = True
        token = jwt.encode({
            'user' : request.form['username'],
            'expiration': datetime.datetime.utcnow() + datetime.timedelta(seconds=120)
        },
         app.config['SECRET_KEY'])
        return jsonify({'token':token.decode('utf-8')})

    else:
        return make_respose('Unable to verify', 403,{'WWW-Authenticate' : 'Basic realm:"Authentication Failed'})
'''


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

@app.route('/detail')
def detail():
    return render_template('detail.html')

if __name__ == '__main__' :
    app.run(debug=True)
