import requests

HOST = 'http://localhost:5000'

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
