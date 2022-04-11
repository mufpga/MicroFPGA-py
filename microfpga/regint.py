""" The register interface defines the communication protocol for writing and
reading data from the FPGA.

It is based on the original register interface from Alchitry.
"""
import warnings
import serial.tools.list_ports

# Vendor and hardware ID, used to detect the FPGAs.
AU_CU_VID = "0403:6010"
VID_PID = "VID:PID"[::-1]
SER = " SER"


def format_write_request(address, value):
    """ Format a write request based on an address and the value to write to
    the FPGA.

    :param address: address at which to write date.
    :param value: data to write to the address.
    :return: formatted request.
    """
    if address >= 2**(4 * 8):
        raise ValueError(f'Address {address} is too large (max 4 bytes).')
    if address < 0:
        raise ValueError(f'Address {address} cannot be negative.')

    if value >= 2**(4 * 8):
        raise ValueError(f'Value {value} is too large (max 4 bytes).')
    if value < 0:
        raise ValueError(f'Address {address} cannot be negative.')

    buff = bytearray(9)

    buff[0] = 1 << 7
    buff[1:] = int.to_bytes(address, length=4, byteorder="little")
    buff[5:] = int.to_bytes(value, length=4, byteorder="little")

    return buff


def format_read_request(address):
    """ Format a read request for the specified address.

    :param address: address at which to read date from the FPGA.
    :return: formatted request.
    """
    if address >= 2**(4 * 8):
        raise ValueError(f'Address {address} is too large (max 4 bytes).')
    if address < 0:
        raise ValueError(f'Address {address} cannot be negative.')

    buff = bytearray(5)

    buff[0] = 0
    buff[1:] = int.to_bytes(address, length=4, byteorder="little")

    return buff


def format_to_int(data):
    """ Format 4 bytes into an int value.

    This method is used to format the answer to a read request.

    :param data: 4 byte-long data read from the FPGA.
    :return: int value corresponding to the data (little endian).
    """
    assert (
        len(data) == 4
    ), f"Data has the wrong number of bytes (got {len(data)}, expected 4)"

    # regint returns a byte array with little endian encoding
    val = (
        (data[0] & 0xFF) |
        (data[1] & 0xFF) << 8 |
        (data[2] & 0xFF) << 16 |
        (data[3] & 0xFF) << 24
    )

    return val


def _find_port():
    """ Detects all USB ports compatible with MicroFPGA.

    This method uses serial.tools.list_ports to get a list of all USB ports,
    and then selects all FPGA from Alchitry.

    :return: list of compatible USB ports.
    """
    # list ports
    port_list = list(serial.tools.list_ports.comports())

    # checks vendor and product IDs
    au_cu_list = []
    for port in port_list:
        start = len(port.hwid) - port.hwid[::-1].find(VID_PID) + 1
        end = port.hwid.find(SER)

        vid_pid = port.hwid[start:end]
        if vid_pid == AU_CU_VID:
            au_cu_list.append(port.device)

    return au_cu_list


class RegisterInterface:
    """ Communication interface for the FPGA.

    This class allows writing and reading data from the FPGA.

    """
    def __init__(self, known_device=None):
        self._connected = False
        devices = _find_port()

        if devices:
            if len(devices) == 1:
                self._device = devices[0]
                self.__connect()
            else:
                if known_device in devices:
                    self._device = known_device
                    self.__connect()
                else:
                    self.__not_connected()
                    warnings.warn(
                        f"Cannot choose between detected devices {devices} "
                        f"(known_device={known_device}). Choose a device from"
                        f" the list and pass it as known_device parameter to "
                        f"the controller. If there is no detected device in "
                        f"the list, check the physical device connection."
                    )
        else:
            self.__not_connected()
            warnings.warn("No device found.")

    def __connect(self):
        assert self._device is not None
        self._serial = serial.Serial(self._device, 57600, timeout=1)
        self._connected = True

    def __not_connected(self):
        self._device = None
        self._serial = None
        self._connected = False

    def is_connected(self):
        """ Check if it is connected to a USB port.

        :return: True if it is, False otherwise.
        """
        return self._connected

    def disconnect(self):
        """ Disconnect from the USB port.

        :return:
        """
        if self._serial:
            self._serial.close()
        self._connected = False

    def get_device(self):
        """ Return the device.

        :return: device.
        """
        return self._device

    def write(self, address, value):
        """ Write a new value at the specified address.

        :param address: address at which to write the value.
        :param value: new value.
        :return: True if the request was sent, False if the device is not
            connected.
        """
        if self._connected:
            self._serial.write(format_write_request(address, value))
            return True
        return False

    def read(self, address):
        """ Write a read request to the address and reads 4 bytes.

        :param address: address to read from.
        :return: value returned by the FPGA.
        """
        if self._connected:
            self._serial.write(format_read_request(address))
            return format_to_int(self._serial.read(4))
        return -1
