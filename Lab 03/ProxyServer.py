from socket import *
import os

tcpSerSock = socket(AF_INET, SOCK_STREAM)

server_address = ("127.0.0.1", 8888)
tcpSerSock.bind(server_address)
tcpSerSock.listen(1)

domainName = ""
searchFile = ""
while 1:
    # start receiving data from the client
    print("Ready to serve...")

    tcpCliSock, addr = tcpSerSock.accept()
    print("Received a connection from:", addr)

    # Fill in start.
    message = tcpCliSock.recv(1024).decode()
    # Fill in end.
    print("MESSAGE:", message)

    # Extract the filename from the given message
    if len(message) > 1:
        print(message.split()[1])
        filename = message.split()[1].partition("/")[2]
        print(filename)

    fileExist = False

    if filename.startswith("www."):
        domainName = filename
        print(f"domainName = {domainName}")
    else:
        searchFile = filename
        print(f"searchFile = {searchFile}")
    try:
        file_path = os.path.join("./Lab 03/cache/", domainName + "/" + filename)
        print(f"file_path = {file_path}")

        # Check wether the file exist in the cache
        f = open(f"./{file_path}", "rb")
        outputdata = f.readlines()
        fileExist = True
        print("Hit in cache")

        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
        tcpCliSock.send("Content-Type:text/html\r\n".encode())

        for line in outputdata:
            tcpCliSock.send(line)
        tcpCliSock.send("\r\n".encode())

        tcpCliSock.close()

    except IOError:
        if fileExist == False:
            # Create a socket on the proxyserver
            c = socket(AF_INET, SOCK_STREAM)

            try:
                # Connect to the socket to port 80
                c.connect((domainName, 80))

                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                fileobj = c.makefile("rwb", 0)
                request = "GET /" + searchFile + " HTTP/1.0\r\n\r\n"
                fileobj.write(request.encode())

                buff = fileobj.readlines()
                file_path = os.path.join("./Lab 03/cache/", domainName + "/" + filename)

                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Write the response to the cache file
                # Also send the response in the buffer to client socket and the corresponding file in the cache
                with open(f"./{file_path}", "wb") as f:
                    for line in buff:
                        f.write(line)
                        tcpCliSock.send(line)
            except:
                print("Illegal request")
            
            c.close()

        else:
            tcpCliSock.send("HTTP/1.0 400 Bad Request\r\n".encode())

    # Close the client and the server sockets
    tcpCliSock.close()

tcpSerSock.close()