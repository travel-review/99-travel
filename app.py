from flask import Flask, request, jsonify, redirect, url_for, make_response, render_template, session
from datetime import datetime, timedelta
from functools import wraps
from datetime import datetime
from pymongo import MongoClient
import jwt

app = Flask(__name__)

client = MongoClient('127.0.0.1')
db = client.upload

SECRET_KEY = 'SPARTA'

@app.route('/')
def login():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        print(user_info)
        return render_template('login.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/api/signin', methods=['POST'])
def api_signin():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = pw_receive

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
        }
        token = jwt.encode(payload, SECRET_KEY,
                           algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def api_signup():
    id_receive = request.form['id_give']
    pw_receive = request.form ['pw_give']

    pw_hash = pw_receive

    db.user.insert_one(
        {'id': id_receive, 'pw': pw_hash})

    return jsonify({'result': 'success'})

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/upload',methods=['POST'])
def write_review():
    title_receive = request.form['title_give']
    author_receive = request.form['author_give']
    review_receive = request.form['Review_give']

    file = request.files['file_give']

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    extension = file.filename.split('.')[-1]
    filename = f'file-{mytime}'
    save_to = f'static/{filename}.{extension}'

    file.save(save_to)

    doc = {
        'title': title_receive,
        'author': author_receive,
        'review': review_receive,
        'file': f'{filename}.{extension}'
    }

    db.review.insert_one(doc)

    return jsonify({'msg': '저장완료!'})

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

@app.route('/detail')
def detail():
    return render_template('detail.html')

if __name__ == '__main__' :
    app.run(debug=True)
