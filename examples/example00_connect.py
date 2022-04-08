#!/usr/bin/env python
""" Simple script showing how to connect to the FPGA.
"""

import microfpga.controller as cl

# In unix systems (macOS and Linux), the FTDI driver creates two ports, since the name would depend on the system the
# module will not know to which device connect. In such a case, a warning is printed to the console and the connection
# fails. Here is how to connect:
#   1) The warning should print a list of available devices.
#   2) Choose from the list the port corresponding to channel 1 of the FPGA (examples: '/dev/ttyUSB1' or
#       '/dev/cu.usbserial-FT3KRFFN1').
#   3) Replace the 'with' statement with the following:
#
#       with cl.MicroFPGA(know_device=XXX) as mufpga:
#
#               where XXX is the port name
with cl.MicroFPGA() as mufpga:

    # check if successful
    if mufpga.is_connected():

        # print id
        print(f'Connected to {mufpga.get_id()}')

    else:
        print('Failed to connect')

print('Disconnected')


# # Alternatively, you can connect and disconnect yourself:
# mufpga = cl.MicroFPGA()

# if mufpga.is_connected():
#    print(f'Connected to {mufpga.get_id()}')

# # It is important to free the port by disconnecting
# mufpga.disconnect()
# print(f'Still connected? {mufpga.is_connected()}')
