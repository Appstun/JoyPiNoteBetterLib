import time

import RPi.GPIO as GPIO

from ..Shared.SharedGpio import getSharedGpio, releaseSharedGpio, setupPin


class TouchSensor:
    """Touch sensor reader using shared GPIO handling.

    Uses the shared GPIO bus to reduce resource overhead and avoid conflicts
    when multiple GPIO-based components are used together.

    Attributes:
        pin: GPIO pin number (BCM mode).
    """

    def __init__(self, pin: int = 17):
        """Initialize the touch sensor.

        Args:
            pin: GPIO pin number in BCM mode (default 17).
        """
        self.pin = pin
        getSharedGpio()
        setupPin(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def waitForTouch(self, interval: float = 0.05) -> None:
        """Block until the sensor detects a touch.

        Polls the sensor at the specified interval until a touch is detected
        or the operation is interrupted by KeyboardInterrupt.

        Args:
            interval: Polling interval in seconds (default 0.05).
        """
        try:
            while not GPIO.input(self.pin):
                time.sleep(interval)
        except KeyboardInterrupt:
            pass

    def isTouched(self) -> bool:
        """Check if the sensor is currently being touched.

        Returns:
            True if touched, False otherwise.
        """
        return GPIO.input(self.pin) == GPIO.HIGH

    def __del__(self):
        """Release GPIO reference on object deletion."""
        releaseSharedGpio()
