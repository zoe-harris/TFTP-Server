# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #1

from packet import Packet
from threading import Thread
from queue import Queue


class Read(Thread):

    def __init__(self, read_request, rcv_queue, snd_queue):

        Thread.__init__(self)

        self.rcv_queue = rcv_queue
        self.snd_queue = snd_queue

        # make client address tuple
        self.client = (read_request[1][0], read_request[1][1])

        # extract file name from first packet
        file_name = Packet.get_file_name(read_request[0])

        # open file to be read/written from
        self.file = open(file_name, 'rb')

    def run(self):

        # make Packets object
        p = Packet()

        # initialize DATA block number
        block_num = 1
        last_packet = bytearray()

        while True:

            if not self.rcv_queue.empty():

                packet_received = (self.rcv_queue.get())[0]

                # if packet is a ACK packet (op code = 4)
                if int.from_bytes(packet_received[0:2], 'big') == 4:

                    # if ACK block number is correct, send new packet
                    if int.from_bytes(packet_received[2:4], 'big') != (block_num - 1):
                        # FIXME: Sending packet?
                        self.snd_queue.put([last_packet, self.client])

                    else:

                        # make + send DATA packet
                        data_array = bytearray(self.file.read(512))
                        data_header = p.make_data_header(block_num)
                        data_packet = data_header + data_array
                        # FIXME: Sending packet?
                        self.snd_queue.put([data_packet, self.client])
                        last_packet = data_packet

                        # update DATA block number
                        block_num += 1

                        # exit loop if last packet has been sent
                        if len(data_array) < 512:
                            break

                # if packet is an ERROR packet (op code = 5)
                if int.from_bytes(packet_received[0:2], 'big') == 5:
                    break

        # Close file, client socket, and terminate program
        self.file.close()

