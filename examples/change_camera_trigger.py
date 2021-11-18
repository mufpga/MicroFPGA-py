#!/usr/bin/env python
"""
Change camera trigger mode.
"""

import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode, CameraTriggerMode
import time

# use_camera=True and default_trigger=True are the defaults and could be omitted
with cl.MicroFPGA(n_laser=1, use_camera=True) as mufpga:
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
                'pulse': 1,  # ms
                'period': 50,
                'exposure': 40,
                'delay': 0.5  # delay of 500 us between pulse and start of the exposure
            }
            mufpga.set_camera_state_ms(**camera)  # set the values in ms

            # define three lasers pulsing on rising edge of the camera trigger
            # with pulse lengths 1, 2 and 3 us.
            laser0 = {
                'channel': 0,
                'mode': LaserTriggerMode.MODE_RISING,
                'duration': 1,
                'sequence': sig.MAX_SEQUENCE
            }

            # set the laser states
            mufpga.set_laser_state(**laser0)

            # we also need to start the camera
            mufpga.start_camera()
            print('Camera running')

            # now the FPGA generates both camera and laser trigger for 2 s
            time.sleep(2)  # in s

            # stop, the trigger signals are off
            mufpga.stop_camera()
            print('Camera stopped')

        # change camera trigger mode to passive: the lasers are now triggered
        # by an external trigger signal, they keep their triggering parameters
        # (mode, duration, sequence)
        mufpga.set_passive_trigger()

    else:
        print('Failed to connected')
