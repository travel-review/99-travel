from flask import Flask, request, jsonify, redirect, url_for, make_response, flash, render_template, session
import os
from datetime import datetime, timedelta
from functools import wraps
from bson.objectid import ObjectId
from pymongo import MongoClient
import jwt
import hashlib

import utils

app = Flask(__name__)

client = MongoClient('127.0.0.1')
db = client.my_sparta

_FAKE_PLACE_NUM = 5
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
    utils.insert_fake_places(_FAKE_PLACE_NUM)
    # db.places.insert_one(
    #     {
    #         'title': '경복궁',
    #         'description': '투어 & 박물관이 있는 역사적인 궁전',
    #         'userId': '61405336dea13163fda7257e',
    #         'img_url': 'https://t2.gstatic.com/images?q=tbn:ANd9GcQHjpQ16ZIupZR7ENzIyyXJr4v_pEWzML9EFy1SqyuwTgpfP_YnH8r-Mq96CypOs-Vk0eWHwWEIB-gy1uJSDp9kfw',
    #         'like': ['rrrr'],
    #         'continent': 'seoul'
    #     })
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
    if result:
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

    overCheck = db.user.find_one({'id': id_receive})
    if(overCheck):
        return jsonify({'result': 'overlap'})
    else:
        db.user.insert_one(
            {'id': id_receive, 'pw': pw_hash})
        return jsonify({'result': 'success'})


@app.route('/landing')
def landing():
    return render_template('landing.html')


# 네비게이션 api 부분
@app.route('/nav/<continent>')
def nav(continent):
    token_receive = request.cookies.get('mytoken')
    try:
        places = list(db.places.find({"continent": continent}))
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        print(payload['id'])
        print(places)
        return render_template('landing.html', user_info=user_info, places=places)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/api/upload', methods=['POST'])
def write_review():
    white_list = ['JPG','jpg','gif','png','PNG']
    token_receive = request.cookies.get('mytoken')
    try:

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})

        title_receive = request.form['title_give']
        review_receive = request.form['Review_give']
        continent_receive = request.form['continent_give']
        file = request.files['file_give']

        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
        extension = file.filename.split('.')[-1]
        if extension not in white_list:
            return jsonify({'result': 'fail', 'msg': '올바른 파일 형식이 아닙니다!'})
        filename = f'file-{mytime}'
        save_to = f'static/img/{filename}.{extension}'
        print(file)
        print(save_to)
        print(os.getcwd())
        file.save(save_to)

        doc = {
            'title': title_receive,
            'description': review_receive,
            'userId': payload["id"],
            'img_url': f'{filename}.{extension}',
            'like': [],
            'continent': continent_receive,
        }
        db.places.insert_one(doc)
        print(1234)
        return jsonify({'result': 'success', 'msg': '저장완료!'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("/", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/", msg="로그인 정보가 존재하지 않습니다."))

# 마이페이지 부분
@app.route('/api/mypage')
def api_mypage():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        submitted_places = list(db.places.find({'userId': payload['id']}))
        like_places = list(db.places.find({'like': payload['id']}))
        user_info = db.user.find_one({"id": payload['id']})
        print(payload['id'])
        return render_template('mypage.html', user_info=user_info, submitted_places=submitted_places,
                               like_places=like_places)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 리스팅
@app.route('/landing/reviews', methods=['GET'])
def read_reviews():

    reviews = list(db.places.find({}, {'_id': False}))
    return jsonify({'all_reviews': reviews})

@app.route('/detail/<placeId>')
def detail(placeId):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        my_query = {"_id": ObjectId(placeId)}
        login_id = payload.get('id')
        col = db.places.find_one(my_query)
        comments = list(db.comments.find({"comment_place": placeId}))
        if(comments):
            return render_template('detail.html', place=col, user_info=user_info, comments=comments)
        else:
            return render_template('detail.html', place=col, user_info=user_info, comments="false")

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/api/comment', methods=['POST'])
def upload_comment():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        id = payload.get('id')
        comment_receive = request.form['comment_give']
        place_receive = request.form['place_give']
        db.comments.insert_one({'comment': comment_receive, 'writer_id': id, 'comment_place':place_receive})
        return jsonify({'result': 'success', 'msg': '댓글이 등록되었습니다 !'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("/", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/", msg="로그인 정보가 존재하지 않습니다."))



@app.route('/api/comment/remove', methods=['POST'])
def remove_comment():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        id = payload.get('id')
        print(id)
        comment_uni_id_receive = ObjectId(request.form['comment_give'])
        comment_writer_receive = request.form['writer_give']
        if(id==comment_writer_receive):
            db.comments.delete_one({'_id': comment_uni_id_receive})
            return jsonify({'result': 'success','msg': '댓글이 삭제되었습니다.'})
        else:
            print(123)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("/", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/api/review/remove', methods=['POST'])
def remove_review():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        place_id_receive = ObjectId(request.form['_id_give'])
        review_writer_receive = request.form['writer_give']
        user_info = db.users.find_one({"id": payload["id"]})
        id = payload.get('id')
        print(place_id_receive)
        print(review_writer_receive)
        print(id)
        if (id == review_writer_receive):
            db.places.delete_one({'_id': place_id_receive})
            return jsonify({'result': 'success', 'msg': '리뷰가 삭제되었습니다.'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("/", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/api/like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        print(post_id_receive)

        my_query = {"_id": ObjectId(post_id_receive)}
        col = db.places.find_one(my_query)
        print(col)
        if action_receive == "like":
            db.places.update_one(my_query, {"$push": {"like": payload["id"]}})
            count = db.places.find_one(my_query)["like"]
            print(db.places.find_one(my_query))
            print(len(count))
            return jsonify({"result": "success", 'msg': 'updated', "count": len(count)})
        else:
            db.places.update_one(my_query, {"$pull": {"like": payload["id"]}})
            count = db.places.find_one(my_query)["like"]
            print(len(count))
            return jsonify({"result": "success", 'msg': 'updated', "count": len(count)})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


if __name__ == '__main__':
    # TODO: 한번만 실행 강제 시킬 것, 아니면 /get_db api 호출 할 것
    # utils.insert_fake_places(_FAKE_PLACE_NUM)
    app.run(debug=True)
