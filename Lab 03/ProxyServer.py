from socket import *
import os
from urllib.parse import urlparse

PROXY_PORT = 8888
server_host = 'localhost'
CACHE_DIR = './Lab 03/cache/'
HTML = '.html'

def handle_request(client):
    message = client.recv(4096).decode('utf-8')

    print("MESSAGE: ", message)

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
    
    cached_file_path = os.path.join(CACHE_DIR, url.strip('/'))
    cached_file_path += ".html"
    print("Cache Path: ", cached_file_path)
    if os.path.exists(cached_file_path):
    # Serve the object from the cache
        with open(cached_file_path, 'rb') as cached_file:
            response = "HTTP/1.0 200 OK\r\n\r\n"
            client.send(response.encode())
            data = cached_file.read()
            print("DATA: ", data)
            client.sendall(data.encode('utf-8'))
    else:
        try:
            server = socket(AF_INET, SOCK_STREAM)
            host = url.strip('/')
            server.connect((host, 80))

            server.sendall(message.encode())

            response = server.recv(4096)
            print("RESPONSE: ", response.decode())

            # Save the object in the cache
            client.sendall(response)
            with open(cached_file_path, 'w') as cached_file:
                cached_file.write(response.decode())


        except Exception as e:
            print('oof Error: ', e)
            return
    

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
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    main()