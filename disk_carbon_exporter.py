
import socket
import time
import os
import re
import argparse

parser = argparse.ArgumentParser(
    prog="disk_carbon_exporter",
    description="",
)

parser.add_argument("-n", "--hostname")
parser.add_argument("-m", "--mount-path")

parsed_args = parser.parse_args()

def df_json() -> list:
    cmd_line = "df"
    print(f"Running: {cmd_line}")

    result = os.popen(f"{cmd_line}").read()
    lines = result.splitlines()

    return list(
        filter(lambda x: x is not None,
            list(map(lambda x: df_line_parse(x), lines))
        )
    )

def df_line_parse(line):
    words = re.split(r"\s+", line)

    if words[0] == "Filesystem":
        return None

    perc_util = float(words[4].replace("%", "")) / 100.0
    mountpoint = words[5]

    return { "utilization": perc_util, "mount": mountpoint }




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