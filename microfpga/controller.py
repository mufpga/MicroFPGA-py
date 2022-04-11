""" High level module allowing to control MicroFPGA.

Upon instantiation, users can decide the number of signals (inputs/outputs and
parameters) to be used. Additionally, the possibility to use active
synchronization between the camera and lasers can also be set at
initialization.

In the case of a system with multiple compatible FPGA, or with FTDI drivers
creating multiple ports for the FPGA, a warning is emitting listing each
compatible port found on the system. Users can pass on the port name to
select to which USB port to connect.
"""
import warnings
from microfpga import signals
from microfpga import regint
from microfpga.signals import ActiveParameters


# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches
# pylint: disable=too-many-public-methods


class MicroFPGA:
    """ MicroFPGA controller.

    Upon instantiation, users can decide the number of signals (inputs/outputs
    and parameters) to be used. Additionally, the possibility to use active
    synchronization between the camera and lasers can also be set at
    initialization.

    In the case of a system with multiple compatible FPGA, or with FTDI
    drivers creating multiple ports for the FPGA, a warning is emitting
    listing each compatible port found on the system. Users can pass on the
    port name to select to which USB port to connect.
    """
    def __init__(
            self,
            n_laser=0,
            n_ttl=0,
            n_servo=0,
            n_pwm=0,
            n_ai=0,
            use_camera=True,
            known_device=None,
    ):
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

            if (
                    self._version == signals.CURR_VER
            ) and self._id in signals.get_compatible_ids():
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
                    warnings.warn(
                        f"Wrong version: expected {str(signals.CURR_VER)}, "
                        f"got {str(self._version)}. The port has been "
                        f"disconnected"
                    )

                if self._id not in signals.get_compatible_ids():
                    warnings.warn(
                        f"Wrong board id: expected {signals.ID_MOJO} (Mojo),"
                        f" {signals.ID_CU} (Cu), {signals.ID_AU} (Au) or"
                        f" {signals.ID_AUP} (Au+),"
                        f" got {self._id}. The port has been disconnected"
                    )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_connected():
            self.disconnect()

    def disconnect(self):
        """ Disconnect for the connected device.

        :return:
        """
        if self.is_connected():
            self._serial.disconnect()
            self.is_connected()

    def is_connected(self):
        """ Check if the controller is connected to a device.

        :return: True if it is, False otherwise.
        """
        return self._serial.is_connected()

    def get_number_lasers(self):
        """ Return the number of laser channels.

        :return: number of laser channels.
        """
        return len(self._lasers)

    def get_number_ttls(self):
        """ Return the number of TTL channels.

        :return: number of TTL channels.
        """
        return len(self._ttls)

    def get_number_servos(self):
        """ Return the number of servo channels.

        :return: number of servo channels.
        """
        return len(self._servos)

    def get_number_pwms(self):
        """ Return the number of PWM channels.

        :return: number of PWM channels.
        """
        return len(self._pwms)

    def get_number_analogs(self):
        """ Return the number of analog input channels.

        :return: number of analog input channels.
        """
        return len(self._ais)

    def set_ttl_state(self, channel, value):
        """ Set the state of the specified TTL channel to a new value.

        :param channel: TTL channel.
        :param value: new value.
        :return: True if the request was sent, False if disconnected.
        """
        if 0 <= channel < self.get_number_ttls():
            return self._ttls[channel].set_state(value)
        return False

    def get_ttl_state(self, channel):
        """ Get the current state of the specified TTL channel.

        :param channel: TTL channel.
        :return: TTL state.
        """
        if 0 <= channel < self.get_number_ttls():
            return self._ttls[channel].get_state()
        return -1

    def set_servo_state(self, channel, value):
        """ Set the state of the specified servo channel to a new value.

        :param channel: servo channel.
        :param value: new value.
        :return: True if the request was sent, False if disconnected.
        """
        if 0 <= channel < self.get_number_servos():
            return self._servos[channel].set_state(value)
        return False

    def get_servo_state(self, channel):
        """ Get the current state of the specified servo channel.

        :param channel: servo channel.
        :return: servo state.
        """
        if 0 <= channel < self.get_number_servos():
            return self._servos[channel].get_state()
        return -1

    def set_pwm_state(self, channel, value):
        """ Set the state of the specified PWM channel to a new value.

        :param channel: PWM channel.
        :param value: new value.
        :return: True if the request was sent, False if disconnected.
        """
        if 0 <= channel < self.get_number_pwms():
            return self._pwms[channel].set_state(value)
        return False

    def get_pwm_state(self, channel):
        """ Get the current state of the specified PWM channel.

        :param channel: PWM channel.
        :return: PWM state.
        """
        if 0 <= channel < self.get_number_pwms():
            return self._pwms[channel].get_state()
        return -1

    def get_analog_state(self, channel):
        """ Get the latest measurement of the analog input specified channel.

        :param channel: analog channel
        :return: voltage measurement.
        """
        if 0 <= channel < self.get_number_analogs():
            return self._ais[channel].get_state()
        return -1

    def set_mode_state(self, channel, value):
        """ Return the trigger mode of the specified channel.

        The triggering mode is a discrete value between 0 and 4, where 0=off,
        1=on, 2=rising, 3=falling and 4=follow.

        :param channel: laser channel.
        :param value: new mode.
        :return: True if the request was sent, False if disconnected.
        """
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].set_mode(value)
        return False

    def get_mode_state(self, channel):
        """ Set the trigger mode of the specified channel.

        The triggering mode is a discrete value between 0 and 4, where 0=off,
        1=on, 2=rising, 3=falling and 4=follow.

        :param channel: laser channel.
        :return: triggering mode.
        """
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].get_mode()
        return -1

    def set_duration_us(self, channel, value):
        """ Set the pulse duration (us) of the specified channel.

        The duration is the pulse length of the trigger in rising and falling
        modes.

        :param channel: laser channel
        :param value: duration value in us.
        :return: True if the request was sent, False if disconnected.
        """
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].set_duration(value)
        return False

    def get_duration_us(self, channel):
        """ Get the pulse duration (us) of the specified channel.

        The duration is the pulse length of the trigger in rising and falling
        modes.

        :param channel: laser channel
        :return: duration value in us.
        """
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].get_duration()
        return -1

    def set_sequence_state(self, channel, value):
        """ Set the sequence of the specified channel to a new value.

        The sequence is a 16 bit-long sequence representing a pattern of frame
        on which to trigger the laser, where the laser is only triggered on
        1's and the trigger is skipped on 0's.

        :param channel: laser channel.
        :param value: new value.
        :return: True if the request was sent, False if disconnected.
        """
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].set_sequence(value)
        return False

    def get_sequence_state(self, channel):
        """ Get the specified channel's current sequence state.

        The sequence is a 16 bit-long sequence representing a pattern of frame
        on which to trigger the laser, where the laser is only triggered on
        1's and the trigger is skipped on 0's.

        :param channel: laser channel
        :return: sequence value.
        """
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].get_sequence()
        return -1

    def set_laser_state(self, channel, mode, duration, sequence):
        """ Set the laser trigger parameters value for the specified channel.

        The laser trigger parameters are the following:
            - mode: triggering mode, a discrete value between 0 and 4, where
                0=off, 1=on, 2=rising, 3=falling and 4=follow.
            - duration: pulse length of the trigger in rising and falling
                modes.
            - sequence: 16 bit-long sequence representing a pattern of frame
                on which to trigger the laser, where the laser is only
                triggered on 1's and the trigger is skipped on 0's.

        :param channel: laser channel.
        :param mode: new trigger mode.
        :param duration: new pulse duration.
        :param sequence: new sequence.
        :return:
        """
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].set_state(mode, duration, sequence)
        return False

    def get_laser_state(self, channel):
        """ Return a list of the laser trigger parameters value for the
        specified channel.

        The laser trigger parameters are the following:
            - mode: triggering mode, a discrete value between 0 and 4, where
                0=off, 1=on, 2=rising, 3=falling and 4=follow.
            - duration: pulse length of the trigger in rising and falling
                modes.
            - sequence: 16 bit-long sequence representing a pattern of frame
                on which to trigger the laser, where the laser is only
                triggered on 1's and the trigger is skipped on 0's.

        :return: list of parameters value [mde, duration, sequence].
        """
        if 0 <= channel < self.get_number_lasers():
            return self._lasers[channel].get_state()
        return [-1, -1, -1]

    def _get_sync_mode(self):
        if self._sync_mode is None:
            return False
        return self._sync_mode.get_state()

    def is_active_sync(self):
        """ Check if the FPGA is in active synchronization mode.

        :return: True if it is, False otherwise.
        """
        return self._get_sync_mode()

    def set_camera_pulse(self, value):
        """ Set the camera pulse (us) to a new value.

        The camera pulse is the pulse duration of the fire signal used to
        trigger a camera. Note that if the camera is set to a mode where the
        effective exposure is the pulse length of the triggering signal, then
        the pulse encodes the exposure. The camera exposure parameter
        available in MicroFPGA is the pulse length of an internal exposure
        signal and only affect the laser triggers.

        :return:
        """
        if self._get_sync_mode():
            self._camera.set_pulse(value)

    def get_camera_pulse(self):
        """ Return the camera pulse in us.

        The camera pulse is the pulse duration of the fire signal used to
        trigger a camera. Note that if the camera is set to a mode where the
        effective exposure is the pulse length of the triggering signal, then
        the pulse encodes the exposure. The camera exposure parameter
        available in MicroFPGA is the pulse length of an internal exposure
        signal and only affect the laser triggers.

        :return: pulse (us)
        """
        if self._get_sync_mode():
            return self._camera.get_pulse()
        return -1

    def set_camera_readout(self, value):
        """ Set the camera read-out (us) to a new value.

        The camera read-out corresponds to the delay between the end of the
        exposure and the beginning of the next frame.

        :return:
        """
        if self._get_sync_mode():
            self._camera.set_readout(value)

    def get_camera_readout(self):
        """ Return the camera read-out in us.

        The camera read-out corresponds to the delay between the end of the
        exposure and the beginning of the next frame.

        :return: read-out (us)
        """
        if self._get_sync_mode():
            return self._camera.get_readout()
        return -1

    def set_camera_exposure(self, value):
        """ Set the camera exposure (us) to a new value.

        The camera exposure corresponds to the maximum trigger duration of the
        lasers in rising, falling and follow modes. Note that if the effective
        camera trigger is encoded in the fire signal pulse length, then the
        relevant parameter is the pulse parameter.

        :return:
        """
        if self._get_sync_mode():
            self._camera.set_exposure(value)

    def get_camera_exposure(self):
        """ Return the camera exposure (us).

        The camera exposure corresponds to the maximum trigger duration of the
        lasers in rising, falling and follow modes. Note that if the effective
        camera trigger is encoded in the fire signal pulse length, then the
        relevant parameter is the pulse parameter.

        :return: exposure (us)
        """
        if self._get_sync_mode():
            return self._camera.get_exposure()
        return -1

    def set_laser_delay(self, value):
        """ Set the delay (us) between camera and laser trigger.

        :return:
        """
        if self._get_sync_mode():
            self._camera.set_delay(value)

    def get_laser_delay(self):
        """ Return the delay (us) between camera and laser trigger.

        :return: delay (us)
        """
        if self._get_sync_mode():
            return self._camera.get_delay()
        return -1

    def set_camera_state(
            self,
            pulse: int,
            delay: int,
            exposure: int,
            readout: int
    ):
        """
        Set the state of the camera trigger module in arbitrary units. The
        camera trigger module generates a periodic signal consisting of a
        pulse of length <pulse> (in us), repeating every <delay + exposure +
        readout> (in us). The module also generates a laser trigger signal
        that is then processed by the laser trigger module. The laser trigger
        signal follows the camera fire signal, but is delayed by <delay> (in
        us) and has a pulse length of <exposure> (in us).

        :param pulse: fire pulse length of the camera trigger signal in us
            (maximum = 1.048575 s).
        :param exposure: camera exposure used to generate a "fire" signal to
            the lasers in us (maximum = 1.048575 s).
        :param delay: delay between the start of the camera pulse and the
            start of the exposure in us (maximum = 65.535 ms).
        :param readout: period in us between the end of the exposure and the
            next fire pulse (maximum = 65.535 ms).
        """
        if self._get_sync_mode():
            self._camera.set_state(pulse, delay, exposure, readout)

    def get_camera_state(self):
        """
        Return the parameters of the camera trigger module in us.
        :return: State of the camera trigger module
        """
        return self._camera.get_state()

    def set_camera_state_ms(
            self, pulse: float, delay: float, exposure: float, readout: float
    ):
        """
        Set the state of the camera trigger module in ms.

        :param pulse: fire pulse length of the camera trigger signal in us
            (maximum = 1.048575 s).
        :param exposure: camera exposure used to generate a "fire" signal to
            the lasers in us (maximum = 1.048575 s).
        :param delay: delay between the start of the camera pulse and the
            start of the exposure in us (maximum = 65.535 ms).
        :param readout: period in us between the end of the exposure and the
            next fire pulse (maximum = 65.535 ms).
        """
        if self._get_sync_mode():
            pulse_ms = int(pulse * 1_000)
            readout_ms = int(readout * 1_000)
            exposure_ms = int(exposure * 1_000)
            delay_ms = int(delay * 1_000)

            self._camera.set_state(
                pulse_ms,
                delay_ms,
                exposure_ms,
                readout_ms
            )

    def get_camera_state_ms(self):
        """
        Return the parameters of the camera trigger module in ms.
        :return: State of the camera trigger module
        """
        state = self._camera.get_state()
        state[ActiveParameters.PULSE.value] = (
            state[ActiveParameters.PULSE.value] / 1_000.0
        )
        state[ActiveParameters.DELAY.value] = (
            state[ActiveParameters.DELAY.value] / 1_000.0
        )
        state[ActiveParameters.EXPOSURE.value] = (
            state[ActiveParameters.EXPOSURE.value] / 1_000.0
        )
        state[ActiveParameters.READOUT.value] = (
            state[ActiveParameters.READOUT.value] / 1_000.0
        )

        return state

    def start_camera(self):
        """ Start camera triggering and synchronization.

        This method only has effect in active synchronization mode.
        """
        if self._get_sync_mode():
            self._camera.start()

    def stop_camera(self):
        """ Stop camera triggering and synchronization.

        This method only has effect in active synchronization mode.
        """
        if self._get_sync_mode():
            self._camera.stop()

    def is_camera_running(self):
        """ Check if the camera is currently being triggered and synced with
        the lasers.

        :return: True if it is running, False otherwise.
        """
        if self._get_sync_mode():
            return self._camera.is_running()

        return False

    def set_active_sync(self):
        """ Set the FPGA to active synchronization.

        In active synchronization, the FPGA generates a fire signal intended
        for a camera and an internal exposure signal used to trigger the
        lasers.
        """
        if self._sync_mode is not None:
            self._sync_mode.set_active_sync()

    def set_passive_sync(self):
        """ Set the FPGA to passive synchronization.

        In passive synchronization, the FPGA receives an external exposure
        signal (generated from a camera) and processes it to trigger the
        lasers.
        """
        if self._sync_mode is not None:
            self._sync_mode.set_passive_sync()

    def get_id(self):
        """ Return human-readable id.

        :return: FPGA id.
        """
        if self._id == signals.ID_AU:
            return "Au"

        if self._id == signals.ID_AUP:
            return "Au+"

        if self._id == signals.ID_CU:
            return "Cu"

        if self._id == signals.ID_MOJO:
            return "Mojo"

        return "Unknown"
