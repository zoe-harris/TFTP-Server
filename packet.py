# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3


class Packet:

    def make_ack(self, block_num):
        ack_op = bytearray((4).to_bytes(2, byteorder='big'))
        block_num = bytearray(block_num.to_bytes(2, byteorder='big'))
        ack = ack_op + block_num
        return ack

    def make_data(self, block_num, data):
        header = self.make_data_header(block_num)
        data_pkt = header + data
        return data_pkt

    def make_data_header(self, block_num):
        data_op = bytearray((3).to_bytes(2, byteorder='big'))
        block_num = bytearray(block_num.to_bytes(2, byteorder='big'))
        data_header = data_op + block_num
        return data_header

    def op_code(self, pkt):
        return int.from_bytes(pkt[0:2], 'big')

    def get_block_num(self, pkt):
        return int.from_bytes(pkt[2:4], 'big')