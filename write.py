# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #1

from packet import Packet
from threading import Thread
import time


class Write(Thread):

    def __init__(self, socket, write_request, rcv_queue):

        Thread.__init__(self)

        self.rcv_queue = rcv_queue
        self.socket = socket

        # make client address tuple
        self.client = (write_request[1][0], write_request[1][1])

        # extract file name from first packet
        file_name = Packet.get_file_name(write_request[0])

        # open file to be read/written from
        self.file = open(file_name, 'rb')

        # timeout + retransmission variables
        self.last_ack = bytearray()
        self.time_sent = 0

    def run(self):

        # keep track of anticipated block numbers
        next_block_num = 1

        # enter loop of receiving DATA packets
        while True:

            # retransmit last packet on short timeout
            if time.time() - self.time_sent > 0.1:
                self.socket.sendto(self.last_ack, self.client)
            # terminate connection on long timeout
            elif time.time() - self.time_sent > 1:
                break

            if not self.rcv_queue.empty():

                packet_received = (self.rcv_queue.get())[0]

                # if packet is a DATA packet (op code = 3)
                if Packet.get_op_code(packet_received) == 3:

                    # if DATA packet's block number is old, send last ACK
                    if int.from_bytes(packet_received[2:4], 'big') != next_block_num:
                        self.socket.sendto(self.last_ack, self.client)
                        self.time_sent = time.time()

                    else:

                        # make + send new ACK packet
                        ack = Packet.make_ack(next_block_num)
                        self.last_ack = ack
                        self.socket.sendto(self.last_ack, self.client)
                        self.time_sent = time.time()
                        next_block_num += 1

                        # write data from packet to file, exit if too much data
                        if len(packet_received) > 516:
                            break
                        elif len(packet_received) <= 516:
                            data = packet_received[4:len(packet_received)]
                            self.file.write(data)

                # if this is the last DATA packet, break loop
                if len(packet_received) < 516:
                    break

                # if packet is an ERROR packet (op code = 5)
                if Packet.get_op_code(packet_received) == 5:
                    break

            time.sleep(0.02)

        # Close file, client socket, terminate program
        self.file.close()

