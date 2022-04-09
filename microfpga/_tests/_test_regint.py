import pytest
from microfpga.regint import format_read_request, format_write_request, format_to_int


@pytest.mark.parametrize('incorrect_data', [b'', b'\x2a\x0d\x07', b'\x2a\x0d\x07\x56\xca'])
def test_format_to_int_exception(incorrect_data):
    with pytest.raises(AssertionError):
        format_to_int(incorrect_data)


@pytest.mark.parametrize('data', [0, 42, 86, 65536, 2147483648, 4294967295])
def test_format_to_int(data):
    data_bytes = int.to_bytes(data, length=4, byteorder='little')

    data_int = int.from_bytes(data_bytes, byteorder='little')
    assert data_int == data
    assert format_to_int(data_bytes) == data


@pytest.mark.parametrize('address', [0, 42, 86, 65536, 2147483648, 4294967295])
def test_format_read_request(address):
    ref_request = bytearray(5)
    ref_request[0] = 0  # read request flag

    # format address
    data_bytes = int.to_bytes(address, length=4, byteorder='little')
    ref_request[1:] = data_bytes

    read_request = format_read_request(address)
    assert read_request == ref_request


@pytest.mark.parametrize('address,data', [(0, 4294967295), (42, 2147483648), (86, 65536), (2147483648, 4294967295)])
def test_format_read_request(address, data):
    ref_request = bytearray(5)
    ref_request[0] = 128  # write request flag ('10000000' or 1 << 7)

    # format address
    address_bytes = int.to_bytes(address, length=4, byteorder='little')
    ref_request[1:] = address_bytes

    # format data
    data_bytes = int.to_bytes(data, length=4, byteorder='little')
    ref_request[5:] = data_bytes

    write_request = format_write_request(address, data)
    assert write_request == ref_request
