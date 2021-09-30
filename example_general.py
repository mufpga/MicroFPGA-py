#!/usr/bin/env python

import microfpga.controller as ctl
import microfpga.signals as sig

# creates a MicroFPGA controller
num_lasers = 3
num_ttl = 2
num_servos = 3
num_pwm = 1
num_ai = 2  # will only work with Au FPGA

mufpga = ctl.MicroFPGA(num_lasers, num_ttl, num_servos, num_pwm, num_ai)

# checks if successful
if mufpga.is_connected():
    print('Connected to', mufpga.get_id())

    # All signals can be accessed using the controller getters and setters.
    # Channel indexing starts at 0: if num_ttl = 2, then there are TTL 0 and
    # TTL 1.

    # gets current Servo 1 state (if the FPGA was just recently powered up then default values are 0)
    servo_id = 1
    print('Servo', servo_id, 'current position:', mufpga.get_servo_state(servo_id))

    # moves Servo 1 to position 35412
    servo_pos = 35412
    print('Set servo', servo_id, 'position to', servo_pos)
    b = mufpga.set_servo_state(servo_id, servo_pos)
    if not b:
        print('Failed to write position to Servo 1')

    # gets current Servo 1 state
    print('Servo', servo_id, 'position:', mufpga.get_servo_state(servo_id))

    # For lasers, the parameters can be changed individually ...
    laser_id = 2
    new_mode = sig.LaserTrigger.MODE_RISING
    new_duration = 2000  # us
    new_sequence = sig.format_sequence('1010101010101010')  # binary string of length 16

    mufpga.set_mode_state(laser_id, new_mode)
    print('Laser', laser_id, 'mode state:', mufpga.get_mode_state(laser_id))

    mufpga.set_duration_state(laser_id, new_duration)
    print('Laser', laser_id, 'duration state:', mufpga.get_duration_state(laser_id))

    mufpga.set_sequence_state(laser_id, new_sequence)
    print('Laser', laser_id, 'sequence state:', mufpga.get_sequence_state(laser_id))

    # ... or in bulk
    new_state = {
        'channel': laser_id,
        'mode': sig.LaserTrigger.MODE_CAMERA,
        'duration': 30,
        'sequence': sig.format_sequence('1100110011001100')
    }
    mufpga.set_laser_state(**new_state)
    values = mufpga.get_laser_state(laser_id)
    print('Laser', laser_id, 'state:', values)

    # need to disconnect from the fpga
    mufpga.disconnect()
    print('Disconnected')

else:
    print('Failed to connect')
