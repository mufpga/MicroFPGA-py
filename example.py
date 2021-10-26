import microfpga.controller as cl
import microfpga.signals as sig
import random as rd

# create a MicroFPGA controller, this will automatically disconnect at the end
with cl.MicroFPGA(n_lasers=3, n_ttls=2, n_servos=3, n_pwms=1, n_ais=2) as mufpga:
    # checks if successful
    print(f'Connected to {mufpga.get_id()}')

    # All signals can be accessed using the mufpga getters and setters.
    # Channel indexing starts at 0: if num_ttl = 2, then there are TTL 0 and
    # TTL 1.

    # get current Servo 1 state (if the FPGA was just recently powered up then default values are 0)
    servo_id = 1
    curr_servo_pos = mufpga.get_servo_state(servo_id)
    print(f'Current Servo {servo_id} position: {curr_servo_pos}')

    # move Servo 1 to another position
    servo_pos = rd.randint(1000, 65500)
    b = mufpga.set_servo_state(servo_id, servo_pos)
    if not b:
        print('Failed to write position to Servo 1')

    # get current Servo 1 state
    print(f'Current Servo {servo_id} position: {mufpga.get_servo_state(servo_id)}')

    # For lasers, the parameters can be changed individually...
    laser_id = 2
    new_mode = sig.LaserTrigger.MODE_RISING
    new_duration = 2000  # us
    new_sequence = sig.format_sequence('1010101010101010')  # binary string of length 16

    mufpga.set_mode(laser_id, new_mode)
    print(f'Current Laser {laser_id} mode: {mufpga.get_mode(laser_id)}')

    mufpga.set_duration(laser_id, new_duration)
    print(f'Current Laser {laser_id} duration: {mufpga.get_duration(laser_id)}')

    mufpga.set_sequence(laser_id, new_sequence)
    print(f'Current Laser {laser_id} sequence: {mufpga.get_sequence(laser_id)}')

    # ... or in bulk
    laser = {
        'channel': laser_id,
        'mode': sig.LaserTrigger.MODE_CAMERA,
        'duration': 1,
        'sequence': sig.MAX_SEQUENCE
    }
    mufpga.set_laser_state(**laser)
    print(f'Current Laser {laser_id} state: {mufpga.get_laser_state(laser_id)}')

    # read analog input
    analog_id = 0
    print(f'Analog channel {analog_id} value: {mufpga.get_analog_state(analog_id)}')
