from abc import ABC, abstractmethod
from microfpga import regint
from enum import Enum

NUM_LASERS = 8
NUM_TTL = 4
NUM_PWM = 5
NUM_SERVOS = 7
NUM_AI = 8

ADDR_MODE = 0
ADDR_DUR = ADDR_MODE + NUM_LASERS
ADDR_SEQ = ADDR_DUR + NUM_LASERS
ADDR_TTL = ADDR_SEQ + NUM_LASERS
ADDR_SERVO = ADDR_TTL + NUM_TTL
ADDR_PWM = ADDR_SERVO + NUM_SERVOS

ADDR_ACTIVE_TRIGGER = ADDR_PWM + NUM_PWM
ADDR_START_TRIGGER = ADDR_ACTIVE_TRIGGER + 1
ADDR_CAM_PULSE = ADDR_START_TRIGGER + 1
ADDR_CAM_PERIOD = ADDR_CAM_PULSE + 1
ADDR_CAM_EXPO = ADDR_CAM_PERIOD + 1
ADDR_LASER_DELAY = ADDR_CAM_EXPO + 1

ADDR_AI = ADDR_LASER_DELAY + 1

ADDR_VER = 200
ADDR_ID = 201

CURR_VER = 3

ID_AU = 79
ID_AUP = 80
ID_CU = 29
ID_MOJO = 12

MAX_MODE = 4
MAX_DURATION = 65535
MAX_SEQUENCE = 65535
MAX_TTL = 1
MAX_SERVO = 65535
MAX_PWM = 255
MAX_AI = 65535
MAX_CAM_PULSE = 65535
MAX_CAM_PERIOD = 65535
MAX_CAM_EXPOSURE = 65535
MAX_LASER_DELAY = 65535
MAX_START = 1


class LaserTriggerMode(Enum):
    MODE_OFF = 0
    MODE_ON = 1
    MODE_RISING = 2
    MODE_FALLING = 3
    MODE_FOLLOW = 4


class CameraTriggerMode(Enum):
    ACTIVE = 1
    PASSIVE = 0


def format_sequence(string):
    b = True
    for ch in string:
        if ch != '0' and ch != '1':
            b = False

    if b and len(string) == 16:
        return int(string, 2)
    else:
        return -1


def get_compatible_ids():
    return ID_AU, ID_AUP, ID_CU, ID_MOJO


def get_analog_ids():
    return ID_AU, ID_AUP, ID_MOJO


