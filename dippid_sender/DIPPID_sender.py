"""DIPPID accelerometer and button simulator sending UDP packets to localhost."""

import socket
import time
import math
import json
import random


IP = "127.0.0.1"
PORT = 5700
DT = 2  # update rate


class AccelerometerSimulator:
    """Simulate accelerometer using simple sine waves."""

    def __init__(self):
        """Initialize the simulator and store the start time."""
        self.start_time = time.time()

    def get_values(self):
        """Return simulated x, y, z accelerometer values."""
        t = time.time() - self.start_time

        return {
            "x": math.sin(2 * math.pi * 0.6 * t),
            "y": math.sin(2 * math.pi * 0.9 * t),
            "z": math.sin(2 * math.pi * 1.2 * t),
        }


class ButtonSimulator:
    """
    Simulate a button that is randomly pressed and released.
    """

    def __init__(self, initial_state=0, press_prob=0.2, release_prob=0.5):
        """Initialize the button simulator."""
        self.state = initial_state  # 0 = not pressed, 1 = pressed
        self.press_prob = press_prob
        self.release_prob = release_prob

    def update(self):
        if self.state == 0:
            # currently not pressed, press based on press probability
            if random.random() < self.press_prob:
                self.state = 1
        else:
            # currently pressed,release based on release probability
            if random.random() < self.release_prob:
                self.state = 0
        return self.state


def create_message(accel_values, button_state):
    """
    Create a JSON string compatible with DIPPID-style messages.
    Example:
    {
        "accelerometer": {"x": 0.1, "y": -0.2, "z": 0.9},
        "button_1": 1
    }
    """
    data = {"accelerometer": accel_values, "button_1": button_state}
    return json.dumps(data)


def main():
    """Send accelerometer and button data via UDP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    accel = AccelerometerSimulator()
    button = ButtonSimulator()

    print(f"Sending accelerometer data to {IP}:{PORT}")

    while True:
        accel_values = accel.get_values()
        button_state = button.update()
        message = create_message(accel_values, button_state)

        print(message)
        sock.sendto(message.encode(), (IP, PORT))

        time.sleep(DT)


if __name__ == "__main__":
    main()
