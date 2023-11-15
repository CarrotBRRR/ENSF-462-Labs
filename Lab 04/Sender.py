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
    for msg_S in msg_L:
        resendMessage = msg_S
        rdt.rdt_3_0_send(msg_S)
        # try to receive message before timeout
        rcvPkt = None
        while rcvPkt == None:
            rcvPkt = rdt.rdt_3_0_receive()
            if rcvPkt is None:
                # If timeout occurs resend message
                if time_of_last_data + timeout < time.time():
                    rdt.rdt_3_0_send(resendMessage, True)
                    time_of_last_data = time.time()
                else:
                    continue
            elif rcvPkt == True:
                rcvPkt = None
            elif rcvPkt:
                if int(rcvPkt.msg_S) != rdt.seq_num:
                    print(
                        f"Receive ACK {rcvPkt.msg_S}. Resend message {rdt.seq_num}"
                    )
                    rdt.rdt_3_0_send(resendMessage)
                    rcvPkt = None

        time_of_last_data = time.time()

        # print the result
        if rcvPkt:
            print(
                f"Receive ACK {rcvPkt.seq_num}. Message successfully sent!\n"
            )
            rdt.seq_num += 1
    rdt.disconnect()