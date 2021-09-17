# 항해 99 미니프로젝트 1 29조 - Travel+
참여인원 : 김영우/ 이경아/ 권민혁

개발기간 : 2021.9.13 ~ 2021.9.17

개발언어:
-   Frontend : HTML / CSS/ JavaScript
-   Backend : Python(Flask)


**목차**

[1. 프로젝트 설명](#프로젝트-설명)

[2. 시연 영상](#시연-영상)

[3. What I learned ](#what-i-learned)

[4. 주요 기능 구현 (API) ](#주요-기능-구현)


## 프로젝트 설명

미니 웹 프로젝트를 만들어 런칭하세요! 
 29조는 여행 후기를 자유롭게 작성할 수 있는 페이지를 만들었습니다!


## 🎥시연 영상

 [Click](https://www.youtube.com/watch?v=eUjLl5feeWU&ab_channel=kyuung)
 
 

## 🔎What I learned

1.  실제 사이트에서 어떤 식으로 사이트를 구성할까?

2.  프론트엔드와 백엔드는 어떤 차이점 일까?

3.  서버와 클라이언트는 어떻게 통신을 할까?

4.  어떻게하면 팀원들과 프로젝트를 잘할 수 있을까?


## 🛠주요 기능 구현

|   API             |Method                |URL              |  설명         |
|----------------|-------------------------------|-----------|-----------   |
|api_signin()    |`POST`             |'/api/signin'          |  로그인          |
|api_signup()      |`POST`            |'/api/signup'         |   회원가입       |
| write_review() |	`POST` 	     |/api/upload			|  리뷰 업로드   |
|upload_comment()|`POST`|/api/comment| 댓글 등록하기|
|remove_comment()|`POST`|'/api/comment/remove'|댓글 삭제
|remove_review()|`POST`|/api/review/remove|리뷰 삭제|
|update_like()|`POST`|'/api/like'|좋아요 정보 불러오기|
|nav(continent)   |`GET`		|/nav/\<continent>     |대륙 선택(네비게이션) |
|api_mypage()     |`GET`         |/api/mypage           |마이페이지 로그인 확인|
| read_reviews()|`GET`           |/landing/reviews       |리뷰 불러오기|
|detail(placeId)|`GET`          |/detail/\<placeId>|    detail 페이지 로그인 확인 및 값 전달  |
