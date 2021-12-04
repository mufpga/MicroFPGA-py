#!/usr/bin/env python
""" Demonstrate active camera triggering with a single laser.

In active mode, the FPGA generates a camera trigger signal, as well as
an exposure signal. The camera trigger signal is an output of the
FPGA and can be directly connected to the external trigger of a camera.
The exposure signal generated is purely internal and is processed
by the laser trigger modules (see Example01 and Example02).

In addition to the laser trigger parameters, we need to set a number of
camera trigger parameters:
- pulse: pulse length in ms of the camera trigger signal, comprised
          between 0 and 6553.5 ms in steps of 0.1 ms.
- period: period in ms of the camera trigger signal, comprised
          between 0 and 6553.5 ms in steps of 0.1 ms.
- exposure: pulse length in ms of the exposure signal, the period is
            the same as the camera trigger signal, and the value is
             comprised between 0 and 6553.5 ms in steps of 0.1 ms.
- delay: delay in ms of the exposure signal with respect to the camera
        trigger rising edge, comprised between 0 and 655.35 ms in steps
        of 0.01 ms.

The signals therefore look like the following:
             <-------------period------------>
             <-pulse->
             ---------                        ---------      high
            |         |                      |         |
camera -----         ------------------------          ----- low

                  <---------exposure--------->
                  ---------------------------      ----------- high
                 |                           |    |
exposure --------                            -----            low
            <---> delay
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

        # then we need to set the camera state
        # we can do it in milliseconds, keeping in mind the following bounds:
        # max(pulse) = 0 to 6553,5 ms (in steps of 0.1 ms)
        # max(period) = 0 to 6553,5 ms
        # max(exposure) = 0 to 6553,5 ms
        # max(delay) = 0 to 655,35 ms <--- delay goes in steps of 0.01 ms
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

    else:
        print('Failed to connected')

print('Disconnected')
