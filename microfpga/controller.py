from microfpga import signals
from microfpga import regint


class MicroFPGA:
    def __init__(self, n_laser=0, n_ttl=0, n_servo=0, n_pwm=0, n_ai=0):
        self._serial = regint.RegisterInterface()
        self.device = self._serial.get_device()

        self._lasers = []
        self._ttls = []
        self._servos = []
        self._pwms = []
        self._ais = []
        if self._serial.is_connected():

            self._version = self._serial.read(signals.ADDR_VER)
            self._id = self._serial.read(signals.ADDR_ID)
            self._triggering_mode = self._serial.read(signals.ADDR_TRIGGER_MODE)

            if (self._version == signals.CURR_VER) and (self._id == signals.ID_AU or self._id == signals.ID_CU):
                # instantiates lasers
                for i in range(n_laser):
                    self._lasers.append(signals.LaserTrigger(i, self._serial))

                # instantiates TTLs
                for i in range(n_ttl):
                    self._ttls.append(signals.Ttl(i, self._serial))

                # instantiates servos
                for i in range(n_servo):
                    self._servos.append(signals.Servo(i, self._serial))

                # instantiates pwms
                for i in range(n_pwm):
                    self._pwms.append(signals.Pwm(i, self._serial))

                # instantiates analog inputs
                if self._id == signals.ID_AU:
                    for i in range(n_ai):
                        self._ais.append(signals.Analog(i, self._serial))

                if self._triggering_mode:
                    self._camera = signals.Camera(self._serial)
            else:
                self.disconnect()
                if self._version != signals.CURR_VER:
                    raise Warning('Wrong version: expected ' + str(signals.CURR_VER) + \
                                  ', got ' + str(self._version) + '. The port has been disconnected')

                if self._id != signals.ID_AU and self._id != signals.ID_CU:
                    raise Warning('Wrong board id: expected ' + str(signals.ID_AU) + \
                                  ' (Au) or ' + str(signals.ID_CU) + ' (Cu), got ' + str(
                        self._id) + '. The port has been disconnected')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_connected():
            self.disconnect()

    def disconnect(self):
        self._serial.disconnect()

    def is_connected(self):
        return self._serial.is_connected()

    def get_number_lasers(self):
        return len(self._lasers)

    def get_number_ttls(self):
        return len(self._ttls)

    def get_number_servos(self):
        return len(self._servos)

    def get_number_pwms(self):
        return len(self._pwms)

    def get_number_analogs(self):
        return len(self._ais)

    def set_ttl_state(self, channel, value):
        if 0 <= channel < self.get_number_ttls():
            return self._ttls[channel].set_state(value)
        else:
            return False

    def get_ttl_state(self, channel):
        if 0 <= channel < self.get_number_ttls():
            return self._ttls[channel].get_state()
        else:
            return -1

    def set_servo_state(self, channel, value):
        if 0 <= channel < self.get_number_servos():
            return self._servos[channel].set_state(value)
        else:
            return False

    def get_servo_state(self, channel):
        if 0 <= channel < self.get_number_servos():
            return self._servos[channel].get_state()
        else:
            return -1

    def set_pwm_state(self, channel, value):
        if 0 <= channel < self.get_number_pwms():
            return self._pwms[channel].set_state(value)
        else:
            return False

    def get_pwm_state(self, channel):
        if 0 <= channel < self.get_number_pwms():
            return self._pwms[channel].get_state()
        else:
            return -1

    def get_analog_state(self, channel):
        if 0 <= channel < self.get_number_analogs():
            return self._ais[channel].get_state()
        else:
            return -1

    def set_mode_state(self, channel, value):
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].set_mode(value)
        else:
            return False

    def get_mode_state(self, channel):
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].get_mode()
        else:
            return -1

    def set_duration_state(self, channel, value):
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].set_duration(value)
        else:
            return False

    def get_duration_state(self, channel):
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].get_duration()
        else:
            return -1

    def set_sequence_state(self, channel, value):
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].set_sequence(value)
        else:
            return False

    def get_sequence_state(self, channel):
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].get_sequence()
        else:
            return -1

    def set_laser_state(self, channel, mode, duration, sequence):
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].set_state(mode, duration, sequence)
        else:
            return False

    def get_laser_state(self, channel):
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].get_state()
        else:
            return [-1, -1, -1]

    def set_camera_pulse(self, value):
        if self._triggering_mode:
            self._camera.set_pulse(value)

    def get_camera_pulse(self):
        if self._triggering_mode:
            return self._camera.get_pulse()
        else:
            return -1

    def set_camera_period(self, value):
        if self._triggering_mode:
            self._camera.set_period(value)

    def get_camera_period(self):
        if self._triggering_mode:
            return self._camera.get_period()
        else:
            return -1

    def set_camera_exposure(self, value):
        if self._triggering_mode:
            self._camera.set_exposure(value)

    def get_camera_exposure(self):
        if self._triggering_mode:
            return self._camera.get_exposure()
        else:
            return -1

    def set_camera_state(self, pulse, period, exposure):
        if self._triggering_mode:
            self._camera.set_state(pulse, period, exposure)

    def start_camera(self):
        if self._triggering_mode:
            self._camera.start()

    def stop_camera(self):
        if self._triggering_mode:
            self._camera.stop()

    def is_camera_running(self):
        if self._triggering_mode:
            return self._camera.is_running()
        else:
            return False

    def can_trigger_camera(self):
        return self._triggering_mode

    def get_id(self):
        if self._id == signals.ID_AU:
            return 'Au'
        elif self._id == signals.ID_CU:
            return 'Cu'
        else:
            return 'Unknown'
