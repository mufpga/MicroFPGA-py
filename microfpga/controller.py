from microfpga import signals
from microfpga import regint
from microfpga.signals import ActiveParameters
import warnings


class MicroFPGA:

    def __init__(self, n_laser=0, n_ttl=0, n_servo=0, n_pwm=0, n_ai=0, use_camera=True, known_device=None):
        self._serial = regint.RegisterInterface(known_device)
        self.device = self._serial.get_device()

        self._lasers = []
        self._ttls = []
        self._servos = []
        self._pwms = []
        self._ais = []
        if self._serial.is_connected():
            self._version = self._serial.read(signals.ADDR_VER)
            self._id = self._serial.read(signals.ADDR_ID)

            if (self._version == signals.CURR_VER) and \
                    self._id in signals.get_compatible_ids():
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
                if self._id in signals.get_analog_ids():
                    for i in range(n_ai):
                        self._ais.append(signals.Analog(i, self._serial))

                # instantiate camera
                if use_camera:
                    self._camera = signals.Camera(self._serial)
                    self._sync_mode = signals.SyncMode(self._serial)
                    self._sync_mode.set_active_sync()
                else:
                    self._camera = None
                    self._sync_mode = None
                    signals.SyncMode(self._serial).set_passive_sync()

            else:
                self.disconnect()

                if self._version != signals.CURR_VER:
                    warnings.warn('Wrong version: expected ' + str(signals.CURR_VER) + \
                                  ', got ' + str(self._version) + '. The port has been disconnected')

                if not (self._id in signals.get_compatible_ids()):
                    warnings.warn(f'Wrong board id: expected {signals.ID_MOJO} (Mojo),'
                                  f' {signals.ID_CU} (Cu), {signals.ID_AU} (Au) or'
                                  f' {signals.ID_AUP} (Au+),'
                                  f' got {self._id}. The port has been disconnected')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_connected():
            self.disconnect()

    def disconnect(self):
        if self.is_connected():
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

    def set_camera_sync_mode(self, sync_mode):
        if self._sync_mode is None:
            return False
        else:
            return self._sync_mode.set_state(sync_mode)

    def get_sync_mode(self):
        if self._sync_mode is None:
            return False
        else:
            return self._sync_mode.get_state()

    def is_active_sync(self):
        return self.get_sync_mode() == True

    def set_camera_pulse(self, value):
        if self.get_sync_mode():
            self._camera.set_pulse(value)

    def get_camera_pulse(self):
        if self.get_sync_mode():
            return self._camera.get_pulse()
        else:
            return -1

    def set_camera_readout(self, value):
        if self.get_sync_mode():
            self._camera.set_readout(value)

    def get_camera_readout(self):
        if self.get_sync_mode():
            return self._camera.get_readout()
        else:
            return -1

    def set_camera_exposure(self, value):
        if self.get_sync_mode():
            self._camera.set_exposure(value)

    def get_camera_exposure(self):
        if self.get_sync_mode():
            return self._camera.get_exposure()
        else:
            return -1

    def set_laser_delay(self, value):
        if self.get_sync_mode():
            self._camera.set_delay(value)

    def get_laser_delay(self):
        if self.get_sync_mode():
            return self._camera.get_delay()
        else:
            return -1

    def set_camera_state(self, pulse: int, delay: int, exposure: int, readout: int):
        """
        Set the state of the camera trigger module in arbitrary units. The camera
        trigger module generates a periodic signal consisting of a pulse of length
        <pulse> (in us), repeating every <delay+exposure+readout> (in us).
        The module also generates a laser trigger signal that is then processed by the
        laser trigger module. The laser trigger signal follows the camera fire signal,
        but is delayed by <delay> (inus) and has a pulse length of <exposure> (in us).

        :param pulse: fire pulse length of the camera trigger signal in us (maximum = 1.048575 s).
        :param exposure: camera exposure used to generate a "fire" signal to the lasers
         in us (maximum = 1.048575 s).
        :param delay: delay between the start of the camera pulse and the start of the
        exposure in  us  (maximum = 65.535 ms).
        :param readout: period in us between the end of the exposure and the next fire pulse
         (maximum = 65.535 ms).
        """
        if self.get_sync_mode():
            self._camera.set_state(pulse, delay, exposure, readout)

    def get_camera_state(self):
        """
        Return the parameters of the camera trigger module in us.
        :return: State of the camera trigger module
        """
        return self._camera.get_state()

    def set_camera_state_ms(self, pulse: float, delay: float, exposure: float, readout: float):
        """
        Set the state of the camera trigger module in ms.

        :param pulse: fire pulse length of the camera trigger signal in us (maximum = 1.048575 s).
        :param exposure: camera exposure used to generate a "fire" signal to the lasers
         in us (maximum = 1.048575 s).
        :param delay: delay between the start of the camera pulse and the start of the
        exposure in  us  (maximum = 65.535 ms).
        :param readout: period in us between the end of the exposure and the next fire pulse
         (maximum = 65.535 ms).
        """
        if self.get_sync_mode():
            pulse_ms = int(pulse * 1_000)
            readout_ms = int(readout * 1_000)
            exposure_ms = int(exposure * 1_000)
            delay_ms = int(delay * 1_000)

            self._camera.set_state(pulse_ms, delay_ms, exposure_ms, readout_ms)

    def get_camera_state_ms(self):
        """
        Return the parameters of the camera trigger module in ms.
        :return: State of the camera trigger module
        """
        state = self._camera.get_state()
        state[ActiveParameters.PULSE.value] = state[ActiveParameters.PULSE.value] / 1_000.
        state[ActiveParameters.DELAY.value] = state[ActiveParameters.DELAY.value] / 1_000.
        state[ActiveParameters.EXPOSURE.value] = state[ActiveParameters.EXPOSURE.value] / 1_000.
        state[ActiveParameters.READOUT.value] = state[ActiveParameters.READOUT.value] / 1_000.

        return state

    def start_camera(self):
        if self.get_sync_mode():
            self._camera.start()

    def stop_camera(self):
        if self.get_sync_mode():
            self._camera.stop()

    def is_camera_running(self):
        if self.get_sync_mode():
            return self._camera.is_running()
        else:
            return False

    def set_active_sync(self):
        if self._sync_mode is not None:
            self._sync_mode.set_active_sync()

    def set_passive_sync(self):
        if self._sync_mode is not None:
            self._sync_mode.set_passive_sync()

    def get_id(self):
        if self._id == signals.ID_AU:
            return 'Au'
        elif self._id == signals.ID_AUP:
            return 'Au+'
        elif self._id == signals.ID_CU:
            return 'Cu'
        elif self._id == signals.ID_MOJO:
            return 'Mojo'
        else:
            return 'Unknown'
