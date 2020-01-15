import socket
import time
import select

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Enable us to reconnect
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((IP, PORT))

server.listen()

print(f'Server Listening on Port {PORT}')

socket_list = [server]

clients = {}

def receive_message(client_socket):
  try:
    msg_header = client_socket.recv(HEADER_LENGTH)

    if not len(msg_header):
      return False

    msg_length = int(msg_header.decode('utf-8').strip())
    return { 'header': msg_header, 'data': client_socket.recv(msg_length) }
  except:
    return False

while True:
  read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)

  for notify_socket in read_sockets:
    if notify_socket == server:
      client_socket, client_address = server.accept()

      user = receive_message(client_socket)
      if user == False:
        continue

      socket_list.append(client_socket)
      clients[client_socket] = user

      username = user['data'].decode('utf-8')

      print(f'Accepted connection from IP {client_address[0]}:{client_address[1]} with username:{username}')

    else:
      msg = receive_message(notify_socket)
      
      if msg == False:
        client = clients[notify_socket]['data'].decode('utf-8')
        print(f'Connection closed from {client}')
        socket_list.remove(notify_socket)
        del clients[notify_socket]
        continue
      
      user = clients[notify_socket]
      username = user['data'].decode('utf-8')
      msg_decoded = msg['data'].decode('utf-8')
      print(f'Received Message from {username}: {msg_decoded}')

      for client_socket in clients:
        if client_socket != notify_socket:
          client_socket.send(user['header'] + user['data'] + msg['header'] + msg['data'])

  for notify_socket in exception_sockets:
    socket_list.remove(notify_socket)
    del clients[notify_socket]
