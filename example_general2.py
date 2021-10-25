#!/usr/bin/env python

import microfpga.controller as ctrl
import microfpga.signals as sig

with ctrl.MicroFPGA(n_laser=1, n_servo=3, n_ai=2) as mufpga:

    # check if successful
    if mufpga.is_connected():
        print('Connected to', mufpga.get_id())

        # check if the fpga is in active trigger mode
        print('Main trigger:', bool(mufpga.is_active_trigger()))

        # read analog channel 1
        print('Analog channel 1:', mufpga.get_analog_state(1))

        # set servo position
        print('Servo 2 position:', mufpga.get_servo_state(2))
        pos = 35500
        print('Set Servo 2 position to', pos)
        mufpga.set_servo_state(2, pos)
        print('Servo 2 position:', mufpga.get_servo_state(2))

        # set laser state
        new_state = {
            'channel': 0,
            'mode': sig.LaserTrigger.MODE_CAMERA,
            'duration': 30,
            'sequence': sig.format_sequence('1100110011001100')
        }
        mufpga.set_laser_state(**new_state)
        values = mufpga.get_laser_state(0)
        print('Laser state:', values)

    else:
        print('Failed to connect')

