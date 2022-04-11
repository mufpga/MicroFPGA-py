""" Unit tests for the static methods of microfpga.signal and for some
mechanisms of the signals.
"""
import pytest
from microfpga.signals import Signal, _Mode, LaserTriggerMode, format_sequence


class SignalTest(Signal):
    """ Test class for a Signal that allows dynamically setting the number of
    channels and maximum value for testing purposes.
    """
    def __init__(
        self,
        output=True,
        channel_id: int = 0,
        max_channels=1,
        max_value=404,
    ):
        self._address = 42

        if max_channels > 0:
            self._max_channels = max_channels
        else:
            self._max_channels = 1

        self._max_value = max_value

        Signal.__init__(self, channel_id, None, output)

    def get_address(self):
        return self._address

    def get_max(self):
        return self._max_value

    def get_num_signal(self):
        return self._max_channels

    def get_name(self):
        return "SignalTest"


@pytest.mark.parametrize("channel_id", [-1, 4])
def test_signal_channel_exception(channel_id):
    """ Test that requesting a channel with negative or larger than the
    channel size leads to an exception.

    :param channel_id: int value in the range [0, 3].
    :return:
    """
    with pytest.raises(Exception):
        SignalTest(channel_id=channel_id, max_channels=3)


@pytest.mark.parametrize("value", [0, 5, 10])
def test_signal_allowed_value(value):
    """ Test allowed values.

    :param value: int value in the range [0, 10].
    :return:
    """
    sig = SignalTest(max_value=10)
    assert sig.is_allowed(value)


@pytest.mark.parametrize("value", [-1, 11, 20])
def test_signal_disallowed_value(value):
    """ Test that out-of-range values are not allowed.

    :param value: out-of-range int values.
    :return:
    """
    sig = SignalTest(max_value=10)
    assert not sig.is_allowed(value)


@pytest.mark.parametrize("value", [0, 5, 10, 11, 20])
def test_readonly_signal_allowed_value(value):
    """ Test that values are not allowed for read-only signals.

    :param value: positive int signal value.
    :return:
    """
    sig = SignalTest(output=False, max_value=10)
    assert sig.is_read_only()
    assert not sig.is_allowed(value)


@pytest.mark.parametrize(
    "value", [1, LaserTriggerMode.MODE_ON, 3, LaserTriggerMode.MODE_FOLLOW]
)
def test_mode_value_and_enum(value):
    """ Test that both int and LaserTriggerMode enum can be passed as values
    to a _Mode parameter.

    :param value: int or LaserTriggerMode enum values
    :return:
    """
    mode = _Mode(0, None)

    assert mode.is_allowed(value)


@pytest.mark.parametrize(
    "incorrect_seq",
    [
        "010110011010010",
        "01010101100010100",
        "1010101010121010",
        "1010a01010101010",
        "_1t_w0rk5__ma73!",
    ],
)
def test_incorrect_format_sequence(incorrect_seq):
    """ Tests that incorrect sequences are formatted to -1.

    :param incorrect_seq: incorrect sequence
    :return:
    """
    assert format_sequence(incorrect_seq) == -1


@pytest.mark.parametrize(
    "sequence, value",
    [
        ("0000000000000000", 0),
        ("1111111111111111", 65535),
        ("1010101010101010", 43690),
        ("1100110011001100", 52428),
    ],
)
def test_format_sequence(sequence, value):
    """ Test whether format_sequence returns the correct value.

    :param sequence: 16 bit-long binary sequence
    :param value: corresponding int value
    :return:
    """
    assert format_sequence(sequence) == value
