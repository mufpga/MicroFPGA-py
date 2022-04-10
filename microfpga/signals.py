""" Module defining the different signals (I/O) classes of MicroFPGA.
"""
from abc import ABC, abstractmethod
from microfpga import regint
from enum import Enum

# constants, defined similarly in the FPGA configuration source
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

ADDR_ACTIVE_SYNC = ADDR_PWM + NUM_PWM
ADDR_START_TRIGGER = ADDR_ACTIVE_SYNC + 1
ADDR_CAM_PULSE = ADDR_START_TRIGGER + 1
ADDR_CAM_READOUT = ADDR_CAM_PULSE + 1
ADDR_CAM_EXPO = ADDR_CAM_READOUT + 1
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
MAX_DURATION = 1048575
MAX_SEQUENCE = 65535
MAX_TTL = 1
MAX_SERVO = 65535
MAX_PWM = 255
MAX_AI = 65535
MAX_CAM_PULSE = 1048575
MAX_CAM_READOUT = 65535
MAX_CAM_EXPOSURE = 1048575
MAX_LASER_DELAY = 65535
MAX_START = 1


class LaserTriggerMode(Enum):
    """The different laser trigger modes.

    In passive synchronization, the FPGA receives an exposure signal from a
    camera in order to trigger the lasers. In active synchronization, the
    exposure signal is generated by the FPGA itself, the camera is being
    triggered by another FPGA-generated signal.

    MODE_OFF: off all the time, regardless of the exposure signal.
    MODE_OFF: on all the time, regardless of the exposure signal.
    MODE_RISING: pulse on rising edges of the exposure signal.
    MODE_FALLING: pulse on falling edges of the exposure signal.
    MODE_FOLLOW:  follow the exposure signal.
    """

    MODE_OFF = 0  # off all the time
    MODE_ON = 1  # on all the time
    MODE_RISING = 2  # pulse on rising edges of the "exposure signal"
    MODE_FALLING = 3  # pulse on falling edges of the "exposure signal"
    MODE_FOLLOW = 4  # follow the "exposure signal"


class TriggerSyncMode(Enum):
    """The different synchronization modes

    PASSIVE: the FPGA receives an exposure signal from a camera in order to
            trigger the lasers.
    ACTIVE: the exposure signal is generated by the FPGA itself, the camera is
            being triggered by another FPGA-generated signal (fire signal).
    """

    PASSIVE = 0
    ACTIVE = 1


class ActiveParameters(Enum):
    """Parameters used in active synchronization to generate the fire signal
    and the internal exposure signal.

    PULSE: duration in \u03bcs of the fire signal pulses.
    DELAY: delay in \u03bcs between fire signal and exposure signal rising
            edges.
    EXPOSURE: duration in \u03bcs of the exposure signal pulses.
    READOUT: delay in \u03bcs of exposure signal falling edges and fire signal
            rising edges.
    """

    PULSE = "pulse"
    DELAY = "delay"
    EXPOSURE = "exposure"
    READOUT = "read-out"


def format_sequence(sequence):
    """Convert a binary sequence of 16 bits into an int.

    :param sequence: String composed of 16 zeroes or ones.
    :return: int value of the binary sequence, or -1 if the sequence is not 16
            characters long or contains characters others than 0 or 1.
    """
    b = True
    for ch in sequence:
        if ch != "0" and ch != "1":
            b = False

    if b and len(sequence) == 16:
        return int(sequence, 2)
    else:
        return -1


def get_compatible_ids():
    """Return a list of board IDs compatible with MicroFPGA.

    The compatible boards are the Au, Au+, Cu and Mojo. When configured for
    MicroFPGA, the board type can be identified by their ID.

    :return: list of compatible IDs.
    """
    return ID_AU, ID_AUP, ID_CU, ID_MOJO


def get_analog_ids():
    """Return a list of board IDs compatible with analog inputs.

    :return: list of compatible IDs.
    """
    return ID_AU, ID_AUP, ID_MOJO


