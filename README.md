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
RDS: PostGreSQL
```

### 🪡 ERD(feat. graph_models)


내용
#
### ✨ Essence of our Project
: 클론 코딩을 진행하면서 신경 썼던, 혹은 잘 되었다고 생각하는 부분은?
#
#### 1. Accounts App
내용
#
#### 2. Shop App
내용
#
#### 3. Style App
내용
#
#### 4. Deployment
##### AWS: EC2, RDS, S3, CodeDeploy
사용 이유: 
장고 세미나에서는 Heroku(Saas)를 사용해서 굉장히 편안하게 배포를 진행할 수 있었는데, Iaas인 AWS 상에서 직접 하나하나 세팅해보고 싶어서 EC2와 RDS를 사용하게 되었습니다.
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














