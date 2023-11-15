import Network
import argparse
import time
from time import sleep
import hashlib

class Packet:
    seq_num_S_length = 10
    length_S_length = 10
    checksum_length = 32

    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S

    @classmethod
    def from_byte_S(cls, byte_S):
        if cls.corrupt(byte_S):
            raise RuntimeError("Cannot initialize Packet: byte_S is corrupt")

        seq_num = int(
            byte_S[
                cls.length_S_length : cls.length_S_length + cls.seq_num_S_length
            ]
        )
        msg_S = byte_S[
            cls.length_S_length + cls.seq_num_S_length + cls.checksum_length :
        ]
        return cls(seq_num, msg_S)

    def get_byte_S(self):
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        length_S = str(
            self.length_S_length
            + len(seq_num_S)
            + self.checksum_length
            + len(self.msg_S)
        ).zfill(self.length_S_length)

        checksum = hashlib.md5((length_S + seq_num_S + self.msg_S).encode("utf-8"))
        checksum_S = checksum.hexdigest()

        return length_S + seq_num_S + checksum_S + self.msg_S

    @staticmethod
    def corrupt(byte_S):
        length_S = byte_S[0 : Packet.length_S_length]
        seq_num_S = byte_S[
            Packet.length_S_length : Packet.seq_num_S_length + Packet.seq_num_S_length
        ]
        checksum_S = byte_S[
            Packet.seq_num_S_length
            + Packet.seq_num_S_length : Packet.seq_num_S_length
            + Packet.length_S_length
            + Packet.checksum_length
        ]
        msg_S = byte_S[
            Packet.seq_num_S_length + Packet.seq_num_S_length + Packet.checksum_length :
        ]

        checksum = hashlib.md5(str(length_S + seq_num_S + msg_S).encode("utf-8"))
        computed_checksum_S = checksum.hexdigest()

        return checksum_S != computed_checksum_S


class RDT:
    byte_buffer = ""
    ack_seq_num = 0

    timeout = 10

    def __init__(self, role_S, receiver_S, port):
        self.network = Network.NetworkLayer(role_S, receiver_S, port)
        self.seq_num = 1

    def disconnect(self):
        self.network.disconnect()

    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())

    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S

        while True:
            if len(self.byte_buffer) < Packet.length_S_length:
                return ret_S
            length = int(self.byte_buffer[: Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S

            p = Packet.from_byte_S(self.byte_buffer[0:length])
            ret_S = p.msg_S if (ret_S is None) else ret_S
            self.byte_buffer = self.byte_buffer[length:]


    def rdt_3_0_send(self, message, seq_num):
        print(f"Send message seq_num {seq_num}")

        p = Packet(seq_num, message)
        current_seq = seq_num

        while current_seq == seq_num:
            self.network.udt_send(p.get_byte_S())
            ack = ''
            timer = time.time()

            while ack == '' and timer + self.timeout > time.time():
                ack = self.network.udt_receive()

            if timer + self.timeout <= time.time():
                msg_length = int(ack[:Packet.length_S_length])
                self.byte_buffer = ack[msg_length:]

                if not Packet.corrupt(ack[:msg_length]):
                    ack_p = Packet.from_byte_S(ack[:msg_length])

                    if ack_p.seq_num == seq_num:
                        print(f"Received ACK {ack_p.seq_num}. Message successfully sent!")
                        break
                    else:
                        print(f"Received ACK {ack_p.seq_num}. Resend message seq_num {seq_num}")
                        self.rdt_1_0_send(message)
                else:
                    print(f"Corruption detected in ACK. Resend message {seq_num}")
                    self.byte_buffer = ''
                
            else:
                print(f"Timeout! Resend message seq_num {seq_num}")
                self.rdt_1_0_send(message)


    def rdt_3_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S

        if len(self.byte_buffer) < Packet.length_S_length:
            return ret_S
        length = int(self.byte_buffer[: Packet.length_S_length])
        if len(self.byte_buffer) < length:
            return ret_S
        current_seq = self.seq_num

        if Packet.corrupt(self.byte_buffer):
            # Send a NAK
            print(f"Corruption detected! Send ACK {self.ack_seq_num}")
            ack = Packet(self.seq_num, "0")
            self.network.udt_send(ack.get_byte_S())

        else:
            # create packet from buffer content
            print(f"Receive message {current_seq}. Send ACK {self.seq_num}")
            p = Packet.from_byte_S(self.byte_buffer[0:length])

            ack = Packet(self.seq_num, "1")
            self.network.udt_send(ack.get_byte_S())
    
            self.seq_num += 1
            # Add contents to return string
            ret_S = p.msg_S if (ret_S is None) else ret_S
        # remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
        # if this was the last packet, will return on the next iteration
        return ret_S
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RDT implementation.")
    parser.add_argument(
        "role",
        help="Role is either sender or receiver.",
        choices=["sender", "receiver"],
    )
    parser.add_argument("receiver", help="receiver.")
    parser.add_argument("port", help="Port.", type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.receiver, args.port)
    if args.role == "sender":
        rdt.rdt_3_0_send("MSG_FROM_SENDER", 1)
        sleep(2)
        print(rdt.rdt_3_0_receive())
        rdt.disconnect()

    else:
        sleep(1)
        print(rdt.rdt_3_0_receive())
        rdt.rdt_3_0_send("MSG_FROM_RECEIVER", 1)
        rdt.disconnect()
