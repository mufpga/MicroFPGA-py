#!/usr/bin/env python
""" Demonstrate microsecond pulsing on three lasers (active trigger).

A camera trigger signal must be used as input to the FPGA. The
FPGA generates three laser trigger signals (laser0, laser1 and
laser2). Those laser signals are short pulses of 1, 2 and 3 us,
respectively, on each rising edge of the camera input trigger.
"""

import time
import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode


with cl.MicroFPGA(n_laser=3, use_camera=True) as mufpga:

    # check if successful
    if mufpga.is_connected():

        if mufpga.is_active_trigger():
            camera = {
                'pulse': 1.5,  # ms
                'period': 5,
                'exposure': 4,
                'delay': 0.1
            }
            mufpga.set_camera_state_ms(**camera)

            # print state
            print(mufpga.get_camera_state_ms())

            # set lasers state
            laser0 = {
                'channel': 0,
                'mode': LaserTriggerMode.MODE_RISING,
                'duration': 1,
                'sequence': sig.MAX_SEQUENCE
            }
            laser1 = {
                'channel': 1,
                'mode': LaserTriggerMode.MODE_RISING,
                'duration': 2,
                'sequence': sig.MAX_SEQUENCE
            }
            laser2 = {
                'channel': 2,
                'mode': LaserTriggerMode.MODE_RISING,
                'duration': 3,
                'sequence': sig.MAX_SEQUENCE
            }
            mufpga.set_laser_state(**laser0)
            mufpga.set_laser_state(**laser1)
            mufpga.set_laser_state(**laser2)

            # read lasers state
            print(f'Current Laser 0 state: {mufpga.get_laser_state(0)}')
            print(f'Current Laser 1 state: {mufpga.get_laser_state(1)}')
            print(f'Current Laser 2 state: {mufpga.get_laser_state(2)}')

            # run camera for 1 s
            mufpga.start_camera()
            print('Camera running')

            time.sleep(1)  # in s

            mufpga.stop_camera()
            print('Camera stopped')

    else:
        print('Failed to connect')
