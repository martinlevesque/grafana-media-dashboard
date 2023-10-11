
import socket
import time
import os
import argparse

parser = argparse.ArgumentParser(
    prog="disk_carbon_exporter",
    description="",
)

parser.add_argument("-n", "--hostname")
parser.add_argument("-m", "--mount-path")

parsed_args = parser.parse_args()

def df_json() -> dict:
    cmd_line = "df"
    print(f"Running: {cmd_line}")

    result = os.popen(f"{cmd_line}").read()
    print(f"result = {result}")

df_json()

print(f"{parsed_args.hostname}")

CARBON_SERVER = '0.0.0.0'
CARBON_PORT = 2003

message = 'martin-old-server.disk-perc-use 0.10 %d\n' % int(time.time())

print('sending message:\n%s' % message)
sock = socket.socket()
sock.connect((CARBON_SERVER, CARBON_PORT))
sock.sendall(message.encode())
sock.close()