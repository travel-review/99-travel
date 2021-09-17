from flask import Flask, request, jsonify, redirect, url_for, render_template
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import timedelta
import os
import jwt
import hashlib

import utils

app = Flask(__name__)

# 배포시에는 mongodb://user:password@ip주소 형식으로 변경합니다.
client = MongoClient('127.0.0.1')
db = client.travel_plus

_FAKE_PLACE_NUM = 5
SECRET_KEY = 'SPARTA'


# 더미데이터를 받아옵니다. 다양한 이미지 사이즈를 preview합니다.
@app.route('/get_db')
def tmp_get_db():
    utils.insert_fake_places(_FAKE_PLACE_NUM)
    return render_template('login.html')


# 시작 페이지. 사용자 토큰을 확인 후 login 페이지나 landing 페이지로 보내줍니다.
@app.route('/')
def main():
    token_receive = request.cookies.get('my_token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        collection = db['places']
        # 모든 장소를 검색합니다.
        places = collection.find({})
        return render_template('landing.html', user_info=user_info, places=places)
    except jwt.ExpiredSignatureError:
        print("로그인 시간이 만료되었습니다.")
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        print("로그인 정보가 존재하지 않습니다.")
        return redirect(url_for("login"))


# 로그인 페이지
@app.route('/login')
def login():
    return render_template('login.html')


# 로그인 api
@app.route('/api/signin', methods=['POST'])
def api_sign_in():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    # id, 암호화된 pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result:
        # payload에는 유저의 id와 만료시간이 들어있습니다.
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY,
                           algorithm='HS256').decode('utf-8')
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면 fail을 반환합니다.
    else:
        print('아이디/비밀번호가 일치하지 않습니다.')
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입 페이지
@app.route('/signup')
def signup():
    return render_template('signup.html')


# 회원가입 api
@app.route('/api/signup', methods=['POST'])
def api_sign_up():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    over_check = db.user.find_one({'id': id_receive})
    # 현재 존재하는 id인지 중복체크합니다.
    if over_check:
        return jsonify({'result': 'overlap'})
    else:
        db.user.insert_one({'id': id_receive, 'pw': pw_hash})
        return jsonify({'result': 'success'})


# 메인 페이지
@app.route('/landing')
def landing():
    return render_template('landing.html')


# 메인 페이지 네비게이션 api
@app.route('/nav/<continent>')
def nav(continent):
    token_receive = request.cookies.get('my_token')
    try:
        places = list(db.places.find({"continent": continent}))
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        print(user_info)
        print(places)
        return render_template('landing.html', user_info=user_info, places=places)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 업로드 페이지
@app.route('/upload')
def upload():
    return render_template('upload.html')