class Signal(ABC):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface, output: bool = True):
        if channel_id < self.get_num_signal():
            self.channel_id = channel_id
            self.output = output
            self._serial_com = serial_com
        else:
            raise Exception(f'{channel_id} exceeds maximum number of {self.get_name()} signals.')

    @abstractmethod
    def get_address(self):
        pass

    @abstractmethod
    def get_max(self):
        pass

    def is_allowed(self, value: int):
        return 0 <= value <= self.get_max()

    @abstractmethod
    def get_num_signal(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    def set_state(self, value: int):
        if self.output and self.is_allowed(value):
            return self._serial_com.write(self.get_address() + self.channel_id, value)
        else:
            raise ValueError(f'Value {value} not allowed in {self.get_name()} (channel {self.channel_id}).')

    def get_state(self):
        return self._serial_com.read(self.get_address() + self.channel_id)


class Ttl(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_TTL

    def get_max(self):
        return MAX_TTL

    def get_num_signal(self):
        return NUM_TTL

    def get_name(self):
        return 'TTL'


class Pwm(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_PWM

    def get_max(self):
        return MAX_PWM

    def get_num_signal(self):
        return NUM_PWM

    def get_name(self):
        return 'PWM'


class Servo(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_SERVO

    def get_max(self):
        return MAX_SERVO

    def get_num_signal(self):
        return NUM_SERVOS

    def get_name(self):
        return 'Servos'


class Analog(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com, False)

    def get_address(self):
        return ADDR_AI

    def get_max(self):
        return -1

    def get_num_signal(self):
        return NUM_AI

    def get_name(self):
        return 'AI'


class _Mode(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_MODE

    def get_max(self):
        return MAX_MODE

    def get_num_signal(self):
        return NUM_LASERS

    def is_allowed(self, value):
        if isinstance(value, LaserTriggerMode):
            return Signal.is_allowed(self, value.value)
        else:
            return Signal.is_allowed(self, value)

    def set_state(self, value):
        if isinstance(value, LaserTriggerMode):
            return Signal.set_state(self, value.value)
        else:
            return Signal.set_state(self, value)

    def get_name(self):
        return 'Laser mode'


class _Duration(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_DUR

    def get_max(self):
        return MAX_DURATION

    def get_num_signal(self):
        return NUM_LASERS

    def get_name(self):
        return 'Laser duration'


class _Sequence(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_SEQ

    def get_max(self):
        return MAX_SEQUENCE

    def get_num_signal(self):
        return NUM_LASERS

    def get_name(self):
        return 'Laser sequence'


class LaserTrigger:

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        self.channel_id = channel_id

        self.mode = _Mode(channel_id, serial_com)
        self.duration = _Duration(channel_id, serial_com)
        self.seq = _Sequence(channel_id, serial_com)

    def set_mode(self, value):
        return self.mode.set_state(value)

    def get_mode(self):
        return self.mode.get_state()

    def set_duration(self, value):
        return self.duration.set_state(value)

    def get_duration(self):
        return self.duration.get_state()

    def set_sequence(self, value):
        return self.seq.set_state(value)

    def get_sequence(self):
        return self.seq.get_state()

    def set_state(self, mode, duration, sequence):
        b = self.set_mode(mode)
        if not b:
            print(f'Laser {self.channel_id}: could not set Mode properly {b}.')
            return b

        b = self.set_duration(duration)
        if not b:
            print(f'Laser {self.channel_id}: could not set Duration properly.')
            return b

        b = self.set_sequence(sequence)
        if not b:
            print(f'Laser {self.channel_id}: could not set Sequence properly.')

        return b

    def get_state(self):
        return [self.get_mode(), self.get_duration(), self.get_sequence()]


class _CameraPulse(Signal):

    def __init__(self, serial_com: regint.RegisterInterface):
        Signal.__init__(self, 0, serial_com)

    def get_address(self):
        return ADDR_CAM_PULSE

    def get_max(self):
        return MAX_CAM_PULSE

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Camera trigger pulse'


class _CameraPeriod(Signal):

    def __init__(self, serial_com: regint.RegisterInterface):
        Signal.__init__(self, 0, serial_com)

    def get_address(self):
        return ADDR_CAM_PERIOD

    def get_max(self):
        return MAX_CAM_PERIOD

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Camera trigger period'


class _CameraExposure(Signal):

    def __init__(self, serial_com: regint.RegisterInterface):
        Signal.__init__(self, 0, serial_com)

    def get_address(self):
        return ADDR_CAM_EXPO

    def get_max(self):
        return MAX_CAM_EXPOSURE

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Camera exposure'


class _LaserDelay(Signal):

    def __init__(self, serial_com: regint.RegisterInterface):
        Signal.__init__(self, 0, serial_com)

    def get_address(self):
        return ADDR_LASER_DELAY

    def get_max(self):
        return MAX_LASER_DELAY

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Laser trigger delay'


class _CameraStart(Signal):

    def __init__(self, serial_com: regint.RegisterInterface):
        Signal.__init__(self, 0, serial_com)

    def get_address(self):
        return ADDR_START_TRIGGER

    def get_max(self):
        return 1

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Camera start/stop'

    def start(self):
        return self.set_state(1)

    def stop(self):
        return self.set_state(0)


class TriggerMode(Signal):

    def __init__(self, serial_com: regint.RegisterInterface):
        Signal.__init__(self, 0, serial_com)

    def get_address(self):
        return ADDR_ACTIVE_TRIGGER

    def get_max(self):
        return CameraTriggerMode.ACTIVE.value

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Active/passive camera trigger'

    def set_active_trigger(self):
        self.set_state(CameraTriggerMode.ACTIVE.value)

    def set_passive_trigger(self):
        self.set_state(CameraTriggerMode.PASSIVE.value)


class Camera:

    def __init__(self, serial_com: regint.RegisterInterface):
        self._pulse = _CameraPulse(serial_com)
        self._period = _CameraPeriod(serial_com)
        self._exposure = _CameraExposure(serial_com)
        self._delay = _LaserDelay(serial_com)
        self._start = _CameraStart(serial_com)

    def set_pulse(self, value):
        return self._pulse.set_state(value)

    def get_pulse(self):
        return self._pulse.get_state()

    def set_period(self, value):
        return self._period.set_state(value)

    def get_period(self):
        return self._period.get_state()

    def set_exposure(self, value):
        return self._exposure.set_state(value)

    def get_exposure(self):
        return self._exposure.get_state()

    def set_delay(self, value):
        return self._delay.set_state(value)

    def get_delay(self):
        return self._delay.get_state()

    def set_state(self, pulse, period, exposure, delay):
        self.set_pulse(pulse)
        self.set_period(period)
        self.set_exposure(exposure)
        self.set_delay(delay)

    def get_state(self):
        return {'pulse': self.get_pulse(),
                'period': self.get_period(),
                'exposure': self.get_exposure(),
                'delay': self.get_delay()}

    def start(self):
        return self._start.start()

    def stop(self):
        return self._start.stop()

    def is_running(self):
        return self._start.get_state()
