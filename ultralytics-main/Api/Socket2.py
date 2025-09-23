import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))

client_socket.sendall(b'Hello, Server!')
data = client_socket.recv(1024)
print(f"Received: {data.decode('utf-8')}")

client_socket.close()