# 업로드 api
@app.route('/api/upload', methods=['POST'])
def write_review():
    white_list = ['JPG', 'jpg', 'gif', 'png', 'PNG', 'webp']
    token_receive = request.cookies.get('my_token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 타이틀
        title_receive = request.form['title_give']
        # 설명
        review_receive = request.form['Review_give']
        # 대륙이름
        continent_receive = request.form['continent_give']
        # 파일
        file = request.files['file_give']
        today = datetime.now()
        # 현재시간
        my_time = today.strftime('%Y-%m-%d-%H-%M-%S')
        # 확장자
        extension = file.filename.split('.')[-1]
        # 확장자에 따라 올릴 수 있는 파일을 제한하여 오류 메세지를 전송합니다.
        # 프론트로 대륙 선택을 하지 않았을 경우에도 오류메세지를 전송합니다.
        if extension not in white_list:
            return jsonify({'result': 'fail', 'msg': '올바른 파일 형식이 아닙니다!'})
        filename = f'file-{my_time}'
        save_to = f'static/img/{filename}.{extension}'
        print(file)
        print(save_to)
        print(os.getcwd())
        file.save(save_to)

        # 업로드 파일을 모델 형식에 맞추어 db에 추가합니다.
        doc = {
            'title': title_receive,
            'description': review_receive,
            'userId': payload["id"],
            'img_url': f'{filename}.{extension}',
            'like': [],
            'continent': continent_receive,
        }
        db.places.insert_one(doc)
        return jsonify({'result': 'success', 'msg': '저장완료!'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("/", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/", msg="로그인 정보가 존재하지 않습니다."))


# 마이 페이지
@app.route('/api/mypage')
def api_my_page():
    token_receive = request.cookies.get('my_token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 내가 소개한 여행지 리스트
        submitted_places = list(db.places.find({'userId': payload['id']}))
        # 내가 좋아요 한 여행지 리스트
        like_places = list(db.places.find({'like': payload['id']}))

        user_info = db.user.find_one({"id": payload['id']})
        return render_template('mypage.html', user_info=user_info, submitted_places=submitted_places,
                               like_places=like_places)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 메인 페이지 리스팅 api
@app.route('/landing/reviews', methods=['GET'])
def read_reviews():
    reviews = list(db.places.find({}, {'_id': False}))
    return jsonify({'all_reviews': reviews})


# 상세 페이지
@app.route('/detail/<place_id>')
def detail(place_id):
    token_receive = request.cookies.get('my_token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        my_query = {"_id": ObjectId(place_id)}
        col = db.places.find_one(my_query)
        # 등록된 모든 코멘트 리스트
        comments = list(db.comments.find({"comment_place": place_id}))
        if comments:
            return render_template('detail.html', place=col, user_info=user_info, comments=comments)
        else:
            return render_template('detail.html', place=col, user_info=user_info, comments="false")
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 댓글 api
@app.route('/api/comment', methods=['POST'])
def upload_comment():
    token_receive = request.cookies.get('my_token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 댓글 내용
        comment_receive = request.form['comment_give']
        # 댓글을 작성한 게시글의 고유 id
        place_receive = request.form['place_give']
        # 댓글을 작성한 게시글에 맞게 comments db에 댓글을 추가합니다.
        db.comments.insert_one({'comment': comment_receive, 'writer_id': payload["id"], 'comment_place': place_receive})
        return jsonify({'result': 'success', 'msg': '댓글이 등록되었습니다 !'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("/", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/", msg="로그인 정보가 존재하지 않습니다."))


# 댓글 삭제 api
@app.route('/api/comment/remove', methods=['POST'])
def remove_comment():
    token_receive = request.cookies.get('my_token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload["id"])
        # 댓글을 작성한 사람의 고유 id
        comment_uni_id_receive = ObjectId(request.form['comment_give'])
        # 댓글을 작성한 사람의 유저 id
        comment_writer_receive = request.form['writer_give']
        # 일치하는 댓글을 db에서 삭제합니다.
        db.comments.delete_one({'_id': comment_uni_id_receive, 'writer_id': comment_writer_receive})
        return jsonify({'result': 'success', 'msg': '댓글이 삭제되었습니다.'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("/", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/", msg="로그인 정보가 존재하지 않습니다."))


# 게시글 삭제 api
@app.route('/api/review/remove', methods=['POST'])
def remove_review():
    token_receive = request.cookies.get('my_token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        place_id_receive = ObjectId(request.form['_id_give'])
        review_writer_receive = request.form['writer_give']

        print(place_id_receive)
        print(review_writer_receive)
        print(payload["id"])
        # 일치하는 게시글을 db에서 삭제합니다.
        db.places.delete_one({'_id': place_id_receive, 'id': review_writer_receive})
        return jsonify({'result': 'success', 'msg': '리뷰가 삭제되었습니다.'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("/", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/", msg="로그인 정보가 존재하지 않습니다."))


# 하트 api
@app.route('/api/like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('my_token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 게시글을 올린 id
        post_id_receive = request.form["post_id_give"]
        # post로 받은 action (좋아요/취소)
        action_receive = request.form["action_give"]
        print(post_id_receive)

        my_query = {"_id": ObjectId(post_id_receive)}
        col = db.places.find_one(my_query)
        print(col)
        if action_receive == "like":
            # 현재 접속중인 아이디를 게시글의 좋아요 리스트에 추가합니다. 아이디에 따라 좋아요 정보가 재 로그인 후에도 남아있습니다.
            # 한 게시물에느 동일 아이디 당 하나의 좋아요를 줄 수 있습니다.
            db.places.update_one(my_query, {"$push": {"like": payload["id"]}})
            count = db.places.find_one(my_query)["like"]
            print(db.places.find_one(my_query))
            # 좋아요 수 표시는 구현되어 있으나 기획상 삭제되었습니다.
            print(len(count))
            return jsonify({"result": "success", 'msg': 'updated', "count": len(count)})
        else:
            db.places.update_one(my_query, {"$pull": {"like": payload["id"]}})
            count = db.places.find_one(my_query)["like"]
            # 좋아요 수 표시는 구현되어 있으나 기획상 삭제되었습니다.
            print(len(count))
            return jsonify({"result": "success", 'msg': 'updated', "count": len(count)})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


# 클린 코드를 위해 경고메세지도 최소화했습니다.
if __name__ == '__main__':
    app.runapp.run(host='0.0.0.0', port=5000, debug=True)

