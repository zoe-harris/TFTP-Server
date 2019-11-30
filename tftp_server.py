# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3

import argparse
import sys
from session_manager import SessionManager

# make parser using argParse()
parser = argparse.ArgumentParser()
parser.add_argument('-sp')  # Server Port Number

# store IP address, file name, and port numbers
args = parser.parse_args()
server_port = int(args.sp)

# if either port number out of range, program terminates
if server_port < 5000 or server_port > 65535:
    sys.exit("ERROR: argParse value for server port is out of range (<5000, >65535)")

s = SessionManager(server_port)
s.run_manager()
