# Theatre API

API service for theatre management written with DRF

## Installing using GitHub

Linux/MacOS:

```shell
git clone https://github.com/denys-source/theatre-api
cd theatre-api/
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

Windows:
```shell
git clone https://github.com/denys-source/theatre-api
cd theatre-api/
python venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Running with docker

Docker should be installed
```shell
docker-compose up --build
```

## Getting access
1. Create user at `/api/user/register`
2. Get access and refresh token at `/api/user/token/`

## Features

* Managing reservations and tickets
* JWT authentication
* API root endpoints are filtered based on current user permissions
* Creating and managing theatre halls, plays and performances
* Filtering plays by title, genres and actors
* Filtering performances by date and plays
* Documentation can be accessed at `/api/doc/swagger` or `/api/doc/redoc`

## Demo
![image](https://github.com/denys-source/theatre-api/assets/72623693/2717df91-194c-40c3-afc8-5070952020f8)
