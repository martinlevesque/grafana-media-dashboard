
import socket
import time
import os
import re
import argparse

parser = argparse.ArgumentParser(
    prog="disk_carbon_exporter",
    description="",
)

parser.add_argument("-n", "--hostname", required=True)
parser.add_argument("-m", "--mount-path", required=True)

parsed_args = parser.parse_args()

def df_json() -> list:
    cmd_line = "df"

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

df_entries = df_json()

mount_entries = list(filter(lambda x: x["mount"] == parsed_args.mount_path, df_entries))
mount_entry = {}

if len(mount_entries):
    mount_entry = mount_entries[0]
else:
    print(f"Mount path {parsed_args.mount_path} not found")
    exit(1)

CARBON_SERVER = '0.0.0.0'
CARBON_PORT = 2003

util = mount_entry["utilization"]
message = f"{parsed_args.hostname}.disk-perc-use {util} {int(time.time())}\n"

print('sending message:\n%s' % message)
sock = socket.socket()
sock.connect((CARBON_SERVER, CARBON_PORT))
sock.sendall(message.encode())
sock.close()