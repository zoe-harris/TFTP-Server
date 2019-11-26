# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3

from socket import *
import sys
from packet import Packet
import time


class Session:

    def __init__(self, ip_address, file_name, server_port, client_port):

        # constructor variables
        self.ip_address = ip_address
        self.file_name = file_name
        self.server_port = server_port
        self.client_port = client_port

        # client address tuple
        self.client = (self.ip_address, self.client_port)

        # open file to be read/written from
        self.file = open(self.file_name, 'rb')

        # create client socket + bind to client port
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', self.server_port))

        # packet maker
        self.p = Packet()

        # retransmission variables
        self.time_sent = time.time()
        self.last_pkt = bytearray()

        # track ack and block number
        self.ack_num = 0
        self.block_num = 0
        self.next_block_num = 1

        # determine end of transmission
        self.last_pkt_made = False
        self.last_ack_num = None

    def run(self):

        # receive first packet
        pkt = self.server_socket.recvfrom(1024)

        # if RRQ, initiate read mode
        if int.from_bytes(pkt[0:2], 'big') == 1:
            self.read_mode()
        # if WRQ, initiate write mode
        elif int.from_bytes(pkt[0:2], 'big') == 2:
            self.write_mode()

    """ RUNS IN RESPONSE TO READ REQUEST """

    def read_mode(self):

        while True:

            # retransmit on short timeout
            if self.short_timeout():
                self.server_socket.sendto(self.last_pkt, self.client)

            # terminate on long timeout
            if self.long_timeout():
                break

            # receive new packet
            pkt = self.server_socket.recvfrom(1024)

            # check TID
            if pkt[1][1] == self.client_port:
                pkt = pkt[0]

                # terminate if ERROR packet
                if self.p.op_code(pkt) == 5:
                    self.terminate()

                # if ACK packet, send DATA packet
                if self.p.op_code(pkt) == 4:

                    # send new DATA packet if correct ACK number
                    if self.p.get_block_num(pkt) == self.block_num - 1:
                        if not self.last_pkt_made:
                            self.send_data()
                    else:
                        # retransmit last packet if incorrect ACK number
                        self.server_socket.sendto(self.last_pkt, self.client)

                # check if ACK is for final DATA packet
                if self.p.get_block_num(pkt) == self.last_ack_num - 1:
                    break

        # terminate the connection
        self.terminate()

    """ RUNS IN RESPONSE TO WRITE REQUEST """

    def write_mode(self):

        while True:

            # retransmit on short timeout
            if self.short_timeout():
                self.server_socket.sendto(self.last_pkt, self.client)

            # terminate on long timeout
            if self.long_timeout():
                break

            # receive new packet
            pkt = self.server_socket.recvfrom(1024)

            # check TID
            if pkt[1][1] == self.client_port:
                pkt = pkt[0]

                # terminate if ERROR packet
                if self.p.op_code(pkt) == 5:
                    self.terminate()

                # if DATA packet, send ACK packet
                if self.p.op_code(pkt) == 3:
                    self.send_ack()

                # write data from pkt to file
                if len(pkt) > 516:
                    break
                elif len(pkt) <= 516:
                    data = pkt[4:len(pkt)]
                    self.file.write(data)

                # terminate if data < 516 bytes
                if len(pkt) < 516:
                    break

        # terminate connection
        self.terminate()

    """ METHODS FOR TRANSFER PROTOCOL EVENTS """

    def send_data(self):

        # make + send new packet
        data = bytearray(self.file.read(512))
        pkt = self.p.make_data(self.block_num, data)
        self.server_socket.sendto(pkt, self.client)

        # if this was the last of the data
        if len(data) < 512:
            self.last_pkt_made = True
            self.last_ack_num = self.block_num

        # update time sent, last packet, and block number
        self.time_sent = time.time()
        self.last_pkt = pkt
        self.block_num += 1

    def send_ack(self):

        # make + send new ACK
        ack = self.p.make_ack(self.next_block_num)
        self.last_pkt = ack
        self.server_socket.sendto(ack, self.client)

        # update expected block number
        self.next_block_num += 1
        self.time_sent = time.time()

    def short_timeout(self):

        # short timeout = 1/10th second
        if time.time() - self.time_sent > 0.1:
            return True

    def long_timeout(self):

        # long timeout = 1 second
        if time.time() - self.time_sent > 1:
            return True

    def terminate(self):

        # close open file + socket before exit
        self.file.close()
        self.server_socket.close()
        sys.exit()
