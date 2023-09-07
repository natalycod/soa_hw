from flask import Flask, request
import subprocess
from enum import Enum

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
            return Status.NOT_FOUND, {}
        return Status.OK, self.users[name]

    def get_users(self):
        result = []
        for name, user in self.users.items():
            result.append(user.to_json())
        return Status.OK, result

app = Flask(__name__)
data = UsersDatabase()

@app.route("/add_user", methods=["POST"])
def add_user():
    status = data.add_user(User(request.json["name"], request.json["image"], request.json["sex"], request.json["email"]))
    return {"status": status.value}

@app.route("/update_user", methods=["POST"])
def update_user():
    print("here")
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

app.run(host='localhost')
