# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #1

from packet import Packet
from threading import Thread
import time


class Read(Thread):

    def __init__(self, socket, read_request, rcv_queue):

        Thread.__init__(self)

        self.rcv_queue = rcv_queue
        self.socket = socket

        # make client address tuple
        self.client = (read_request[1][0], read_request[1][1])

        # extract file name from first packet
        file_name = Packet.get_file_name(read_request[0])

        # open file to be read/written from
        self.file = open(file_name, 'rb')

        # timeout + retransmission variables
        self.block_num = 1
        self.last_pkt = bytearray()
        self.last_pkt_made = False
        self.time_sent = 0

    def run(self):

        # make + send first DATA packet
        self.send_data()

        while True:

            # retransmit last packet on short timeout
            if time.time() - self.time_sent > 0.1:
                self.socket.sendto(self.last_pkt, self.client)
            # terminate connection on long timeout
            elif time.time() - self.time_sent > 1:
                break

            if not self.rcv_queue.empty():

                # receive a new packet
                packet_received = (self.rcv_queue.get())[0]

                # if packet is a ACK packet (op code = 4)
                if int.from_bytes(packet_received[0:2], 'big') == 4:

                    # if ACK block number is correct, send new packet
                    if int.from_bytes(packet_received[2:4], 'big') != (self.block_num - 1):
                        self.socket.sendto(self.last_pkt, self.client)
                        self.time_sent = time.time()

                    else:

                        # make + send DATA packet
                        self.send_data()

                        # exit loop if last packet has been sent
                        if self.last_pkt_made:
                            break

                # if packet is an ERROR packet (op code = 5)
                if int.from_bytes(packet_received[0:2], 'big') == 5:
                    break

            time.sleep(0.02)

        # Close file, client socket, and terminate program
        self.file.close()

    def send_data(self):

        # make + send DATA packet
        data_array = bytearray(self.file.read(512))
        data_header = Packet.make_data_header(self.block_num)
        data_packet = data_header + data_array
        self.socket.sendto(data_packet, self.client)
        self.time_sent = time.time()
        self.last_pkt = data_packet

        # update DATA block number
        self.block_num += 1
        if len(data_array) < 512:
            self.last_pkt_made = True
