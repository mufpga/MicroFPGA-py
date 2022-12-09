#!/usr/bin/env python
""" Demonstrate active camera synchronisation with an AOTF.

Note that MicroFPGA currently does not allow synchronization between the
camera and a PWM channel level, but only with the laser trigger channels.
In an experimental setting, we expect that the analog output level to the
AOTF would remain constant.

Requires the AOTF-CB. The camera output of the FPGA is used to trigger
a camera, and both PWM and laser trigger signals should be used as inputs
to the board. Its output can then be used to synchronize an AOTF with the
camera.
"""

import microfpga.controller as cl
import microfpga.signals as sig
from microfpga.signals import LaserTriggerMode
import time

# use_camera=True is the default value and can be omitted
with cl.MicroFPGA(n_laser=1, n_pwm=1) as mufpga:
    # check if successful
    if mufpga.is_connected():

        # print id
        print(f'Connected to {mufpga.get_id()}')

        # we are in camera-laser sync mode by default
        print(f'Active trigger synchronisation: {mufpga.is_active_sync()}')
        assert mufpga.is_active_sync()

        # then we need to set the camera state
        # we can do it in milliseconds, keeping in mind the following bounds:
        # max(pulse) = 0 to 1048,575 ms (in steps of 1 us)
        # max(delay) = 0 to 65.535 ms
        # max(exposure) = 0 to 1048,575 ms
        # max(readout) = 0 to 65.535 ms
        camera = {
            'pulse': 225,  # ms
            'delay': 0.5,  # delay of 500 us between camera pulse and start of the exposure
            'exposure': 225,
            'readout': 24.5,
        }
        mufpga.set_camera_state_ms(**camera)  # set the values in ms

        # print state
        print(mufpga.get_camera_state_ms())

        # define one "laser" pulsing on rising edge of the
        # camera trigger with pulse length 2000 us.
        laser0 = {
            'channel': 0,
            'mode': LaserTriggerMode.MODE_RISING,
            'duration': 200_000,  # in us
            'sequence': sig.MAX_SEQUENCE
        }
        mufpga.set_laser_state(**laser0)

        # set the initial value of the PWM
        pwm_val = 0
        mufpga.set_pwm_state(0, pwm_val)

        # let's define a sequence of PWM levels (max is 255)
        resolution = 5
        pwm_levels = [i * 255 // resolution for i in range(resolution+1)]

        # and prepare counters
        counter, increment = 0, 0
        counter_inc_steps = 4
        max_counter = counter_inc_steps * len(pwm_levels) * 2
        frame_time = camera['delay'] + camera['exposure'] + camera['readout']

        # we need to start the camera
        mufpga.start_camera()
        print('Camera running')

        # the pwm level is not synchronized with the camera, only the laser trigger is
        while counter < max_counter:

            if counter % counter_inc_steps == 0:
                # change pwm level
                pwm_val = pwm_levels[increment % len(pwm_levels)]
                mufpga.set_pwm_state(0, pwm_val)

                increment += 1

            # sleep for a frame
            time.sleep(frame_time / 1_000)  # in s

            counter += 1

        # stop, the trigger signals are off
        mufpga.stop_camera()
        print('Camera stopped')
    else:
        print('Failed to connected')

print('Disconnected')
