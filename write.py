# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #1

from packet import Packet
from threading import Thread


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

    def run(self):

        # make Packet object
        p = Packet()

        # keep track of anticipated block numbers
        next_block_num = 1
        last_ack = bytearray()

        # enter loop of receiving DATA packets
        while True:

            if not self.rcv_queue.empty():

                packet_received = (self.rcv_queue.get())[0]

                # if packet is a DATA packet (op code = 3)
                if int.from_bytes(packet_received[0:2], 'big') == 3:

                    # if DATA packet's block number is old, send last ACK
                    if int.from_bytes(packet_received[2:4], 'big') != next_block_num:
                        self.socket.sendto(last_ack, self.client)

                    else:

                        # make + send new ACK packet
                        ack = p.make_ack(next_block_num)
                        last_ack = ack
                        self.socket.sendto(last_ack, self.client)
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
                if int.from_bytes(packet_received[0:2], 'big') == 5:
                    break

        # Close file, client socket, terminate program
        self.file.close()

