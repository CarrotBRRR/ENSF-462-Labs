import socket as s

def main():
    server_host = "localhost"
    server_port = 12345

    user2_name = input("Enter your name (user 2): ")

    server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen(1)

    print("Listening for connections...")

    client_socket, client_address = server_socket.accept()
    user1_name = client_socket.recv(1024).decode()

    print(f"Connected to {user1_name}")

    client_socket.send(user2_name.encode())

    while True:
        message = client_socket.recv(1024).decode()
        print(f"{user1_name}: {message}")

        if message.lower() == "bye":
            break

        reply = input(f"{user2_name}: ")
        client_socket.send(reply.encode())

        if reply.lower() == "bye":
            break

    print("Chat ended!")
    client_socket.close()
    server_socket.close()
    print("Conection closed!")

if __name__ == "__main__":
    main()
