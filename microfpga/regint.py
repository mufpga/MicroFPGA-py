import serial.tools.list_ports


class RegisterInterface:

    def __init__(self, known_device=None):
        devices = self.__find_port()

        if devices:
            if len(devices) == 1:
                self._device = devices[0]
                self.__connect()
            else:
                if known_device in devices:
                    self._device = known_device
                    self.__connect()
                else:
                    raise Warning(f'Cannot choose between detected devices {devices} (known_device '
                                  f'= {known_device}). Choose a device from the list and pass it as '
                                  f'know_device parameter to the controller. If there is no detected '
                                  f'device in the list, check the physical device connection.')
                    self.__not_connected()
        else:
            raise Warning('No device found.')
            self.__not_connected()

    def __connect(self):
        assert self._device is not None
        self._serial = serial.Serial(self._device, 57600, timeout=1)
        self._connected = True

    def __not_connected(self):
        self._device = None
        self._serial = None
        self._connected = False

    def __find_port(self):
        AU_CU_VID = '0403:6010'
        VID_PID = 'VID:PID'[::-1]
        SER = ' SER'

        # list ports
        plist = list(serial.tools.list_ports.comports())

        # checks vendor and product IDs
        au_cu_list = []
        for s in plist:
            start = len(s.hwid) - s.hwid[::-1].find(VID_PID) + 1
            end = s.hwid.find(SER)

            vid_pid = s.hwid[start:end]
            if vid_pid == AU_CU_VID:
                au_cu_list.append(s.device)

        return au_cu_list

    def is_connected(self):
        return self._connected

    def disconnect(self):
        self._serial.close()

    def get_device(self):
        return self._device

    def __format_read_request(self, address):
        buff = bytearray(5)

        buff[0] = 0 << 7
        buff[1] = address & 0xff
        buff[2] = (address >> 8) & 0xff
        buff[3] = (address >> 16) & 0xff
        buff[4] = (address >> 24) & 0xff

        return buff

    def __format_write_request(self, address, data):
        buff = bytearray(9)

        buff[0] = 1 << 7
        buff[1] = address & 0xff
        buff[2] = (address >> 8) & 0xff
        buff[3] = (address >> 16) & 0xff
        buff[4] = (address >> 24) & 0xff
        buff[5] = data & 0xff
        buff[6] = (data >> 8) & 0xff
        buff[7] = (data >> 16) & 0xff
        buff[8] = (data >> 24) & 0xff

        return buff

    def __format_to_int(self, data):
        assert len(data) == 4, f'Data has the wrong number of bytes (got {len(data)}, expected 4)'
        val = (data[0] & 0xff) | (data[1] & 0xff) << 8 | (data[2] & 0xff) << 16 | (data[3] & 0xff) << 24
        return val

    def write(self, address, value):
        if self._connected:
            self._serial.write(self.__format_write_request(address, value))
            return True
        return False

    def read(self, address):
        if self._connected:
            self._serial.write(self.__format_read_request(address))
            return self.__format_to_int(self._serial.read(4))
