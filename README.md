# Team 5 Django Team Server
#
#### _🧇 KREAM-Waffle 백엔드 레포에 오신 것을 환영합니다 🧇_
#


### 🧑🏻‍💻 Contributors 
| Contributor | Major Contribution |
| ------ | ------ |
| **Yoonsuh Chung** | Basic authorization & authentication / Shop App / Test CI |
| **Seungah Lee** | Overall deployment settings / AWS CI&CD |
| **Jinahn Jeong** | Social Login / Style App |
#
안녕하세요, 저희는 와플 20.5기 토이프로젝트 Team 5의 장고 팀입니다:)
KREAM이라는 중고거래 플랫폼을 클론코딩하여, 필수기능에 따라 크게 `Accounts` 앱과 `Shop` 앱, `Style` 앱을 구현해 보았습니다.
#
### 💻 기술 스택
```
웹 프레임워크: Django 4.1.4, Django Rest Framework 3.14.0
언어: Python 3.10.6
배포환경: AWS EC2, AWS S3
웹 서버: NginX
WSGI: gunicorn
RDS: PostGreSQL
```

### 🪡 ERD(feat. graph_models)


내용
#
### ✨ Essence of our Project
: 클론 코딩을 진행하면서 신경 썼던, 혹은 잘 되었다고 생각하는 부분은?
#
#### 1. Accounts App
- 기본 회원가입/로그인
  - 써드파티 라이브러리인 `dj_rest_auth`를 활용
  - 토큰 인증을 위해 플러그인인 `djangorestframework-simplejwt` 사용
  - 로그인과 회원가입을 커스터마이징하기 위해 플러그인인 `django-allauth` 활용
- 로그아웃
  - JWT 토큰을 따로 디비에 저장하고 있지 않았기 때문에, 로그아웃 시에 비교적 만료기간이 긴 refresh token을 blacklist 처리해주는 수단이 필요하였음
    - `rest_framework_simplejwt.token_blacklist` 활용
  - api endpoint로는 dj_rest_auth에서 제공하는 로그아웃 api를 활용함. 이때 dj_rest_auth는 로컬의 쿠키를 지워주고 쿠키로 담겨온 토큰을 블랙리스트 처리해야 하나, 쿠키를 인식하지 못하는 문제 발생
    - `djangorestframework-simplejwt`에서 쿠키로 담겨오는 토큰을 허용하지 않는다는 이슈 발견
    - 커스텀 Middleware인 `MoveJWTRefreshCookieIntoTheBody`를 통해 요청의 쿠키에 담긴 refresh token을 body로 옮겨주는 작업을 통해 문제 해결
#
#### 2. Shop App
내용
#
#### 3. Style App


1. 유저 정보를 불러오는 **가벼운** 요청과 유저의 팔로워 목록, 팔로잉 목록, 게시물 목록 각각을 불러오는 **무거운** 요청을 받아들이는 URI 분리. 게시물/댓글/대댓글 정보와 그에 공감한 유저 목록에 대한 URI도 역시 분리함.
    - `GET /styles/profiles/{id}/`
        - `GET /styles/profiles/{id}/followers/`
        - `GET /styles/profiles/{id}/followings/`
        - `GET /styles/posts/?type=default&user_id=`
    - `GET /styles/posts/{id}/`
        - `GET /styles/posts/{id}/likes/`
    - DetailView 안에 ListView가 중첩된 구조
    - 클라이언트 단에서 비동기적으로 처리 가능하게


2. 유저의 게시물 목록 View와 게시물 피드 View를 하나의 URI에서 **query param**으로 구분
    
    > `GET /styles/posts/?type=&user_id=`
    > 
    > 
    > 게시물 목록. query param에 따라 요청을 달리 보낼 수 있습니다. CursorPagination 적용.
query param이 없거나, 유효하지 않은 경우 `HTTP_400_BAD_REQUEST` 를 내려줌.
    > 
    > query param 예시:
    > 
    > - `?type=popular`
    >     
    >     인기 피드. 추후 구현 예정
    >     
    > - `?type=latest`
    >     
    >     최신 피드. 아무나 접근 가능. 생성 시간 역순으로 정렬.
    >     
    > - `?type=following`
    >     
    >     팔로잉 피드. 로그인 한 유저만 접근 가능. 생성 시간 역순으로 정렬.
    >     로그인 하지 않은 유저가 접근 시 `HTTP_401_UNAUTHORIZED` 를 내려줌.
    >     
    > - `?type=default&user_id={user_id}`
    >     
    >     특정 프로필(user_id)의 게시물 목록. 아무나 접근 가능. 생성 시간 역순으로 정렬.
    >     default type일 경우, user_id를 넣어주지 않으면 `HTTP_400_BAD_REQUEST` 를 내려줌. 
    >     
    - 단점: fat view


3. 팔로우/팔로우 취소, 공감/공감 취소 등의 api를 각각 **하나의 endpoint**에서 처리
    - `PATCH /styles/profiles/{user_id}/follow/`
    - `PATCH /styles/{object_type}/{object_id}/like/`
    - 토글 방식.
        - 언팔로우→팔로우 (Follow object create)
        - 팔로우→언팔로우 (Follow object delete)
    - RESTful하지 않으나 편리한 구현
    - PATCH 활용: 해당 api들은 idempotent하지 않고(같은 요청을 여러 번 했을 때 결과가 달라짐), 실제로 자원이 변경되기 때문.


