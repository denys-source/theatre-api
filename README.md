# Theatre API 🍿

The Theatre API Service, developed using Django Rest Framework (DRF), offers a range of essential features for efficient theater management. It enables users to handle reservations and tickets, secures access with JWT authentication, and automatically filters API endpoints based on user permissions. Theatre administrators can create and manage halls, plays, and performances, with advanced filtering options for plays and performances. Users can easily search for plays by title, genres, and actors. Comprehensive documentation is available at `/api/doc/swagger` or `/api/doc/redoc`, making it user-friendly and accessible for both staff and patrons.

## ⚙️ Installing using GitHub

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

## 🐳 Running with docker

Docker should be installed
```shell
docker-compose up --build
```

## 🔓 Getting access
1. Create user at `/api/user/register`
2. Get access and refresh token at `/api/user/token/`

## 📍 Features

* Managing reservations and tickets
* JWT authentication
* API root endpoints are filtered based on current user permissions
* Creating and managing theatre halls, plays and performances
* Filtering plays by title, genres and actors
* Filtering performances by date and plays
* Documentation can be accessed at `/api/doc/swagger` or `/api/doc/redoc`

## 📋 DB scheme

![image](https://github.com/denys-source/theatre-api/assets/72623693/91de271c-de6f-4cf8-9d26-c42148800d83)

## ✅ Demo
![image](https://github.com/denys-source/theatre-api/assets/72623693/2717df91-194c-40c3-afc8-5070952020f8)
