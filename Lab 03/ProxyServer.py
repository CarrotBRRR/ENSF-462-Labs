from socket import *
import os

tcpSerSock = socket(AF_INET, SOCK_STREAM)

server_address = ("127.0.0.1", 8888)
tcpSerSock.bind(server_address)
tcpSerSock.listen(1)

domainName = ""

while 1:
    try:
        # start receiving data from the client
        print("Ready to serve...")

        tcpCliSock, addr = tcpSerSock.accept()
        print("Received a connection from:", addr)

        message = tcpCliSock.recv(1024).decode()

        # Extract the filename from the given message
        if len(message) > 1:
            filename = message.split()[1].partition("/")[2]
            print("Filename =", filename)

        fileExist = False
        isDomain = False
        searchFile = ""

        if filename.startswith("www."):
            domainName = filename
            isDomain = True
            print(f"domainName = {domainName}")
        else:
            searchFile = filename.strip('/')
            print(f"searchFile = {searchFile}")
        try:
            if isDomain:
                file_path = os.path.join("./Lab 03/cache/", domainName + "/" + domainName)
            else:
                file_path = os.path.join("./Lab 03/cache/", domainName + "/" + filename + filename.strip("/"))
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
                    if isDomain:
                        file_path = os.path.join("./Lab 03/cache/", domainName + "/" + domainName)
                    else:
                        file_path = os.path.join("./Lab 03/cache/", domainName + "/" + filename + filename.strip("/"))

                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Write the response to the cache file
                    # Also send the response in the buffer to client socket and the corresponding file in the cache
                    with open(f"{file_path}", "wb") as f:
                        for line in buff:
                            f.write(line)
                            tcpCliSock.send(line)
                except Exception as e:
                    print("Illegal request:", e)
                
                c.close()

            else:
                tcpCliSock.send("HTTP/1.0 400 Bad Request\r\n".encode())

    except ConnectionAbortedError as e:
        print(e, "Retrying...")
        continue

    # Close the client and the server sockets
    print()
    tcpCliSock.close()

tcpSerSock.close()