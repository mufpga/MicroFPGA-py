#!/usr/bin/env python
""" Read analog signal value on a single channel.
"""
import microfpga.controller as cl
import microfpga.signals as sig
import time
import matplotlib.pyplot as plt


def current_milli_time():
    return time.time() * 1000


def run_measurement(controller, channel, n):
    t = []
    r = []

    start = current_milli_time()
    for _ in range(n):
        r.append(controller.get_analog_state(channel))
        t.append(current_milli_time() - start)

    return t, r


with cl.MicroFPGA(n_ai=1) as mufpga:
    # check if successful
    if mufpga.is_connected():
        print('Connected to ' + mufpga.get_id())

        t_ms, r_au = run_measurement(mufpga, channel=0, n=100)

        # result is returned in arbitrary unit, convert to volts
        v = [r / sig.MAX_AI for r in r_au]

        plt.plot(t_ms, v, '-o')
        plt.title('Channel0')
        plt.xlabel('t (ms)')
        plt.ylabel('voltage (V)')
        plt.show()

    else:
        print('Failed to connected')
