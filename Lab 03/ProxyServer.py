from socket import *
import sys

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    sys.exit(2)

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)

server_host = 'localhost'
# You need to bind the server socket to an IP address and port here
tcpSerSock.bind(('your_ip_address', 8888))
# Start listening on the server socket
tcpSerSock.listen(1)

while True:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

    message = tcpCliSock.recv(4096).decode()


    filename = message.split()[1].partition("/")[2]
    fileExist = "false"
    filetouse = "./Lab 03/" + filename

    try:
        # Check whether the file exists in the cache
        f = open(filetouse[1:], "r")
        outputdata = f.readlines()
        fileExist = True

        # Send a response message from cache
        tcpCliSock.send("HTTP/1.0 200 OK\r\n")
        tcpCliSock.send("Content-Type:text/html\r\n")

        # You need to send the cached data back to the client here
        print('Hit Cache')

    except IOError:
        if fileExist == False:
            # Create a socket on the proxy server
            c = socket(AF_INET, SOCK_STREAM)
            hostn = filename.replace("www.", "", 1)

            try:
                # Connect to the socket to port 80
                # Example: c.connect((hostn, 80))

                # Create a temporary file on this socket and send the request to port 80
                fileobj = c.makefile('r', 0)
                fileobj.write("GET " + "http://" + filename + "HTTP/1.0\n\n")

                # You need to read the response into a buffer and send it back to the client

                # Create a new file in the cache for the requested file
                # Also, send the response in the buffer to the client socket and the corresponding file in the cache
                tmpFile = open("./" + filename, "wb")

                # You need to write the data to the cache and send it back to the client

            except:
                print("Illegal request")

    # Handle HTTP response message for file not found

    # Close the client and the server sockets
    tcpCliSock.close()

# Close the server socket
# Example: tcpSerSock.close()
