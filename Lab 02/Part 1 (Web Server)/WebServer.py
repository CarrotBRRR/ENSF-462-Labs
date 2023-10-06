#import socket module
from socket import *

serverSocket = socket(AF_INET, SOCK_STREAM)

# Prepare a sever socket
# Fill in start
serverPort = 6789  # Choose a port number 6789
serverSocket.bind(('127.0.0.1', serverPort)) # bind to socket
serverSocket.listen(1)  # listen for connections
# Fill in end

while True:
    # Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()  # Fill in start # Fill in end
    
    try:
        message = connectionSocket.recv(1024).decode('utf-8', 'ignore')  # Fill in start # Fill in end

        if message: # check if it's a non-empty message
            filename = message.split()[1]
        else: continue

        print(f'File: {filename}')

        f = open(filename[1:])
        readData = f.read()

        # Send one HTTP header line into socket
        # Fill in start
        response_header = "HTTP/1.1 200 OK\r\n\r\n"
        connectionSocket.send(response_header.encode()) # send header
        # Fill in end

        # Send the content of the requested file to the client
        for i in range(0, len(readData)):
            connectionSocket.send(readData[i].encode())
            connectionSocket.send("\r\n".encode())
        connectionSocket.close()

    except IOError:
        # Send response message for file not found
        # Fill in start
        not_found_response = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
        print(not_found_response)
        connectionSocket.send(not_found_response.encode()) # send not found header
        # Fill in end

    # Close client socket
    # Fill in start
    connectionSocket.close()
    # Fill in end

serverSocket.close()
