# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3

from socket import *
from packet import Packet
import time
import queue
from threading import *


class Session(Thread):

    def __init__(self, first_pkt, rcv_queue):

        Thread.__init__(self)

        self.rcv_queue = rcv_queue
        self.send_pkt = None

        # set pkt to first pkt received
        self.pkt = first_pkt

        # extract file name from first packet
        file_name = Packet.get_file_name(self.pkt[0])

        # make client address tuple
        self.client = (self.pkt[1][0], self.pkt[1][1])

        # open file to be read/written from
        self.file = open(file_name, 'rb')

        # retransmission variables
        self.time_sent = time.time()
        self.last_pkt = bytearray()

        # track ack and block numbers
        self.ack_num = 0
        self.block_num = 0

        # determine end of transmission
        self.last_pkt_made = False
        self.last_ack_num = None

    """ RUN EITHER READ OR WRITE MODE"""

    def run(self):

        # if RRQ, initiate read mode
        if Packet.get_op_code(self.pkt) == 1:
            self.read_mode()
        # if WRQ, initiate write mode
        elif Packet.get_op_code(self.pkt) == 2:
            self.write_mode()

    """ RUNS IN RESPONSE TO READ REQUEST """

    def read_mode(self):

        while True:

            # retransmit on short timeout
            if self.short_timeout():
                self.send_pkt = self.last_pkt

            # terminate on long timeout
            if self.long_timeout():
                break

            # receive new packet
            if not self.rcv_queue.empty():

                pkt = (self.rcv_queue.get())[0]

                # terminate if ERROR packet
                if Packet.get_op_code(pkt) == 5:
                    self.terminate()

                # if ACK packet, send DATA packet
                if Packet.get_op_code(pkt) == 4:

                    # send new DATA packet if correct ACK number
                    if Packet.get_block_num(pkt) == self.block_num - 1:
                        if not self.last_pkt_made:
                            self.send_data()
                    else:
                        self.send_pkt = self.last_pkt

                # check if ACK is for final DATA packet
                if Packet.get_block_num(pkt) == self.last_ack_num - 1:
                    break

        # terminate the connection
        self.terminate()

    """ RUNS IN RESPONSE TO WRITE REQUEST """

    def write_mode(self):

        while True:

            # retransmit on short timeout
            if self.short_timeout():
                self.send_pkt = self.last_pkt

            # terminate on long timeout
            if self.long_timeout():
                break

            # receive new packet
            if not self.rcv_queue.empty():

                pkt = (self.rcv_queue.get())[0]

                # terminate if ERROR packet
                if Packet.get_op_code(pkt) == 5:
                    self.terminate()

                # if DATA packet, send ACK packet
                if Packet.get_op_code(pkt) == 3:
                    # FIXME: Forward pkt to SessionManager
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
        data_pkt = Packet.make_data(self.block_num, data)
        self.send_pkt = data_pkt

        # if this was the last of the data
        if len(data) < 512:
            self.last_pkt_made = True
            self.last_ack_num = self.block_num

        # update time sent, last packet, and block number
        self.time_sent = time.time()
        self.last_pkt = data_pkt
        self.block_num += 1

    def send_ack(self):

        # make + send new ACK
        ack = Packet.make_ack(self.block_num + 1)
        self.last_pkt = ack
        self.send_pkt = ack

        # update expected block number
        self.block_num += 1
        self.time_sent = time.time()

    """ TIMEOUT AND TERMINATION """

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