class Signal(ABC):
    """Base class for all MicroFPGA inputs/outputs.

    A signal corresponds to an input or an output of the FPGA. A signal has a
    state which is represented by an int in the range [0, max]. Signals can be
    read-only.

    Each signal class has a maximum number of channels of possible instances,
    each indexed by a channel id.

    Args:
        channel_id (int): channel ID.
        serial_com (RegisterInterface): register interface taking care of the
            communication with the FPGA.
        output (bool): True if the signal is an output signal, False if the
            signal is read-only.
    """

    def __init__(
        self,
        channel_id: int,
        serial_com: regint.RegisterInterface,
        output: bool = True
    ):
        if channel_id < self.get_num_signal():
            self.channel_id = channel_id
            self.output = output
            self._serial_com = serial_com
        else:
            raise Exception(
                f"{channel_id} exceeds maximum number of {self.get_name()} "
                f"signals."
            )

    @abstractmethod
    def get_address(self):
        """Return the signal read/write address.

        If the signal is read-only, then the address is only valid for read
        request.

        :return: address.
        """
        pass

    @abstractmethod
    def get_max(self):
        """Get the maximum value of the signal.

        All signals have a minimum value of 0.

        :return: maximum value.
        """
        pass

    def is_allowed(self, value: int):
        """Check if the value is a valid signal value.

        The value is valid if and only if it in the range [0, max], where max
        can be queried using self.get_max().

        :param value: value to test.
        :return: True if the value is allowed, False otherwise.
        """
        return 0 <= value <= self.get_max() and self.output

    def is_read_only(self):
        return not self.output

    @abstractmethod
    def get_num_signal(self):
        """Return the maximum number of channels for the signal type."""
        pass

    @abstractmethod
    def get_name(self):
        """Return the signal name.

        :return: signal name.
        """
        pass

    def set_state(self, value: int):
        """Set the signal state.

        Throws errors if the signal is read-only or the value not allowed.

        :param value: new state.
        :return: True if the request was sent, False if the device is not
            connected.
        """
        if self.output and self.is_allowed(value):
            return self._serial_com.write(
                self.get_address() + self.channel_id,
                value
            )
        else:
            if self.output:
                raise ValueError(
                    f"Value {value} not allowed in {self.get_name()} "
                    f"(channel {self.channel_id})."
                )
            else:
                raise ValueError(
                    f"{self.get_name()} (channel {self.channel_id}) is "
                    f"read-only."
                )

    def get_state(self):
        """Read the state of the signal.

        :return: signal state.
        """
        return self._serial_com.read(self.get_address() + self.channel_id)


class Ttl(Signal):
    """TTL signal.

    A TTL signal has a state range of [0, 1], representing digital LOW and
    HIGH.
    """

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_TTL

    def get_max(self):
        return MAX_TTL

    def get_num_signal(self):
        return NUM_TTL

    def get_name(self):
        return "TTL"


class Pwm(Signal):
    """PWM signal.

    A PWM outputs a periodic signal with duty cycle equal to the signal state
    [0, 255].
    """

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_PWM

    def get_max(self):
        return MAX_PWM

    def get_num_signal(self):
        return NUM_PWM

    def get_name(self):
        return "PWM"


class Servo(Signal):
    """Servo signal.

    A Servo signal is a particular type of PWM whose duty cycle is bound in a
    range between a min and a max. Here the duty cycle is set using a state in
    the range [0, 65535]. The Servo signal output switches off after 10 s to
    avoid vibrations on the optical table.
    """

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_SERVO

    def get_max(self):
        return MAX_SERVO

    def get_num_signal(self):
        return NUM_SERVOS

    def get_name(self):
        return "Servos"


class Analog(Signal):
    """Analog signal.

    An Analog signal is a read-only signal with values comprised in the range
    [0, 65535], which corresponds to the 0-1 V
    range.
    """

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com, False)

    def get_address(self):
        return ADDR_AI

    def get_max(self):
        return -1

    def get_num_signal(self):
        return NUM_AI

    def get_name(self):
        return "AI"


class _Mode(Signal):
    """Laser trigger: mode signal.

    The mode signal is a parameter of the laser trigger output that dictates
    the type of the trigger signal. It has a discrete state defined by the
    LaserTriggerMode enum.
    """

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_MODE

    def get_max(self):
        return MAX_MODE

    def get_num_signal(self):
        return NUM_LASERS

    def is_allowed(self, value):
        """Check if the value is a valid mode state.

        The value is valid if and only if it corresponds to a LaserTriggerMode
        state.

        :param value: value to test, whether int or LaserTriggerMode enum
            state.
        :return: True if the value is allowed, False otherwise.
        """
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
        return "Laser mode"


