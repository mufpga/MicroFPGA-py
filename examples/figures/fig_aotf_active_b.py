#!/usr/bin/env python
"""
Goal: show the syncing of the analog signal with the laser input.

AOTF board with PWM0 and Laser0 as inputs.
Oscilloscope with Laser0 and AOTF board output.

Record the AOTF and Laser0 signals with a trigger on the Laser0, record
about 200 events.
"""

import time
import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode


with cl.MicroFPGA(n_laser=1, use_camera=True) as mufpga:

    # check if successful
    if mufpga.is_connected():

        if mufpga.is_active_sync():
            camera = {
                'pulse': 1.5,  # ms
                'delay': 0,
                'exposure': 9,
                'readout': 1
            }
            mufpga.set_camera_state_ms(**camera)

            # set PWM state
            pwm_state = 255 // 2
            mufpga.set_pwm_state(0, pwm_state)

            # set laser state
            laser = {
                'channel': 0,
                'mode': LaserTriggerMode.MODE_FOLLOW,
                'duration': 65535,
                'sequence': sig.MAX_SEQUENCE
            }
            mufpga.set_laser_state(**laser)

            # run camera for 1 s
            mufpga.start_camera()
            print('Camera running')

            time.sleep(1)  # in s

            mufpga.stop_camera()
            print('Camera stopped')

    else:
        print('Failed to connect')
