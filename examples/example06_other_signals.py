#!/usr/bin/env python
""" Illustrate how to set the states of TTL, servo and PWM signals.
"""

import microfpga.controller as cl

with cl.MicroFPGA(n_ttl=2,
                  n_servo=2,
                  n_pwm=3,
                  use_camera=False) as mufpga:

    # check if successful
    if mufpga.is_connected():

        # print id
        print(f'Connected to {mufpga.get_id()}')

        # TTL signals have only two states: on (True) or off (False)
        ttl_id = 1 # let's use the second channel
        ttl_state = mufpga.get_ttl_state(ttl_id)
        print(f'Current TTL {ttl_id} state: {ttl_state}')

        # set it to the other state
        mufpga.set_ttl_state(ttl_id, (not ttl_state))
        print(f'Current TTL {ttl_id} state: {mufpga.get_ttl_state(ttl_id)}')

        # PWM signals go from 0 (0%) to 255 (100%), they can be used together
        # with a low-pass filter to create an analog output signal, or simply
        # directly used with certain devices (e.g. LED)
        pwm_id = 2  # let's use the third signal
        pwm_state = mufpga.get_pwm_state(pwm_id)
        print(f'Current PWM {pwm_id} state: {pwm_state}')

        # let's change the value
        pwm_state = (pwm_state+120) % 255  # make sure the value is not > 255
        mufpga.set_pwm_state(pwm_id, pwm_state)
        print(f'Current PWM {pwm_id} state: {mufpga.get_pwm_state(pwm_id)}')

        # Finally, servo signals are used to control servomotors and their value
        # is between 0 and 65535
        servo_id = 1  # let's use the second channel
        servo_state = mufpga.get_servo_state(servo_id)
        print(f'Current Servo {servo_id} state: {servo_state}')

        # let's change the value
        servo_state = (servo_state+25000) % 65535  # make sure the value is not > 65535
        mufpga.set_servo_state(servo_id, servo_state)
        print(f'Current Servo {servo_id} state: {mufpga.get_servo_state(servo_id)}')

    else:
        print('Failed to connect')

print('Disconnected')
