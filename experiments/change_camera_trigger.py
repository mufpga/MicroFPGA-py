#!/usr/bin/env python
""" Change camera trigger mode.
"""

import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode, CameraTriggerMode
import time

# use_camera=True and default_trigger=True are the defaults and could be omitted
with cl.MicroFPGA(n_laser=1, use_camera=True, default_trigger=True) as mufpga:
    # check if successful
    if mufpga.is_connected():

        # if we are in camera trigger mode
        if mufpga.is_active_trigger():
            # then we need to set the camera states
            camera = {
                'pulse': 10,  # 10x100 us = 1 ms
                'period': 200,  # = 20 ms
                'exposure': 190  # = 19 ms
            }

            # define three lasers pulsing on rising edge of the camera trigger
            # with pulse lengths 1, 2 and 3 us.
            laser0 = {
                'channel': 0,
                'mode': LaserTriggerMode.MODE_CAMERA.value,
                'duration': 1,
                'sequence': sig.MAX_SEQUENCE
            }

            # set the laser states
            mufpga.set_laser_state(**laser0)

            # we also need to start the camera
            mufpga.start_camera()
            print('Camera running')

            time.sleep(2)  # 10 s

            # stop
            mufpga.stop_camera()
            print('Camera stopped')

        mufpga.set_camera_trigger_mode(CameraTriggerMode.PASSIVE.value)

    else:
        print('Failed to connected')
