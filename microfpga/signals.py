from abc import ABC, abstractmethod
from microfpga import regint

NUM_LASERS = 8
NUM_TTL = 5
NUM_PWM = 5
NUM_SERVOS = 7
NUM_AI = 8

ADDR_MODE = 0
ADDR_DUR = ADDR_MODE+NUM_LASERS
ADDR_SEQ = ADDR_DUR+NUM_LASERS
ADDR_TTL = ADDR_SEQ+NUM_LASERS
ADDR_SERVO = ADDR_TTL+NUM_TTL
ADDR_PWM = ADDR_SERVO+NUM_SERVOS

ADDR_START_TRIGGER = ADDR_PWM + NUM_PWM
ADDR_CAM_PULSE = ADDR_START_TRIGGER + 1
ADDR_CAM_PERIOD = ADDR_CAM_PULSE + 1
ADDR_CAM_EXPO = ADDR_CAM_PERIOD + 1

ADDR_AI = ADDR_CAM_EXPO + 1

ADDR_VER = 200
ADDR_ID = 201
ADDR_TRIGGER_MODE = 202

CURR_VER = 3

ID_AU = 79
ID_CU = 29

MAX_MODE = 4
MAX_DUR = 65535
MAX_SEQ = 65535
MAX_TTL = 1
MAX_SERVO = 65535
MAX_PWM = 255
MAX_CAM_PULSE = 65535
MAX_CAM_PERIOD = 65535
MAX_CAM_EXPOSURE = 65535

def format_sequence(string):
    b = True
    for ch in string:
        if ch != '0' and ch != '1':
            b =  False
    
    if b and len(string) == 16:
        return int(string,2)
    else :
        return -1

class Signal(ABC):
    
    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface, output: bool = True):
        if channel_id < self.get_num_signal():
            self.channel_id = channel_id
            self.output = output
            self._serial_com = serial_com
        else:
            raise Exception('Index exceed maximum number of '+self.get_name()+' signals.')
    
    @abstractmethod
    def get_address(self):
        pass
       
    @abstractmethod 
    def is_allowed(self, value):
        pass
    
    @abstractmethod 
    def get_num_signal(self):
        pass
    
    @abstractmethod 
    def get_name(self):
        pass
    
    def set_state(self, value):
        if self.output and self.is_allowed(value):
            self._serial_com.write(self.get_address()+self.channel_id, value)
            return True
        else:
            return False
        
    def get_state(self):
        return self._serial_com.read(self.get_address()+self.channel_id)
    
    
class Ttl(Signal):
    
    def __init__(self, channel_id:int, serial_com:regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)
        
    def get_address(self):
        return ADDR_TTL
    
    def is_allowed(self, value):
        return (value >= 0) and (value <= MAX_TTL)

    def get_num_signal(self):
        return NUM_TTL
    
    def get_name(self):
        return 'TTL'
    
class Pwm(Signal):
    
    def __init__(self, channel_id:int, serial_com:regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)
        
    def get_address(self):
        return ADDR_PWM
    
    def is_allowed(self, value):
        return (value >= 0) and (value <= MAX_PWM)

    def get_num_signal(self):
        return NUM_PWM
    
    def get_name(self):
        return 'PWM'
    
class Servo(Signal):
    
    def __init__(self, channel_id:int, serial_com:regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)
        
    def get_address(self):
        return ADDR_SERVO
    
    def is_allowed(self, value):
        return (value >= 0) and (value <= MAX_SERVO)

    def get_num_signal(self):
        return NUM_SERVOS
    
    def get_name(self):
        return 'Servos'
    
class Analog(Signal):
    
    def __init__(self, channel_id:int, serial_com:regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com, False)
        
    def get_address(self):
        return ADDR_AI
    
    def is_allowed(self, value):
        return False

    def get_num_signal(self):
        return NUM_AI
    
    def get_name(self):
        return 'AI'

class _Mode(Signal):
    
    def __init__(self, channel_id:int, serial_com:regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)
        
    def get_address(self):
        return ADDR_MODE
    
    def is_allowed(self, value):
        return (value >= 0) and (value <= MAX_MODE)

    def get_num_signal(self):
        return NUM_LASERS
    
    def get_name(self):
        return 'Laser mode'

class _Duration(Signal):
    
    def __init__(self, channel_id:int, serial_com:regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)
        
    def get_address(self):
        return ADDR_DUR
    
    def is_allowed(self, value):
        return (value >= 0) and (value <= MAX_DUR)

    def get_num_signal(self):
        return NUM_LASERS
    
    def get_name(self):
        return 'Laser duration'
    
class _Sequence(Signal):
    
    def __init__(self, channel_id:int, serial_com:regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)
        
    def get_address(self):
        return ADDR_SEQ
    
    def is_allowed(self, value):
        return (value >= 0) and (value <= MAX_SEQ)
    
    def get_num_signal(self):
        return NUM_LASERS
    
    def get_name(self):
        return 'Laser sequence'
    
class Laser_trigger:
    MODE_OFF = 0
    MODE_ON = 1
    MODE_RISING = 2
    MODE_FALLING = 3
    MODE_CAMERA = 4
        
    def __init__(self, channel_id: int, serial_com:regint.RegisterInterface):
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
            return b
        
        b = self.set_duration(duration)
        if not b:
            return b
        
        b = self.set_sequence(sequence)
        return b
    
    def get_state(self):
        return [self.get_mode(), self.get_duration(), self.get_sequence()]


class _Camera_pulse(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_CAM_PULSE

    def is_allowed(self, value):
        return (value >= 0) and (value <= MAX_CAM_PULSE)

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Camera trigger pulse'

class _Camera_period(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_CAM_PERIOD

    def is_allowed(self, value):
        return (value >= 0) and (value <= MAX_CAM_PERIOD)

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Camera trigger period'

class _Camera_exposure(Signal):

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_CAM_EXPO

    def is_allowed(self, value):
        return (value >= 0) and (value <= MAX_CAM_EXPOSURE)

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Camera exposure'

class _Camera_start(Signal):
    START = 1
    STOP = 0

    def __init__(self, channel_id: int, serial_com: regint.RegisterInterface):
        Signal.__init__(self, channel_id, serial_com)

    def get_address(self):
        return ADDR_START_TRIGGER

    def is_allowed(self, value):
        return value == START or value == STOP

    def get_num_signal(self):
        return 1

    def get_name(self):
        return 'Camera exposure'

    def start(self):
        return self.set_state(START)

    def stop(self):
        return self.set_state(STOP)

class Camera:

    def __init__(self, serial_com: regint.RegisterInterface):
        self.channel_id = channel_id

        self.pulse = _Camera_pulse(0, serial_com)
        self.period = _Camera_period(0, serial_com)
        self.exposure = _Camera_exposure(0, serial_com)
        self.start = _Camera_start(0, serial_com)

    def set_pulse(self, value):
        return self.pulse.set_state(value)

    def get_pulse(self):
        return self.pulse.get_state()

    def set_period(self, value):
        return self.period.set_state(value)

    def get_period(self):
        return self.period.get_state()

    def set_exposure(self, value):
        return self.exposure.set_state(value)

    def get_exposure(self):
        return self.exposure.get_state()

    def start(self):
        return self.start.start()

    def stop(self):
        return self.start.stop()

    def is_running(self):
        return self.start.get_state()