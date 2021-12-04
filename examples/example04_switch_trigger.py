#!/usr/bin/env python
""" Demonstrate how to switch between active/passive trigger modes.
"""

import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode
import time

# use_camera=True is the default value and can be omitted
with cl.MicroFPGA(n_laser=1) as mufpga:
    # check if successful
    if mufpga.is_connected():

        # print id
        print(f'Connected to {mufpga.get_id()}')

        # we are in camera trigger mode by default
        print(f'Active camera trigger: {mufpga.is_active_trigger()}')

        # then we set the camera state
        camera = {
            'pulse': 1,  # ms
            'period': 21,
            'exposure': 19.5,
            'delay': 0.5  # delay of 500 us between camera pulse and start of the exposure
        }
        mufpga.set_camera_state_ms(**camera)  # set the values in ms

        # print state
        print(mufpga.get_camera_state_ms())

        # define one laser pulsing on rising edge of the
        # camera trigger with pulse length 2000 us.
        laser0 = {
            'channel': 0,
            'mode': LaserTriggerMode.MODE_RISING,
            'duration': 2000,  # in us
            'sequence': sig.MAX_SEQUENCE
        }
        mufpga.set_laser_state(**laser0)

        # we also need to start the camera
        mufpga.start_camera()
        print('Camera running')

        # now the FPGA generates both camera and laser trigger for 2 s
        time.sleep(2)  # in s

        # stop, the trigger signals are off
        mufpga.stop_camera()
        print('Camera stopped')

        # switch to passive triggering mode
        mufpga.set_passive_trigger()
        print(f'Active camera trigger: {mufpga.is_active_trigger()}')

        # and switch back
        mufpga.set_active_trigger()
        print(f'Active camera trigger: {mufpga.is_active_trigger()}')

    else:
        print('Failed to connected')

print('Disconnected')
