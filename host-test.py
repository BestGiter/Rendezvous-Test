import socket
import requests
import time
import threading
import subprocess

SERVER = "https://rendezvous-huzh.onrender.com"

GAME = "test"

PORT4 = 5000
PORT6 = 5001


def get_ipv6():
    for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6):
        addr = info[4][0]

        # ignore localhost and link-local addresses
        if not addr.startswith("::1") and not addr.startswith("fe80"):
            return addr

    return None


sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock4.bind(("0.0.0.0", PORT4))

sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock6.bind(("::", PORT6))


ipv6 = get_ipv6()


# create session
r = requests.post(
    SERVER + "/create",
    json={
        "game": GAME,
        "port": PORT4,
        "port6": PORT6,
        "ipv6": ipv6
    }
)

data = r.json()

ID = data["id"]
TOKEN = data["token"]

print("Session:", ID)
print("IPv6:", ipv6)


def updater():
    while True:
        requests.post(
            SERVER + "/update",
            json={
                "id": ID,
                "token": TOKEN,
                "port": PORT4,
                "port6": PORT6,
                "ipv6": ipv6
            }
        )

        time.sleep(30)


threading.Thread(target=updater, daemon=True).start()


print("Waiting for player...")


while True:

    r = requests.post(
        SERVER + "/info",
        json={
            "id": ID,
            "token": TOKEN,
            "game": GAME
        }
    )

    data = r.json()

    if data["success"]:
        break

    time.sleep(1)


peer4 = (data["ipv4"], data["port"])
peer6 = (data["ipv6"], data["port6"])
start = data["start"]


print("Player found")
print(peer4)
print(peer6)


while time.time() < start:
    time.sleep(0.01)


# IPv4 punch
print("Trying IPv4")

sock4.sendto(
    b"hello",
    peer4
)

sock4.settimeout(5)

try:
    msg, addr = sock4.recvfrom(1024)

    print(
        "Connected IPv4:",
        addr,
        msg
    )

except TimeoutError:

    print("IPv4 failed")


    # IPv6 fallback
    print("Trying IPv6")

    sock6.sendto(
        b"hello6",
        peer6
    )

    sock6.settimeout(5)

    try:
        msg, addr = sock6.recvfrom(1024)

        print(
            "Connected IPv6:",
            addr,
            msg
        )

    except TimeoutError:
        print("Failed completely")