from socket import *
from urllib.parse import urlparse

PROXY_PORT = 8888
server_host = 'localhost'

def handle_request(client):
    message = client.recv(4096).decode('utf-8')

    print("Message: ", message)

    lines = message.split('\r\n')
    if len(lines) == 0:
        return

    line1 = lines[0]
    print("first line: ", line1)
    method, url, http = line1.split(' ')

    if method != 'GET':
        respose = b'HTTP/1.1 400 Bad Request\r\n\r\n'
        client.sendall(respose)
        return

    try:
        server = socket(AF_INET, SOCK_STREAM)
        host = url.strip('/')
        server.connect((host, 80))

        server.sendall(message.encode())

        response = server.recv(4096)

        client.sendall(response)

    except Exception as e:
        print('oof Error: ', e)
    

    # Close the client and the server sockets
    client.close()
    server.close()


def main():
    proxy_socket = socket(AF_INET, SOCK_STREAM)
    proxy_socket.bind((server_host, PROXY_PORT))
    proxy_socket.listen(1)

    while True:
        client, addr = proxy_socket.accept()
        print("Connection from", addr)
        handle_request(client)

if __name__ == '__main__':
    main()