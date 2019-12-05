# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3

from packet import Packet
import sys
from socket import *
from queue import Queue
from write import Write
from read import Read


class SessionManager:

    def __init__(self, server_port):

        # make + bind server socket
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', server_port))
        self.server_socket.settimeout(0.00001)

        # dictionary tracks TIDs associated with existing threads
        self.TIDs = {}
        self.threads = list()

        # variable is set on receiving shutdown.txt
        self.shutting_down = False

    def run_manager(self):

        while True:

            # check whether time to exit program
            if self.shutting_down is True and len(self.threads) == 0:
                self.server_socket.close()
                sys.exit()

            # receive new packet from client
            try:
                pkt = self.server_socket.recvfrom(1024)

                # extract op code and file name from packet
                pkt_op_code = Packet.get_op_code(pkt[0])

                # check if packet is RRQ for shutdown.txt
                if pkt_op_code == 1 or pkt_op_code == 2:

                    pkt_file_name = Packet.get_file_name(pkt[0])

                    if pkt_file_name == "shutdown.txt":

                        print("Received shutdown.txt")

                        # if no existing threads, shut down immediately
                        if len(self.threads) == 0:
                            self.server_socket.close()
                            sys.exit()

                        # else, need finish out existing threads
                        else:
                            self.shutting_down = True

                # if not a read or write request
                if pkt_op_code != 1 and pkt_op_code != 2:

                    for thread in self.threads:
                        if thread[0] == pkt[1][1]:
                            thread[1].rcv_queue.put(pkt)

                # if RRQ or WRQ and not shutting down
                if (pkt_op_code == 1 or pkt_op_code == 2) and not self.shutting_down:

                    # if op code == 2, start session in write mode
                    if pkt_op_code == 2:

                        # make + start new write session thread
                        new_thread = Write(self.server_socket, pkt, Queue())
                        new_thread.start()

                        # add thread / TID pair to threads list
                        self.threads.append([pkt[1][1], new_thread])

                    # if op code == 1, start session in read mode
                    else:

                        # make + start new read session thread
                        new_thread = Read(self.server_socket, pkt, Queue())
                        new_thread.start()
                        print("Starting new thread")

                        # add thread / TID pair to threads list
                        self.threads.append([pkt[1][1], new_thread])

            except timeout:
                print("", end="")


