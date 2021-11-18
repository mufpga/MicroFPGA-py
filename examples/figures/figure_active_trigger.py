#!/usr/bin/env python
""" Demonstrate active camera triggering with three lasers.
"""

import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode
import time

# use_camera=True is default and could be omitted
with cl.MicroFPGA(n_laser=3, use_camera=True) as mufpga:
    # check if successful
    if mufpga.is_connected():

        # if we are in camera trigger mode
        if mufpga.is_active_trigger():
            # then we need to set the camera state
            # we can do it in milliseconds, keeping in mind the following bounds:
            # max(pulse) = 0 to 6553,5 ms (in steps of 0.1 ms)
            # max(period) = 0 to 6553,5 ms
            # max(exposure) = 0 to 6553,5 ms
            # max(delay) = 0 to 655,35 ms <--- delay goes in steps of 0.01 ms
            camera = {
                'pulse': 1.4,  # ms
                'period': 21.5,
                'exposure': 20,
                'delay': 0.3  # delay of 300 us between camera pulse and start of the exposure
            }
            mufpga.set_camera_state_ms(**camera)  # set the values in ms

            # print state
            print(mufpga.get_camera_state_ms())

            # define three lasers.
            laser0 = {
                'channel': 0,
                'mode': LaserTriggerMode.MODE_FOLLOW,
                'duration': 1,
                'sequence': sig.MAX_SEQUENCE
            }
            laser1 = {
                'channel': 1,
                'mode': LaserTriggerMode.MODE_RISING,
                'duration': 6500,
                'sequence': sig.format_sequence('0101010101010101')
            }
            laser2 = {
                'channel': 2,
                'mode': LaserTriggerMode.MODE_FALLING,
                'duration': 1000,
                'sequence': sig.format_sequence('1010101010101010')
            }
            mufpga.set_laser_state(**laser0)
            mufpga.set_laser_state(**laser1)
            mufpga.set_laser_state(**laser2)

            # we also need to start the camera
            mufpga.start_camera()
            print('Camera running')

            # now the FPGA generates both camera and laser trigger for 2 s
            time.sleep(2)  # in s

            # stop, the trigger signals are off
            mufpga.stop_camera()
            print('Camera stopped')

    else:
        print('Failed to connected')
