# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3

import threading
from packet import Packet
import sys
from socket import *
from session import Session


class SessionManager:

    def __init__(self, server_port):

        # make + bind server socket
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', server_port))

        # dictionary tracks TIDs associated with existing threads
        self.threadIDs = {}
        # dictionary holds a lock for each thread's TID
        self.threadLocks = {}

        self.shutting_down = False

    def run_manager(self):

        while True:

            # check whether time to exit program
            if self.shutting_down is True and len(self.threadIDs) == 0:
                self.server_socket.close()
                sys.exit()

            # receive new packet
            pkt = self.server_socket.recvfrom(1024)

            # check if RRQ for shutdown.txt
            if Packet.get_op_code(pkt) == 1:
                if int.from_bytes(pkt[0:2], 'big') == 1:

                    file_name = Packet.get_file_name(pkt)

                    if file_name is "shutdown.txt":

                        if len(self.threadIDs) == 0:
                            self.server_socket.close()
                            sys.exit()
                        else:
                            self.shutting_down = True

            # if not RRQ or WRQ and known TID, forward packet to thread
            pkt_op_code = Packet.get_op_code(pkt)
            if pkt_op_code != 1 and pkt_op_code != 2:
                if pkt[1][1] in self.threadIDs:
                    print("Forward packet to correct thread")
                    # FIXME: forward pkt to correct thread

            # else if RRQ or WRQ and not shutting down, start a new thread
            else:

                if self.shutting_down is False:
                    # create new session + add to list
                    new_session = Session(pkt)
                    self.threadIDs[pkt[1][1]] = new_session
                    # start new thread for this session
                    new_thread = threading.Thread(target=new_session.run())
                    new_thread.start()