class _Duration(Signal):
    """Laser trigger: duration signal.

    The duration signal is a parameter of the laser trigger output that
    dictates the duration in \u03bcs of the laser trigger pulses in rising and
    falling trigger modes.
    """

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_DUR

    def get_max(self):
        return MAX_DURATION

    def get_num_signal(self):
        return NUM_LASERS

    def get_name(self):
        return "Laser duration"


class _Sequence(Signal):
    """Laser trigger: sequence signal.

    The sequence signal is a parameter of the laser trigger output that allows
    defining a sequence of frames to skip during triggering in rising, falling
    and follow trigger modes. The sequence is a binary string of length 16,
    where 0 indicates that the laser should not be triggered on this frame of
    the sequence.
    """

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_SEQ

    def get_max(self):
        return MAX_SEQUENCE

    def get_num_signal(self):
        return NUM_LASERS

    def get_name(self):
        return "Laser sequence"


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
            print(f"Laser {self.channel_id}: could not set Mode {b}.")
            return b

        b = self.set_duration(duration)
        if not b:
            print(f"Laser {self.channel_id}: could not set Duration.")
            return b

        b = self.set_sequence(sequence)
        if not b:
            print(f"Laser {self.channel_id}: could not set Sequence.")

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
        return "Camera fire pulse length"


class _CameraReadout(Signal):
    def __init__(self, serial_com: regint.RegisterInterface):
        Signal.__init__(self, 0, serial_com)

    def get_address(self):
        return ADDR_CAM_READOUT

    def get_max(self):
        return MAX_CAM_READOUT

    def get_num_signal(self):
        return 1

    def get_name(self):
        return "Camera read-out time"


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
        return "Camera exposure"


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
        return "Laser trigger delay with respect to the camera fire"


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
        return "Camera start/stop"

    def start(self):
        return self.set_state(1)

    def stop(self):
        return self.set_state(0)


class SyncMode(Signal):
    def __init__(self, serial_com: regint.RegisterInterface):
        Signal.__init__(self, 0, serial_com)

    def get_address(self):
        return ADDR_ACTIVE_SYNC

    def get_max(self):
        return TriggerSyncMode.ACTIVE.value

    def get_num_signal(self):
        return 1

    def get_name(self):
        return "Active/passive synchronisation"

    def set_active_sync(self):
        self.set_state(TriggerSyncMode.ACTIVE.value)

    def set_passive_sync(self):
        self.set_state(TriggerSyncMode.PASSIVE.value)


class Camera:
    def __init__(self, serial_com: regint.RegisterInterface):
        self._pulse = _CameraPulse(serial_com)
        self._readout = _CameraReadout(serial_com)
        self._exposure = _CameraExposure(serial_com)
        self._delay = _LaserDelay(serial_com)
        self._start = _CameraStart(serial_com)

    def set_pulse(self, value):
        return self._pulse.set_state(value)

    def get_pulse(self):
        return self._pulse.get_state()

    def set_readout(self, value):
        return self._readout.set_state(value)

    def get_readout(self):
        return self._readout.get_state()

    def set_exposure(self, value):
        return self._exposure.set_state(value)

    def get_exposure(self):
        return self._exposure.get_state()

    def set_delay(self, value):
        return self._delay.set_state(value)

    def get_delay(self):
        return self._delay.get_state()

    def set_state(self, pulse, delay, exposure, readout):
        self.set_pulse(pulse)
        self.set_delay(delay)
        self.set_exposure(exposure)
        self.set_readout(readout)

    def get_state(self):
        return {
            ActiveParameters.PULSE.value: self.get_pulse(),
            ActiveParameters.DELAY.value: self.get_delay(),
            ActiveParameters.EXPOSURE.value: self.get_exposure(),
            ActiveParameters.READOUT.value: self.get_readout(),
        }

    def start(self):
        return self._start.start()

    def stop(self):
        return self._start.stop()

    def is_running(self):
        return self._start.get_state()
