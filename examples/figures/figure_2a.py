#!/usr/bin/env python
""" Set a single laser in camera mode.

A camera trigger signal must be used as input to the FPGA. The
first laser trigger signal (laser0) is then generated by the
FPGA and follows the camera trigger input.
"""

import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode


with cl.MicroFPGA(n_laser=1, use_camera=False) as mufpga:

    # check if successful
    if mufpga.is_connected():

        # set laser state
        laser = {
            'channel': 0,
            'mode': LaserTriggerMode.MODE_FOLLOW,
            'duration': 65535,
            'sequence': sig.MAX_SEQUENCE
        }
        mufpga.set_laser_state(**laser)

        # read laser state
        print(f'Current Laser 0 state: {mufpga.get_laser_state(0)}')

    else:
        print('Failed to connect')
