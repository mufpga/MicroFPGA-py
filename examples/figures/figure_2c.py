#!/usr/bin/env python
""" Illustrate various laser trigger behaviours.

A camera trigger signal must be used as input to the FPGA. The
FPGA generates three laser trigger signals (laser0, laser1 and
laser2). The three laser signals have different behaviours. The
first laser signal (laser0) follows the camera signal but is
only triggered every two frames. Laser1 is pulsing for 2 ms on
the rising edges of the camera signal but only when laser0 is not
triggered. Finally, the laser laser is pulsing for 2 ms on the
falling edges of the camera signal for two frames and then is 0
for the next two frames, and so on.
"""

import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode, CameraTriggerMode


with cl.MicroFPGA(n_laser=3, use_camera=False) as mufpga:

    # check if successful
    if mufpga.is_connected():

        # set lasers state
        laser0 = {
            'channel': 0,
            'mode': LaserTriggerMode.MODE_FOLLOW,
            'duration': 1,
            'sequence': sig.format_sequence('1010101010101010')
        }
        laser1 = {
            'channel': 1,
            'mode': LaserTriggerMode.MODE_RISING,
            'duration': 4000,
            'sequence': sig.format_sequence('0101010101010101')
        }
        laser2 = {
            'channel': 2,
            'mode': LaserTriggerMode.MODE_FALLING,
            'duration': 2000,
            'sequence': sig.format_sequence('1100110011001100')
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
