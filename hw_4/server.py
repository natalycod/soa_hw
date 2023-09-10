from flask import Flask, request, send_file
import subprocess
from enum import Enum
from fpdf import FPDF
import os

import socket

current_users = {}

class Status(Enum):
    OK = "ok"
    INCORRECT_EVOLUTION = "incorrect_evolution"
    NOT_FOUND = "not_found"

class User:
    def __init__(self, name: str, image: str, sex: str, email: str):
        self.name = name
        self.image = image
        self.sex = sex
        self.email = email
        self.win_count = 0
        self.lose_count = 0
        self.game_time = 0
    
    def to_json(self):
        return {
            "name": self.name,
            "image": self.image,
            "sex": self.sex,
            "email": self.email,
        }

class UsersDatabase:
    def __init__(self):
        self.users = {}

    def add_user(self, user: User):
        if user.name in self.users:
            return Status.INCORRECT_EVOLUTION
        self.users[user.name] = user
        return Status.OK

    def update_user(self, user: User):
        if user.name not in self.users:
            return Status.INCORRECT_EVOLUTION
        self.users[user.name] = user
        return Status.OK
        
    def delete_user(self, name: str):
        if name not in self.users:
            return Status.INCORRECT_EVOLUTION
        del self.users[name]
        return Status.OK
    
    def get_user(self, name: str):
        if name not in self.users:
            return Status.NOT_FOUND, User("", "", "", "")
        return Status.OK, self.users[name]

    def get_users(self):
        result = []
        for name, user in self.users.items():
            result.append(user.to_json())
        return Status.OK, result

    def add_win(self, name: str):
        if name not in self.users:
            return
        self.users[name].win_count += 1

    def add_lose(self, name: str):
        if name not in self.users:
            return
        self.users[name].lose_count += 1

    def add_game_time(self, name: str, time_sec: int):
        if name not in self.users:
            return
        self.users[name].game_time += time_sec

app = Flask(__name__)
data = UsersDatabase()

@app.route("/add_user", methods=["POST"])
def add_user():
    status = data.add_user(User(request.json["name"], request.json["image"], request.json["sex"], request.json["email"]))
    return {"status": status.value}

@app.route("/update_user", methods=["POST"])
def update_user():
    status = data.update_user(User(request.json["name"], request.json["image"], request.json["sex"], request.json["email"]))
    return {"status": status.value}

@app.route("/delete_user", methods=["POST"])
def delete_user():
    status = data.delete_user(request.json["name"])
    return {"status": status.value}

@app.route("/get_user", methods=["GET"])
def get_user():
    status, user = data.get_user(request.json["name"])
    return {"status": status.value, "user": user.to_json()}

@app.route("/get_users", methods=["GET"])
def get_users():
    status, users = data.get_users()
    return {"status": status.value, "users": users}

@app.route("/add_win", methods=["POST"])
def add_win():
    data.add_win(request.json["name"])
    return {}

@app.route("/add_lose", methods=["POST"])
def add_lose():
    data.add_lose(request.json["name"])
    return {}

@app.route("/add_game_time", methods=["POST"])
def add_game_time():
    data.add_game_time(request.json["name"], request.json["sec"])
    return {}

def generate_pdf(user):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 22)
    pdf.cell(70, 10, 'name: ' + user.name, ln=1)
    pdf.cell(70, 10, 'sex: ' + user.sex, ln=1)
    pdf.cell(70, 10, 'image: ' + user.image, ln=1)
    pdf.cell(70, 10, 'email: ' + user.email, ln=1)
    pdf.cell(70, 10, 'Count of games: ' + str(user.win_count + user.lose_count), ln=1)
    pdf.cell(70, 10, 'Count of wins: ' + str(user.win_count), ln=1)
    pdf.cell(70, 10, 'Count of loses: ' + str(user.lose_count), ln=1)
    pdf.cell(70, 10, 'Time in game (seconds): ' + str(user.game_time), ln=1)

    path = user.name + ".pdf"
    pdf.output(path).encode('latin-1')
    return path

@app.route("/get_json", methods=["GET"])
def get_json():
    status, user = data.get_user(request.json["name"])
    json = {}
    json["name"] = user.name
    json["sex"] = user.sex
    json["image"] = user.image
    json["email"] = user.email
    json["win_count"] = user.win_count
    json["lose_count"] = user.lose_count
    json["game_count"] = user.win_count + user.lose_count
    json["game_time"] = user.game_time
    return json

@app.route("/get_pdf", methods=["GET"])
def get_pdf():
    status, user = data.get_user(request.json["name"])
    path, json = generate_pdf(user)
    return send_file(path, download_name=path)

app.run(host='0.0.0.0')
