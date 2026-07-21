import socket
import requests
import time
import subprocess


SERVER = "https://rendezvous-huzh.onrender.com"

GAME = "test"


PORT4 = 6000
PORT6 = 6001


ID = input("Session ID: ")


def get_ipv6():
    for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6):
        addr = info[4][0]

        # ignore localhost and link-local addresses
        if not addr.startswith("::1") and not addr.startswith("fe80"):
            return addr

    return None


ipv6 = get_ipv6()


sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock4.bind(("0.0.0.0", PORT4))


sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock6.bind(("::", PORT6))


r = requests.post(
    SERVER + "/join",
    json={
        "id": ID,
        "game": GAME,
        "port": PORT4,
        "port6": PORT6,
        "ipv6": ipv6
    }
)


data = r.json()


if not data["success"]:
    print(data)
    exit()


peer4 = (
    data["ipv4"],
    data["port"]
)

peer6 = (
    data["ipv6"],
    data["port6"]
)

start = data["start"]


print("Host:")
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
        "Connected IPv4",
        addr,
        msg
    )


except TimeoutError:

    print("IPv4 failed")


    print("Trying IPv6")

    sock6.sendto(
        b"hello6",
        peer6
    )

    sock6.settimeout(5)


    try:

        msg, addr = sock6.recvfrom(1024)

        print(
            "Connected IPv6",
            addr,
            msg
        )


    except TimeoutError:

        print("No connection")