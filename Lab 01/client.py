import socket as s

def main():
    server_host = "localhost"
    server_port = 12345

    user1_name = input("Enter your name (user 1): ")

    client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    client_socket.send(user1_name.encode())

    user2_name = client_socket.recv(1024).decode()

    print(f"Connected to {user2_name}")

    while True:
        message = input(f"{user1_name}: ")
        client_socket.send(message.encode())

        if message.lower() == "bye":
            break

        reply = client_socket.recv(1024).decode()
        print(f"{user2_name}: {reply}")

        if reply.lower() == "bye":
            break

    print("Chat ended!")
    client_socket.close()
    print("Connection Closed!")

if __name__ == "__main__":
    main()
