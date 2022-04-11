""" Unit tests of microfpga.regint static functions.
"""
import pytest
from microfpga.regint import (
    format_read_request,
    format_write_request,
    format_to_int
)


@pytest.mark.parametrize(
    "incorrect_data", [b"", b"\x2a\x0d\x07", b"\x2a\x0d\x07\x56\xca"]
)
def test_format_to_int_exception(incorrect_data):
    """ Check that incorrect data (length different from 4 bytes) generate an
    assertion error.


    :param incorrect_data:
    :return:
    """
    with pytest.raises(AssertionError):
        format_to_int(incorrect_data)


@pytest.mark.parametrize("data", [0, 42, 86, 65536, 2147483648, 4294967295])
def test_format_to_int(data):
    """ Test that format_to_int encodes the 4 bytes correctly (little endian).

    :param data: int
    :return:
    """
    data_bytes = int.to_bytes(data, length=4, byteorder="little")

    data_int = int.from_bytes(data_bytes, byteorder="little")
    assert data_int == data
    assert format_to_int(data_bytes) == data


@pytest.mark.parametrize("address", [0, 42, 86, 65536, 2147483648, 4294967295])
def test_format_read_request(address):
    """ Test the formatting of read requests.

    :param address: address
    :return:
    """
    ref_request = bytearray(5)
    ref_request[0] = 0  # read request flag

    # format address
    data_bytes = int.to_bytes(address, length=4, byteorder="little")
    ref_request[1:] = data_bytes

    read_request = format_read_request(address)
    assert read_request == ref_request


@pytest.mark.parametrize(
    "address",
    [-1, 4294967296],
)
def test_format_read_request_exception(address):
    """ Tests that address raises an error when it is too large.

    :param address: address
    :return:
    """
    with pytest.raises(ValueError):
        format_read_request(address)


@pytest.mark.parametrize(
    "address,data",
    [(0, 4294967295), (42, 2147483648), (86, 65536), (2147483648, 4294967295)],
)
def test_format_write_request(address, data):
    """ Test the formatting of write requests.

    :param address:
    :param data:
    :return:
    """
    ref_request = bytearray(5)
    ref_request[0] = 128  # write request flag ('10000000' or 1 << 7)

    # format address
    address_bytes = int.to_bytes(address, length=4, byteorder="little")
    ref_request[1:] = address_bytes

    # format data
    data_bytes = int.to_bytes(data, length=4, byteorder="little")
    ref_request[5:] = data_bytes

    write_request = format_write_request(address, data)
    assert write_request == ref_request


@pytest.mark.parametrize(
    "address,value",
    [(42, 4294967296), (4294967296, 86), (11, -1), (-1, 65535)],
)
def test_format_write_request_exception(address, value):
    """ Tests that address and value raise an error when they are too large.

    :param address: address
    :param value: value
    :return:
    """
    with pytest.raises(ValueError):
        format_write_request(address, value)
