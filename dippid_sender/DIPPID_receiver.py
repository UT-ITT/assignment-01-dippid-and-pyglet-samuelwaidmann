"""Receive DIPPID-style messages (accelerometer and button_1) via UDP and print them."""

from DIPPID import SensorUDP

PORT = 5700
sensor = SensorUDP(PORT)


def handle_accelerometer(data):
    """Print accelerometer values."""
    print(data)


def handle_button_press(data):
    """Print button press or release events."""
    if data == 0:
        print("button released")
    else:
        print("button pressed")


sensor.register_callback("accelerometer", handle_accelerometer)
sensor.register_callback("button_1", handle_button_press)
