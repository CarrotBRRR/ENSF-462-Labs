import argparse
import RDT
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uppercase conversion receiver.")
    parser.add_argument("port", help="Port.", type=int)
    args = parser.parse_args()

    timeout = 10  # close connection if no new data within 5 seconds
    time_of_last_data = time.time()

    rdt = RDT.RDT("receiver", None, args.port)
    expected_seq_num = 1

    while True:
        msg_S = rdt.rdt_3_0_receive()

        if msg_S is None:
            if time_of_last_data + timeout < time.time():
                break
            else:
                continue
        time_of_last_data = time.time()

        # reply back the message
        print(f"Reply: {msg_S}\n")

    rdt.disconnect()
