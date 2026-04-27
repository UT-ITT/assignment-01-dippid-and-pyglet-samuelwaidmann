"""
DIPPID-based tilt controller for horizontal paddle movement.
Uses accelerometer["x"] and gyroscope["z"].
"""

from __future__ import annotations
from typing import Optional
from DIPPID import SensorUDP


class DippidTiltController:
    """
    Map DIPPID accelerometer + gyroscope data to horizontal paddle movement.
    """

    def __init__(
        self,
        port: int = 5700,
        accel_weight: float = 0.6,
        gyro_weight: float = 0.4,
        deadzone: float = 0.05,
        max_speed: float = 15.0,
    ) -> None:
        """
        :param port: UDP port to listen on.
        :param accel_weight: How much to rely on accelerometer vs gyroscope (0.0 to 1.0).
        :param gyro_weight: How much to rely on gyroscope vs accelerometer (0.0 to 1.0).
        :param deadzone: Minimum combined tilt required to move the paddle (ignore tiny, unintentional movements and sensor noise.).
        :param max_speed: Maximum horizontal speed of the paddle in pixels per frame at maximum tilt.
        """
        self.sensor = SensorUDP(port=port)
        self.accel_weight = accel_weight
        self.gyro_weight = gyro_weight
        self.deadzone = deadzone
        self.max_speed = max_speed

        self._filtered_tilt = 0.0  # filtered tilt value for smoother movement
        self._filter_alpha = 0.2  # smoothing factor for low-pass filter (0.0 = no smoothing, 1.0 = max smoothing)

    def _get_accel_x(self) -> Optional[float]:
        """Get the x-axis accelerometer value."""
        accel = self.sensor.get_value("accelerometer")
        if accel is None:
            return None
        try:
            return float(accel["x"])
        except Exception:
            return None

    def _get_gyro_z(self) -> Optional[float]:
        """Get the z-axis gyroscope value."""
        gyro = self.sensor.get_value("gyroscope")
        if gyro is None:
            return None
        try:
            return float(gyro["z"])
        except Exception:
            return None

    def _compute_raw_tilt(self) -> float:
        """Combine accelerometer and gyroscope data to compute a raw tilt value."""
        accel_x = self._get_accel_x() or 0.0
        gyro_z = self._get_gyro_z() or 0.0

        gyro_scaled = gyro_z * 0.05

        combined = self.accel_weight * accel_x + self.gyro_weight * gyro_scaled

        if abs(combined) < self.deadzone:
            return 0.0

        return combined

    def _filter_tilt(self, raw: float) -> float:
        """Apply a simple low-pass filter to smooth out the tilt value."""
        self._filtered_tilt = (
            self._filter_alpha * raw + (1 - self._filter_alpha) * self._filtered_tilt
        )
        return self._filtered_tilt

    def get_paddle_dx(self, window_width: int) -> float:
        """Compute horizontal paddle movement based on current sensor data."""
        raw = self._compute_raw_tilt()
        tilt = self._filter_tilt(raw)
        tilt = -max(-1.0, min(1.0, tilt))
        return tilt * self.max_speed

    def disconnect(self) -> None:
        """Clean up sensor connection."""
        self.sensor.disconnect()
