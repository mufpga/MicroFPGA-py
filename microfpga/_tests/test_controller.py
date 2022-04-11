""" Test if controller can be instantiated.
"""

from microfpga.controller import MicroFPGA


def test_instantiation_microfpga():
    """ Simply test if a controller can be instantiated in the absence of any
    device.

    This allows also knowing whether the dependencies create problems.

    :return:
    """
    MicroFPGA()
