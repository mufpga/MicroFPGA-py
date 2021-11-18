from microfpga import signals
from microfpga import regint


class MicroFPGA:
    def __init__(self, n_laser=0, n_ttl=0, n_servo=0, n_pwm=0, n_ai=0, use_camera=True):
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

            if (self._version == signals.CURR_VER) and (self._id == signals.ID_AU or self._id == signals.ID_CU):
                # instantiate lasers
                for i in range(n_laser):
                    self._lasers.append(signals.LaserTrigger(i, self._serial))

                # instantiate TTLs
                for i in range(n_ttl):
                    self._ttls.append(signals.Ttl(i, self._serial))

                # instantiate servos
                for i in range(n_servo):
                    self._servos.append(signals.Servo(i, self._serial))

                # instantiate pwms
                for i in range(n_pwm):
                    self._pwms.append(signals.Pwm(i, self._serial))

                # instantiate analog inputs
                if self._id == signals.ID_AU:
                    for i in range(n_ai):
                        self._ais.append(signals.Analog(i, self._serial))

                # instantiate camera
                if use_camera:
                    self._camera = signals.Camera(self._serial)
                    self._trigger_mode = signals.TriggerMode(self._serial)
                    self._trigger_mode.set_active_trigger()
                else:
                    self._camera = None
                    self._trigger_mode = None
                    signals.TriggerMode(self._serial).set_passive_trigger()

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

    def set_duration_us(self, channel, value):
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].set_duration(value)
        else:
            return False

    def get_duration_us(self, channel):
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

    def set_camera_trigger_mode(self, trigger_mode):
        if self._trigger_mode is None:
            return False
        else:
            return self._trigger_mode.set_state(trigger_mode)

    def get_trigger_mode(self):
        if self._trigger_mode is None:
            return False
        else:
            return self._trigger_mode.get_state()

    def is_active_trigger(self):
        return self.get_trigger_mode() == True

    def set_camera_pulse(self, value):
        if self.get_trigger_mode():
            self._camera.set_pulse(value)

    def get_camera_pulse(self):
        if self.get_trigger_mode():
            return self._camera.get_pulse()
        else:
            return -1

    def set_camera_period(self, value):
        if self.get_trigger_mode():
            self._camera.set_period(value)

    def get_camera_period(self):
        if self.get_trigger_mode():
            return self._camera.get_period()
        else:
            return -1

    def set_camera_exposure(self, value):
        if self.get_trigger_mode():
            self._camera.set_exposure(value)

    def get_camera_exposure(self):
        if self.get_trigger_mode():
            return self._camera.get_exposure()
        else:
            return -1

    def set_laser_delay(self, value):
        if self.get_trigger_mode():
            self._camera.set_delay(value)

    def get_laser_delay(self):
        if self.get_trigger_mode():
            return self._camera.get_delay()
        else:
            return -1

    def set_camera_state(self, pulse: int, period: int, exposure: int, delay: int):
        """
        Set the state of the camera trigger module in arbitrary units. The camera
        trigger module generates a periodic signal consisting of a pulse of length
        <pulse> (in steps of 100 us), repeating every <period> (in steps of 100 us).
        The module also generates a laser trigger signal that is then processed by the
        laser trigger module. The laser trigger signal follows the camera trigger signal,
        but is delayed by <delay> (in steps of 10 us) and has a pulse length of <exposure>
        (in steps of 100 us). If <delay>+<exposure> > <period> (in physical units), then
        <exposure> is shorten by the difference.

        :param pulse: pulse length of the camera trigger signal, in steps of 100 us.
        :param period: period of the camera trigger signal, in steps of 100 us.
        :param exposure: camera exposure used to generate a "fire" signal to the lasers,
         in steps of 100 us.
        :param delay: delay between the start of the camera pulse and the start of the
        exposure, in steps of 10 us.
        """
        if self.get_trigger_mode():
            self._camera.set_state(pulse, period, exposure, delay)

    def get_camera_state(self):
        """
        Return the parameters of the camera trigger module in arbitrary units.
        :return: State of the camera trigger module
        """
        return self._camera.get_state()

    def set_camera_state_ms(self, pulse: float, period: float, exposure: float, delay: float):
        """
        Set the state of the camera trigger module in ms. The camera
        trigger module generates a periodic signal consisting of a pulse of length
        <pulse>, repeating every <period>.
        The module also generates a laser trigger signal that is then processed by the
        laser trigger module. The laser trigger signal follows the camera trigger signal,
        but is delayed by <delay> and has a pulse length of <exposure>
        (in steps of 100 us). If <delay>+<exposure> > <period>, then
        <exposure> is shorten by the difference.

        :param pulse: pulse length of the camera trigger signal (maximum = 6553,5 ms).
        :param period: period of the camera trigger signal (maximum = 6553,5 ms).
        :param exposure: camera exposure used to generate a "fire" signal to the lasers
         (maximum = 6553,5 ms).
        :param delay: delay between the start of the camera pulse and the start of the
        exposure (maximum = 655,35 ms).
        """
        if self.get_trigger_mode():
            pulse_au = int(pulse * 10)
            period_au = int(period * 10)
            exposure_au = int(exposure * 10)
            delay_au = int(delay * 100)

            self._camera.set_state(pulse_au, period_au, exposure_au, delay_au)

    def get_camera_state_ms(self):
        """
        Return the parameters of the camera trigger module in ms.
        :return: State of the camera trigger module
        """
        state = self._camera.get_state()
        state['pulse'] = state['pulse'] / 10.
        state['period'] = state['period'] / 10.
        state['exposure'] = state['exposure'] / 10.
        state['delay'] = state['delay'] / 100.

        return state

    def start_camera(self):
        if self.get_trigger_mode():
            self._camera.start()

    def stop_camera(self):
        if self.get_trigger_mode():
            self._camera.stop()

    def is_camera_running(self):
        if self.get_trigger_mode():
            return self._camera.is_running()
        else:
            return False

    def set_active_trigger(self):
        self._trigger_mode.set_active_trigger()

    def set_passive_trigger(self):
        self._trigger_mode.set_passive_trigger()

    def get_id(self):
        if self._id == signals.ID_AU:
            return 'Au'
        elif self._id == signals.ID_AUP:
            return 'Au+'
        elif self._id == signals.ID_CU:
            return 'Cu'
        else:
            return 'Unknown'
