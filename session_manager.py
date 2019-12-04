# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3

import threading
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

        # dictionary tracks TIDs associated with existing threads
        self.threadIDs = {}
        self.threads = list()

        # variable is set on receiving shutdown.txt
        self.shutting_down = False

    def run_manager(self):

        while True:

            # check whether time to exit program
            if self.shutting_down is True and len(self.threadIDs) == 0:
                self.server_socket.close()
                sys.exit()

            # receive new packet from client
            pkt = self.server_socket.recvfrom(1024)

            # check if packet is RRQ for shutdown.txt
            if Packet.get_op_code(pkt) == 1 and Packet.get_file_name(pkt) is "shutdown.txr":

                # if no existing threads, shut down immediately
                if len(self.threads) == 0:
                    self.server_socket.close()
                    sys.exit()

                # else, need finish out existing threads
                else:
                    self.shutting_down = True

            # if not a read or write request
            pkt_op_code = Packet.get_op_code(pkt)
            if pkt_op_code != 1 and pkt_op_code != 2:

                # if packet has a known TID
                if pkt[1][1] in self.threadIDs:

                    # add packet to receive queue of correct thread
                    self.threadIDs.get(pkt[1][1]).recv_queue.put(pkt)

            # if RRQ or WRQ and not shutting down
            if (pkt_op_code == 1 or pkt_op_code == 2) and not self.shutting_down:

                # make new send and receive queues
                rcv_queue = Queue()
                snd_queue = Queue()

                # if op code == 2, start session in write mode
                if Packet.get_op_code(pkt) == 2:
                    new_session = Write(pkt, rcv_queue, snd_queue)
                # if op code == 1, start session in read mode
                else:
                    new_session = Read(pkt, rcv_queue, snd_queue)

                # make + start new thread using new session
                new_thread = threading.Thread(target=new_session.run())
                new_thread.start()

                # add thread / TID pair to dictionary + thread to list
                self.threadIDs[pkt[1][1]] = new_thread
                self.threads.append(new_thread)

            # check send queues of threads + send packets as needed
            for thread in self.threads:
                if not thread.snd_queue.empty():
                    snd_pkt = thread.snd_queue.get()
                    self.server_socket.sendto(snd_pkt[0], snd_pkt[1])


