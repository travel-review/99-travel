from flask import Flask, request, jsonify, redirect, url_for, make_response, flash, render_template, session
from datetime import datetime, timedelta
from functools import wraps
from pymongo import MongoClient
import jwt
import hashlib

app = Flask(__name__)

client = MongoClient('127.0.0.1')
db = client.my_sparta

SECRET_KEY = 'SPARTA'

@app.route('/')
def main():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        collection = db['places']
        places = collection.find({})

        print(user_info)
        print(places)
        return render_template('landing.html', user_info=user_info, places=places)
    except jwt.ExpiredSignatureError:
        print("로그인 시간이 만료되었습니다.")
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        print("로그인 정보가 존재하지 않습니다.")
        return redirect(url_for("login"))

@app.route('/get_db')
def tmp_get_db():
    db.places.insert_one(
        {
            'title': '경복궁',
            'description': '투어 & 박물관이 있는 역사적인 궁전',
            'img_url': 'https://t2.gstatic.com/images?q=tbn:ANd9GcQHjpQ16ZIupZR7ENzIyyXJr4v_pEWzML9EFy1SqyuwTgpfP_YnH8r-Mq96CypOs-Vk0eWHwWEIB-gy1uJSDp9kfw',
            'like': ['rrrr'],
            'continent': 'seoul'
        })
    return render_template('login.html')



@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/api/signin', methods=['POST'])
def api_signin():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

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
                           algorithm='HS256').decode('utf-8')
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        print('아이디비번 x')
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def api_signup():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    db.user.insert_one(
        {'id': id_receive, 'pw': pw_hash})
    return jsonify({'result': 'success'})

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


@app.route('/api/like', methods=['POST'])
def update_like():
    print(11111)
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload["id"])
        user_info = db.users.find_one({"id": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "_id": post_id_receive,
            "id": user_info,
            "type": type_receive
        }
        print(db.places.like.estimated_document_count())
        count = db.places.like.estimated_document_count()
        if action_receive == "like":
            myquery = {"_id": post_id_receive}
            find_place = db.places.find_one(myquery)
            print(find_place)
            # newvalues = {"$set": {"like": "Canyon 123"}}
            return jsonify({"result": "success", 'msg': 'updated', "count": count})
        else:
            return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == '__main__' :
    app.run(debug=True)
