import requests
import socket
import os

HOST = 'http://rest_server:5000'

print(socket.gethostbyname(socket.gethostname()))

while True:
    message = input()
    if message.startswith("add_user "):
        items = message.split()
        req = {"name": items[1], "image": items[2], "sex": items[3], "email": items[4]}
        resp = requests.post(HOST + "/add_user", json=req)
        print("status:", resp)
        print("response:", resp.text)

    elif message.startswith("update_user "):
        items = message.split()
        req = {"name": items[1], "image": items[2], "sex": items[3], "email": items[4]}
        resp = requests.post(HOST + "/update_user", json=req)
        print("status:", resp)
        print("response:", resp.text)

    elif message.startswith("delete_user "):
        items = message.split()
        req = {"name": items[1]}
        resp = requests.post(HOST + "/delete_user", json=req)
        print("status:", resp)
        print("response:", resp.text)

    elif message.startswith("get_user "):
        items = message.split()
        req = {"name": items[1]}
        resp = requests.get(HOST + "/get_user", json=req)
        print("status:", resp)
        print("response:", resp.text)

    elif message == "get_users":
        resp = requests.get(HOST + "/get_users")
        print("status:", resp)
        print("response:", resp.text)

    elif message.startswith("get_pdf "):
        items = message.split()
        req = {"name": items[1]}
        resp = requests.get(HOST + "/get_pdf", json=req)
        print("status:", resp)
        with open(items[1] + ".pdf", 'wb') as f:
            f.write(resp.content)
        print("Saved to " + os.path.abspath(items[1] + ".pdf"))

    elif message.startswith("get_json "):
        items = message.split()
        req = {"name": items[1]}
        resp = requests.get(HOST + "/get_json", json=req)
        print("status:", resp)
        print("response:", resp.text)

    elif message.startswith("add_win "):
        items = message.split()
        req = {"name": items[1]}
        resp = requests.post(HOST + "/add_win", json=req)
        print("status:", resp)
        print("response:", resp.text)

    elif message.startswith("add_lose "):
        items = message.split()
        req = {"name": items[1]}
        resp = requests.post(HOST + "/add_lose", json=req)
        print("status:", resp)
        print("response:", resp.text)

    elif message.startswith("add_game_time "):
        items = message.split()
        req = {"name": items[1], "sec": items[2]}
        resp = requests.post(HOST + "/add_game_time", json=req)
        print("status:", resp)
        print("response:", resp.text)
