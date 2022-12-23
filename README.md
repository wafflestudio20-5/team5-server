# team5-server

##  **처음 작업 전 확인해주세요!**
### 1. python version: 3.9.12

### 2. pip install -r requirment.txt

### 3. .config_secret/settings_common.json 생성 (secret_key, database setting)

### 4. runserver 명령어

[ Basic ]
```
$ (local에서 개발 중에 사용)
$ python manage.py runserver -settings=config.settings.debug

$ (배포 시 사용)
$ python manage.py runserver -settings=config.settings.deploy
```

[ 귀찮을 때 ]

(가상환경 이름)/Scripts/activate 스크립트 열기 > 가장 마지막 줄에 밑에꺼 추가 > 원래대로 runserver 명령어 사용
```
export DJANGO_SETTINGS_MODULE=config.settings.debug
```
