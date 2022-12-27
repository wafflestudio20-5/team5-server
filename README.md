# team5-server

##  **처음 작업 전 확인해주세요!**
### 1. python version: 3.10.6 (배포 시 3.9.12로 다운그레이드가 안되네요...)

### 2. pip install -r requirment.txt

### 3. .config_secret/settings_common.json, settings_debug.json, settings_deploy.json 생성

### 4. runserver 명령어

[ Basic ]
```
$ (local에서 개발 중에 사용)
$ python manage.py runserver -settings=config.settings.debug

$ (배포 시 사용)
$ python manage.py runserver -settings=config.settings.deploy
```

[ 환경변수 사용하기 ]

```
$ (local에서 개발 중에 사용)
$ export DJANGO_SETTINGS_MODULE=config.settings.debug
$ python manage.py runserver

$ (배포 시 사용)
$ export DJANGO_SETTINGS_MODULE=config.settings.deploy
$ python manage.py runserver

```