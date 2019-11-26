# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3

import argparse
import sys


# make parser using argParse()
parser = argparse.ArgumentParser()
parser.add_argument('-a')  # IP Address
parser.add_argument('-cp')  # Client Port Number
parser.add_argument('-sp')  # Server Port Number
parser.add_argument('-f')  # File Name

# store IP address, file name, and port numbers
args = parser.parse_args()
ip_address = args.a
file_name = args.f
server_port = int(args.sp)
client_port = int(args.cp)

# if either port number out of range, program terminates
if server_port < 5000 or server_port > 65535:
    sys.exit("ERROR: argParse value for server port is out of range (<5000, >65535)")

if client_port < 5000 or client_port > 65535:
    sys.exit("ERROR: argParse value for client port is out of range (<5000, >65535)")