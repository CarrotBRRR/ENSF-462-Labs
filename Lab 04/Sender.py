import argparse
import RDT
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Quotation sender talking to a receiver."
    )
    parser.add_argument("receiver", help="receiver.")
    parser.add_argument("port", help="Port.", type=int)
    args = parser.parse_args()

    msg_L = [
        "sending message - 1",
        "sending message - 2",
        "sending message - 3",
        "sending message - 4",
        "sending message - 5",
        "sending message - 6",
        "sending message - 7",
        "sending message - 8",
        "sending message - 9",
        "sending message - 10",
    ]

    timeout = 2  # send the next message if no response
    time_of_last_data = time.time()

    rdt = RDT.RDT("sender", args.receiver, args.port)
    seq_num = 0

    for msg_S in msg_L:
        seq_num += 1
        rdt.rdt_3_0_send(msg_S, seq_num)

    rdt.disconnect()
