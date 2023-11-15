import argparse
import socket
import threading
from time import sleep
import random
import RDT

class NetworkLayer:
    prob_pkt_loss = .2
    prob_byte_corr = .1
    prob_pkt_reorder = 0

    sock = None
    conn = None
    buffer_S = ""
    lock = threading.Lock()
    collect_thread = None
    stop = None
    socket_timeout = 0.1
    reorder_msg_S = None

    def __init__(self, role_S, receiver_S, port):
        if role_S == "sender":
            print("Network: role is sender")
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((receiver_S, port))
            self.conn.settimeout(self.socket_timeout)

        elif role_S == "receiver":
            print("Network: role is receiver")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(("localhost", port))
            self.sock.listen(1)
            self.conn, addr = self.sock.accept()
            self.conn.settimeout(self.socket_timeout)

        self.collect_thread = threading.Thread(name="Collector", target=self.collect)
        self.stop = False
        self.collect_thread.start()

    def disconnect(self):
        if self.collect_thread:
            self.stop = True
            self.collect_thread.join()

    def __del__(self):
        if self.sock is not None:
            self.sock.close()
        if self.conn is not None:
            self.conn.close()

    def udt_send(self, msg_S):
        if random.random() < self.prob_pkt_loss:
            return

        if random.random() < self.prob_byte_corr:
            start = random.randint(RDT.Packet.length_S_length, len(msg_S) - 5)
            num = random.randint(1, 5)
            repl_S = "".join(random.sample("XXXXX", num))
            msg_S = msg_S[:start] + repl_S + msg_S[start + num :]

        if random.random() < self.prob_pkt_reorder or self.reorder_msg_S:
            if self.reorder_msg_S is None:
                self.reorder_msg_S = msg_S
                return None
            else:
                msg_S += self.reorder_msg_S
                self.reorder_msg_S = None

        totalsent = 0
        while totalsent < len(msg_S):
            sent = self.conn.send(msg_S[totalsent:].encode("utf-8"))
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def collect(self):
        while True:
            try:
                recv_bytes = self.conn.recv(4096)
                with self.lock:
                    self.buffer_S += recv_bytes.decode("utf-8")
            except socket.timeout as err:
                pass
            if self.stop:
                return

    def udt_receive(self):
        with self.lock:
            ret_S = self.buffer_S
            self.buffer_S = ""
        return ret_S

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network layer implementation.")
    parser.add_argument("role", choices=["sender", "receiver"])
    parser.add_argument("receiver")
    parser.add_argument("port", type=int)
    args = parser.parse_args()

    network = NetworkLayer(args.role, args.receiver, args.port)
    if args.role == "sender":
        network.udt_send("MSG_FROM_SENDER")
        sleep(2)
        print(network.udt_receive())
        network.disconnect()

    else:
        sleep(1)
        print(network.udt_receive())
        network.udt_send("MSG_FROM_RECEIVER")
        network.disconnect()
