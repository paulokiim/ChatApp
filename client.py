import socket
import select
import errno
import sys

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

username = input('Username: ')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username_encoded = username.encode('utf-8')
username_header = f'{len(username_encoded):<{HEADER_LENGTH}}'.encode('utf-8')
client_socket.send(username_header + username_encoded)

while True:
  msg = input(f'{username} -> ')

  if msg:
    msg = msg.encode('utf-8')
    msg_header = f'{len(msg):<{HEADER_LENGTH}}'.encode('utf-8')

    client_socket.send(msg_header + msg)
  
  try:
    while True:
      username_header = client_socket.recv(HEADER_LENGTH)
      if not len(username_header):
        print('Connection Closed by the Server')
        sys.exit(1)
      
      username_length = int(username_header.decode('utf-8').strip())
      username = client_socket.recv(username_length).decode('utf-8')

      msg_header = client_socket.recv(HEADER_LENGTH)
      msg_length = int(msg_header.decode('utf-8').strip())
      msg = client_socket.recv(msg_length).decode('utf-8')

      print(f'{username} <- {msg}')
  except IOError as e:
    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
      print(f'Reading Error {str(e)}')
      sys.exit(1)
    continue
  except Exception as e:
    print(f'General Error {str(e)}')
    sys.exit(1)