# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3


class Packet:

    """ METHODS FOR MAKING PACKETS  """

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

    """ METHODS FOR READING FROM PACKETS """

    @staticmethod
    def get_op_code(pkt):
        return int.from_bytes(pkt[0:2], 'big')

    @staticmethod
    def get_block_num(pkt):
        return int.from_bytes(pkt[2:4], 'big')

    @staticmethod
    def get_file_name(pkt):

        counter = 2
        check_zero = pkt[2]

        while check_zero != 0:
            counter += 1
            check_zero = pkt[counter]

        file_name = pkt[2:counter]
        return file_name.decode("utf-8")

    """

    2 bytes     string     1 byte  string    1 byte
    ------------------------------------------------
    | Opcode |  Filename  |   0   |  Mode  |   0   |
    ------------------------------------------------

    RRQ : Opcode #1
    WRQ : Opcode #2

    """
