# 데브파이브 백엔드

---

## Install

**python 3.9** poetry 설치

    pip install poetry

가상 환경 접속

    poetry shell

라이브러리 설치

    poetry install

root 폴더에 .env 파일을 작성

    STAGE=local, prod, dev
    DB_URL=localhost
    DB_PORT=5432
    DB_ID=postgres
    DB_PW=pw
    DB_DB=postgres
    DB_SCHEMA=public

서버 시작

    poetry run start

Lint 문법 검사 시작

    poetry run lint

## Update database models

    poetry run commit "message"

실제 데이터베이스에 적용 (서버 켜질 때 자동 적용) 비권장

    poetry run push

## FCM 적용

firebase admin account json을 app 폴더 안에 아래 파일명으로 추가

    google-account.json