#!/usr/bin/env python

import microfpga.controller as ctrl
import time


def current_milli_time():
    return round(time.time() * 1000)


def run_measurement(controller, channel, n):
    t = []
    r = []

    start = current_milli_time()
    for _ in range(n):
        r.append(controller.get_analog_state(channel))
        t.append(current_milli_time() - start)

    return t, r


with ctrl.MicroFPGA(n_ai=1) as mufpga:

    # checks if successful
    if mufpga.is_connected():
        print('Connected to ' + mufpga.get_id())

        t_ns, r_ns = run_measurement(mufpga, channel=0, n=100)
        print('Time (ms)', t_ns)
        print('Read-out value (a.u.)', r_ns)
    else:
        print('Failed to connected')

