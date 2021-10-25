#!/usr/bin/env python

import microfpga.controller as ctrl
import microfpga.signals as sig
import time

with ctrl.MicroFPGA(n_laser=3) as mufpga:

    # check if connected
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
            'mode': sig.LaserTrigger.MODE_RISING,
            'duration': 1,
            'sequence': sig.MAX_SEQUENCE
        }

        laser1 = {
            'channel': 1,
            'mode': sig.LaserTrigger.MODE_RISING,
            'duration': 2,
            'sequence': sig.MAX_SEQUENCE
        }

        laser2 = {
            'channel': 2,
            'mode': sig.LaserTrigger.MODE_RISING,
            'duration': 3,
            'sequence': sig.MAX_SEQUENCE
        }

        # set the laser states
        mufpga.set_laser_state(**laser0)
        mufpga.set_laser_state(**laser1)
        mufpga.set_laser_state(**laser2)

        # if we are in camera trigger mode
        if mufpga.is_active_trigger():
            # we also need to start the camera
            mufpga.start_camera()
            print('Camera running:', mufpga.is_camera_running())

            time.sleep(2)

            # stop
            mufpga.stop_camera()
            print('Camera running:', mufpga.is_camera_running())
    else:
        print('Failed to connect')