4. `following`, `liked` 등의 field를 두어 클라이언트에서 현재 로그인 한 유저를 기준으로, 대상 유저 instance의 팔로잉 여부나 게시물/댓글/대댓글 instance의 공감 여부를 내려줌
    
    > `"following":`
    > 
    > 1. `"login required"`
    > 로그인 하지 않은 유저가 접근했을 때
    > 2. `null`
    > 자기 자신의 프로필을 요청했을 때
    > 3. `true`
    > 팔로잉 O
    > 4. `false`
    > 팔로잉 X
    
    > `"liked":`
    > 
    > 1. `"login required"`
    > 로그인 하지 않은 유저가 접근했을 때
    > 2. `true`
    > 공감 O
    > 3. `false`
    > 공감 X
     - 클라이언트에서 해당 필드를 참조하면 바로 컴포넌트를 띄울 수 있도록
         - 팔로우 버튼
         - 공감 버튼
     - serializer 단에서 .to_representation() 오버라이딩


5. 게시물에 대한 댓글/대댓글 목록을 nested하게 하나의 응답으로 내려줌.

    > `GET /styles/posts/{id}/comments`
    > 
    > 
    > 게시물(id)의 댓글&대댓글 목록. 로그인 한 유저만 접근 가능. 댓글은 생성 시간 역순으로, 대댓글은 생성 시간 순으로 정렬.
    > 
    > Response 예시:
    > 
    > ```json
    > [
    >   {
    >     "id": 5,
    >     "content": "reply created by admin", # 댓글 내용
    >     "created_by": { # 댓글 작성자 프로필
    >       "user_id": 1,
    >       "user_name": "admin",
    >       "profile_name": "948d791",
    >       "image": null,
    >       "following": null
    >     },
    >     "created_at": "2023-01-27T19:45:49.499747+09:00", # 댓글 생성 시간
    >     "replies": [ # 댓글에 달린 대댓글 리스트
    >       {
    >         "id": 13,
    >         "content": "reply!", # 대댓글 내용
    >         "to_profile": { # 대댓글 보내는 대상의 프로필
    >           "user_id": 3,
    >           "profile_name": "08b7103"
    >         },
    >         "created_by": { # 대댓글 작성자 프로필
    >           "user_id": 2,
    >           "user_name": "jeongjinan123",
    >           "profile_name": "377bc71",
    >           "image": null,
    >           "following": true
    >         },
    >         "created_at": "2023-01-29T00:44:30.607082+09:00", # 대댓글 생성 시간
    >         "num_likes": 1, # 공감 수
    >         "liked": false # 공감 여부(현재 로그인 한 유저 기준)
    >       }
    >     ],
    >     "num_likes": 1, # 공감 수
    >     "liked": false # 공감 여부(현재 로그인 한 유저 기준)
    >   },
    >   {
    >     "id": 3,
    >     "content": "comment created by admin",
    >     "created_by": {
    >       "user_id": 1,
    >       "user_name": "admin",
    >       "profile_name": "948d791",
    >       "image": null,
    >       "following": null
    >     },
    >     "created_at": "2023-01-27T17:28:22.049404+09:00",
    >     "replies": [],
    >     "num_likes": 0,
    >     "liked": false
    >   }
    > ]
    > ```
    >
#
#### 4. Deployment
##### AWS: EC2, RDS, S3, CodeDeploy
사용 이유: 
장고 세미나에서는 Render.com(Paas)를 사용해서 굉장히 편안하게 배포를 진행할 수 있었는데, Iaas인 AWS 상에서 직접 하나하나 세팅해보고 싶어서 EC2와 RDS를 사용하게 되었습니다.
신경 쓴 부분: 
1) RDS와 EC2 사이의 네트워크 외에도 개발 시 서버에 백엔드 팀원들이 접속할 수 있게 세팅하였습니다.
2) RDS를 연결해서 볼 때 IDE 외에 pgAdmin을 이용해 테이블 확인 및 row 편집이 가능하도록 하였습니다.
3) S3?

아직 해결중인 부분:
1) AWS CodeDeploy를 사용해보려고 했으나 S3까지 업로드 후 CodeDeploy를 이용해 업로드가 이루어지지 않아 수동 배포를 진행하고 있습니다.

##### WSGI: gunicorn
사용 이유: 
장고 세미나에서 사용하기도 했지만, uWSGI에 비해 가볍고, 기능 상 차이가 없다고 평가되고 있어 사용하게 되었습니다.
신경 쓴 부분:
1) gunicorn을 사용할 때 socket(unix socket)을 이용하는 방식과 port(tcp/ip)를 이용하는 방식이 있는데, 전자의 경우 후자와 다르게 동일한 시스템 내에서 작동 중이라는 걸 전제로 동작해 후자에서 필요한 네트워크를 이용해 전달 시 필요한 검증들을 줄일 수 있어 전자를 선택하여 구현했습니다.
2) gunicorn을 사용할 때, worker 수를 정해야하는데 도큐먼트에 따라 2*cpu core +1의 수를 따라 결정하였습니다. 사용하는 ec2의 코어가 1개 이므로 3으로 설정하였습니다.

##### Web Server: nginx
사용 이유:
gunicorn으로도 서버를 돌릴 수 있다고 배웠지만, reverse proxy로써 웹과 앱에서의 요청을 모두 처리해야하는 서버인 만큼 동시 요청에 대해 적절한 로드 밸런싱을 제공해야 한다고 생각해 연결했습니다
신경 쓴 부분:
1) https 설정을 certbot을 이용해 설정하였고, http로 접속했을 때 https로 자동으로 연결되도록 설정하였습니다

추가할 만한 부분:
1) certbot에서 ssl 인증서 자동 갱신을 cron job으로 등록할 수 있을 거 같아 시도해볼 수 있을 것 같습니다.














