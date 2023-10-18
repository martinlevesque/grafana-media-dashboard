
import socket
import time
import sys
import json
import os
import re
import argparse

JSON_FILENAME_PREVIOUS_NET = "previous_net.json"

parser = argparse.ArgumentParser(
    prog="net_carbon_exporter",
    description="",
)

parser.add_argument("-n", "--hostname", required=True)
parser.add_argument("-i", "--interface", required=True)

parsed_args = parser.parse_args()

def proc_net_json() -> list:
    cmd_line = "cat /proc/net/dev"

    result = os.popen(f"{cmd_line}").read()
    lines = result.splitlines()
    print(f"lines = {lines}")

    return list(
        filter(lambda x: x is not None,
            list(map(lambda x: proc_net_line_parse(x), lines))
        )
    )

def proc_net_line_parse(line):
    # replace all occurences
    cleaned_line = line.replace("|", " ").replace(":", " ")


    words = re.split(r"\s+", cleaned_line)
    words = list(filter(lambda x: x != "", words))
    print(f"words = {words}")

    if words[0] in ["Inter-|", "face"] or f"{words[0]}" == "" or len(words) < 10:
        return None

    return {
        "interface": words[0],
        "bytes_recv": words[1],
        "bytes_sent": words[9] 
    }

entries = proc_net_json()

all_entries = list(filter(lambda x: x["interface"] == parsed_args.interface, entries))
entry = {}
previous_entry = {}

if len(all_entries):
    entry = all_entries[0]
else:
    print(f"Interface {parsed_args.interface} not found")
    exit(1)

# read json file previous_net.json

# if file does not exist, create it
if os.path.isfile(JSON_FILENAME_PREVIOUS_NET) == False:
    with open(JSON_FILENAME_PREVIOUS_NET, "w") as f:
        f.write(json.dumps(entry))

    sys.exit(0)
else:
    with open(JSON_FILENAME_PREVIOUS_NET, "r") as f:
        previous_entry = json.loads(f.read())

    with open(JSON_FILENAME_PREVIOUS_NET, "w") as f:
        f.write(json.dumps(entry))

CARBON_SERVER = '0.0.0.0'
CARBON_PORT = 2003

previous_bytes_recv = float(previous_entry["bytes_recv"])
previous_bytes_sent = float(previous_entry["bytes_sent"])
new_bytes_recv = float(entry["bytes_recv"])
new_bytes_sent = float(entry["bytes_sent"])

bytes_recv = new_bytes_recv - previous_bytes_recv
bytes_sent = new_bytes_sent - previous_bytes_sent

message_recv = f"{parsed_args.hostname}-{parsed_args.interface}.bytes_recv {bytes_recv} {int(time.time())}\n"
message_sent = f"{parsed_args.hostname}-{parsed_args.interface}.bytes_sent {bytes_sent} {int(time.time())}\n"

sock = socket.socket()
sock.connect((CARBON_SERVER, CARBON_PORT))

for message in [message_recv, message_sent]:
    print('sending message:\n%s' % message)
    sock.sendall(message.encode())

sock.close()
