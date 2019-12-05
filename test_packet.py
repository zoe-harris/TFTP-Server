# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3

from packet import Packet


class TestPacket:

    def test_ack(self):
        # assert packet length is 4 bytes
        assert len(Packet.make_ack(0)) == 4
        # assert packet op code is 4
        assert int.from_bytes(Packet.make_ack(0)[0:2], 'big') == 4

    def test_data_pkt(self):
        print("Do stuff here...")
        # assert packet length <= 516 bytes and >= 4 bytes
        # assert op code is 3
