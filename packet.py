# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3


class Packet:

    @staticmethod
    def make_ack(block_num):
        ack_op = bytearray((4).to_bytes(2, byteorder='big'))
        block_num = bytearray(block_num.to_bytes(2, byteorder='big'))
        ack = ack_op + block_num
        return ack

    @staticmethod
    def make_data(block_num, data):
        header = Packet.make_data_header(block_num)
        data_pkt = header + data
        return data_pkt

    @staticmethod
    def make_data_header(block_num):
        data_op = bytearray((3).to_bytes(2, byteorder='big'))
        block_num = bytearray(block_num.to_bytes(2, byteorder='big'))
        data_header = data_op + block_num
        return data_header

    @staticmethod
    def op_code(pkt):
        return int.from_bytes(pkt[0:2], 'big')

    @staticmethod
    def get_block_num(pkt):
        return int.from_bytes(pkt[2:4], 'big')