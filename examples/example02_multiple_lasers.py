#!/usr/bin/env python
""" Use three lasers and change their parameters.

A camera trigger signal must be used as input to the FPGA. The
FPGA generates three laser trigger signals (laser0, laser1 and
laser2).
"""

import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode

# By default use_camera = True, here we use passive synchronization
with cl.MicroFPGA(n_laser=3, use_camera=False) as mufpga:

    # check if successful
    if mufpga.is_connected():

        # print id
        print(f'Connected to {mufpga.get_id()}')

        # check current state of the first laser
        # it prints [mode, duration, sequence]
        print(f'Current Laser 0 state: {mufpga.get_laser_state(0)}')
        print(f'Current Laser 1 state: {mufpga.get_laser_state(1)}')
        print(f'Current Laser 2 state: {mufpga.get_laser_state(2)}')

        # set lasers state
        laser0 = {
            'channel': 0,
            'mode': LaserTriggerMode.MODE_RISING,
            'duration': 2000,
            'sequence': sig.format_sequence('1010101010101010')
        }
        laser1 = {
            'channel': 1,
            'mode': LaserTriggerMode.MODE_FALLING,
            'duration': 2000,
            'sequence': sig.MAX_SEQUENCE  # sequence = 1111111111111111
        }
        laser2 = {
            'channel': 2,
            'mode': LaserTriggerMode.MODE_FOLLOW,
            'duration': 0,  # duration has no impact in FOLLOW mode
            'sequence': sig.format_sequence('1100110011001100')
        }
        mufpga.set_laser_state(**laser0)
        mufpga.set_laser_state(**laser1)
        mufpga.set_laser_state(**laser2)

        # read lasers state
        print(f'Current Laser 0 state: {mufpga.get_laser_state(0)}')
        print(f'Current Laser 1 state: {mufpga.get_laser_state(1)}')
        print(f'Current Laser 2 state: {mufpga.get_laser_state(2)}')

        assert [laser2['mode'].value,
                laser2['duration'],
                laser2['sequence']] == mufpga.get_laser_state(laser2['channel'])

    else:
        print('Failed to connect')

print('Disconnected')
