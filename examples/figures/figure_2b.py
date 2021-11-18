#!/usr/bin/env python
""" Demonstrate microsecond pulsing on three lasers.

A camera trigger signal must be used as input to the FPGA. The
FPGA generates three laser trigger signals (laser0, laser1 and
laser2). Those laser signals are short pulses of 1, 2 and 3 us,
respectively, on each rising edge of the camera input trigger.
"""

import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode, CameraTriggerMode


with cl.MicroFPGA(n_laser=3, use_camera=False, default_trigger=False) as mufpga:

    # check if successful
    if mufpga.is_connected():

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

    else:
        print('Failed to connected')
