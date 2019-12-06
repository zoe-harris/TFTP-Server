# Zoe Harris
# CSCE365 Computer Networks
# Programming Assignment #3

from packet import Packet
import pytest


class TestPacket:

    @pytest.mark.parametrize("input_num, expected", [
        (0, bytearray(b'\x00\x04\x00\x00')),
        (32767, bytearray(b'\x00\x04\x7f\xff')),
        (65534, bytearray(b'\x00\x04\xff\xfe')),
        # FIXME: pytest.mark.xfail((70000, bytearray(b'\x00\x04\xff\xfe'))),
        # FIXME: pytest.mark.xfail((512, bytearray(b'\x00\x04\x7f\xff'))),
        # FIXME: pytest.mark.xfail((47834, bytearray(b'\x00\x04\x00\x00')))
    ])
    def test_make_ack(self, input_num, expected):
        assert Packet.make_ack(input_num) == expected

    @pytest.mark.parametrize("input_block, input_data, expected", [
        (0, b'this is a test', bytearray(b'\x00\x03\x00\x00this is a test')),
        (32767, b'this is a test', bytearray(b'\x00\x03\x7f\xffthis is a test')),
        (65534, b'this is a test', bytearray(b'\x00\x03\xff\xfethis is a test')),
        # FIXME: pytest.mark.xfail((32767, b'this is a test', bytearray(b'\x00\x03\x00\x00this is a test'))),
        # FIXME: pytest.mark.xfail((0, b'this is a test', bytearray(b'\x00\x03\x7f\xffthis is a test'))),
        # FIXME: pytest.mark.xfail((65534, b'this is a test', bytearray(b'\x00\x03\xff\xfefail this test')))
    ])
    def test_make_data_pkt(self, input_block, input_data, expected):
        assert Packet.make_data(input_block, input_data) == expected

    @pytest.mark.parametrize("input_block, expected", [
        (0, bytearray(b'\x00\x03\x00\x00')),
        (32767, bytearray(b'\x00\x03\x7f\xff')),
        (65534, bytearray(b'\x00\x03\xff\xfe'))
    ])
    def test_data_header(self, input_block, expected):
        assert Packet.make_data_header(input_block) == expected

    @pytest.mark.parametrize("input_pkt, expected", [
        (bytearray(b'\x00\x01test.txt\x00netascii\x00'), 1),
        (bytearray(b'\x00\x02test.txt\x00netascii\x00'), 2),
        (bytearray(b'\x00\x03\x00\x00this is a test'), 3),
        (bytearray(b'\x00\x04\x00\x00'), 4),
        (bytearray(b'\x00\x05\x00\x01File not found.\x00'), 5)
    ])
    def test_get_op_code(self, input_pkt, expected):
        assert Packet.get_op_code(input_pkt) == expected

    @pytest.mark.parametrize("input_pkt, expected", [
        (bytearray(b'\x00\x03\x00\x00this is a test'), 0),
        (bytearray(b'\x00\x03\x7f\xffthis is a test'), 32767),
        (bytearray(b'\x00\x03\xff\xfethis is a test'), 65534),
        (bytearray(b'\x00\x04\x00\x00'), 0),
        (bytearray(b'\x00\x04\x7f\xff'), 32767),
        (bytearray(b'\x00\x04\xff\xfe'), 65534)
    ])
    def test_get_block_num(self, input_pkt, expected):
        assert Packet.get_block_num(input_pkt) == expected

    @pytest.mark.parametrize("input_pkt, expected", [
        (bytearray(b'\x00\x01ThisIsATest.txt\x00netascii\x00'), "ThisIsATest.txt"),
        (bytearray(b'\x00\x01abc.txt\x00netascii\x00'), "abc.txt"),
        (bytearray(b'\x00\x02Foobar.txt\x00netascii\x00'), "Foobar.txt"),
        (bytearray(b'\x00\x02HelloWorld.txt\x00netascii\x00'), "HelloWorld.txt")
    ])
    def test_get_file_name(self, input_pkt, expected):
        assert Packet.get_file_name(input_pkt) == expected

