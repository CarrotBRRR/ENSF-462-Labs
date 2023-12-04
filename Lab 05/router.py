import socket
import threading
import time
import sys
import json

# Constants
INFINITY = 999


def load_config(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    total_nodes = int(lines[0].strip())
    neighbors = []

    for line in lines[1:]:
        parts = line.strip().split()

        if len(parts) == 4:
            neighbor_info = {
                "label": parts[0],
                "id": int(parts[1]),
                "cost": int(parts[2]),
                "port": int(parts[3]),
            }
            neighbors.append(neighbor_info)
        elif line.strip():  # Check if line is not just empty or spaces
            print(f"Skipping invalid line: {line.strip()}")

    return total_nodes, neighbors



def dijkstra(graph, source):
    distance = {node: INFINITY for node in range(len(graph))}
    previous = {node: None for node in range(len(graph))}
    distance[source] = 0
    unvisited = set(range(len(graph)))

    while unvisited:
        current_node = min(unvisited, key=lambda node: distance[node])
        unvisited.remove(current_node)

        for neighbor_info in graph[current_node]:
            neighbor, cost = neighbor_info["id"], neighbor_info["cost"]
            tentative_value = distance[current_node] + cost
            if tentative_value < distance[neighbor]:
                distance[neighbor] = tentative_value
                previous[neighbor] = current_node

    return distance, previous


def send_udp(message, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(message.encode(), (host, port))


def receive_udp(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("", port))
        message, _ = s.recvfrom(1024)
    return message.decode()


def send_link_state(router_id, port, neighbors):
    while True:
        message = json.dumps({"id": router_id, "neighbors": neighbors})
        for neighbor in neighbors:
            send_udp(message, "localhost", neighbor["port"])
        time.sleep(1)


def receive_and_broadcast_link_state(port, neighbors, link_state):
    while True:
        message = receive_udp(port)
        data = json.loads(message)
        link_state[data["id"]] = data["neighbors"]
        for neighbor in neighbors:
            send_udp(message, "localhost", neighbor["port"])
        time.sleep(1)



def print_routing_table(router_id, distance, previous, total_nodes):
    router_label = chr(router_id + ord("A"))

    # Print Dijkstra's output
    print("Destination_Routerid Distance Previous_node_id")
    for destination in range(total_nodes):
        # Print the current router with a Previous_node_id of its own ID
        if destination == router_id:
            print(f"{destination:<20} {0:<8} {router_id}")
        else:
            prev_node_id = (
                previous[destination] if previous[destination] is not None else "-"
            )
            print(f"{destination:<20} {distance[destination]:<8} {prev_node_id}")

    # Print the forwarding table
    print(f"\nThe forwarding table in {router_label} is printed as follows:")
    print("Destination_Routerid Next_hop_routerlabel")
    for destination in range(total_nodes):
        if destination != router_id:
            next_hop = previous[destination]
            if next_hop == router_id:
                next_hop_label = chr(
                    destination + ord("A")
                )  # Direct connection, use the destination label
            else:
                # Find the first hop on the least cost path to the destination
                while (
                    previous[next_hop] is not None and previous[next_hop] != router_id
                ):
                    next_hop = previous[next_hop]
                next_hop_label = (
                    chr(next_hop + ord("A")) if next_hop is not None else "None"
                )
            print(f"{destination:<20} {next_hop_label}")


def main(router_id, router_port, config_file):
    total_nodes, neighbors = load_config(config_file)
    link_state = {router_id: neighbors}  # Initialize with self neighbors

    # Threads for each component
    send_thread = threading.Thread(
        target=send_link_state, args=(router_id, router_port, neighbors)
    )
    receive_thread = threading.Thread(
        target=receive_and_broadcast_link_state,
        args=(router_port, neighbors, link_state),
    )

    send_thread.start()
    receive_thread.start()

    while True:
        if len(link_state) == total_nodes:
            distance, previous = dijkstra(link_state, router_id)
            print_routing_table(router_id, distance, previous, total_nodes)
        time.sleep(10)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python Router.py <router_id> <router_port> <config_file>")
        sys.exit(1)
    router_id = int(sys.argv[1])
    router_port = int(sys.argv[2])
    config_file = sys.argv[3]

    main(router_id, router_port, config_file)
