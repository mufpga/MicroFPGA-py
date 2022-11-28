#!/usr/bin/env python
"""
Goal: capture transition between two states of the PWM.

AOTF board with PWM0 and Laser0 as inputs.
Oscilloscope with only analog signal output.

Record only the analog signal on the oscilloscope for about 6s.
The oscilloscope should show the analog signal go between different
levels.
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
                'mode': LaserTriggerMode.MODE_ON,
                'duration': 65535,
                'sequence': sig.MAX_SEQUENCE
            }
            mufpga.set_laser_state(**laser)

            # run camera
            mufpga.start_camera()
            print('Camera running')

            for i in range(1, 5):
                time.sleep(1)  # in s

                pwm_state = i * 255 // 4
                mufpga.set_pwm_state(0, pwm_state)

            mufpga.stop_camera()
            print('Camera stopped')

    else:
        print('Failed to connect')
