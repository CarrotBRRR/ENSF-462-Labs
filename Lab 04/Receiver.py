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
    while True:
        # try to receive message before timeout
        rcvPkt = rdt.rdt_3_0_receive()
        if rcvPkt is None:
            if time_of_last_data + timeout < time.time():
                print("Timeout: No more data. Closing connection.")
                break
            else:
                continue
        time_of_last_data = time.time()
        if rcvPkt == True:
            print(
                f"Corruption detected! Sending ACK {rdt.seq_num - 1}\n"
            )
            rdt.rdt_3_0_send(str(rdt.seq_num - 1))
        else:
            print(
                f"Receive message {rcvPkt.seq_num}. Send ACK {rdt.seq_num}\n"
            )
            rdt.rdt_3_0_send(str(rcvPkt.seq_num))
            if rcvPkt.seq_num == rdt.seq_num:
                rdt.seq_num += 1

    rdt.disconnect()