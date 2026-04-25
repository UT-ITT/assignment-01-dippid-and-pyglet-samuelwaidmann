"""DIPPID accelerometer and button simulator sending UDP packets to localhost."""

import socket
import time
import math
import json


IP = "127.0.0.1"
PORT = 5700
DT = 2  # update rate


class AccelerometerSimulator:
    """Accelerometer simulator using simple sine waves."""

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


def main():
    """Send accelerometer and button data via UDP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    accel = AccelerometerSimulator()

    print(f"Sending accelerometer data to {IP}:{PORT}")

    while True:
        values = accel.get_values()
        message = json.dumps({"accelerometer": values})

        print(message)
        sock.sendto(message.encode(), (IP, PORT))

        time.sleep(DT)


if __name__ == "__main__":
    main()
