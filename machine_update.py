
import socket
import time


CARBON_SERVER = '0.0.0.0'
CARBON_PORT = 2003

message = 'foo.bar.baz 400 %d\n' % int(time.time())

print('sending message:\n%s' % message)
sock = socket.socket()
sock.connect((CARBON_SERVER, CARBON_PORT))
sock.sendall(message.encode())
sock.close()