import RPi.GPIO as GPIO

from ..Shared.SharedGpio import getSharedGpio, releaseSharedGpio, setupPin


class TiltSensor:
    """Tilt sensor reader using shared GPIO handling.

    Uses the shared GPIO bus to reduce resource overhead and avoid conflicts
    when multiple GPIO-based components are used together.

    Attributes:
        pin: GPIO pin number (BCM mode).
    """

    def __init__(self, pin: int = 22):
        """Initialize the tilt sensor.

        Args:
            pin: GPIO pin number in BCM mode (default 22).
        """
        self.pin = pin
        getSharedGpio()
        setupPin(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def isTilted(self) -> bool:
        """Check if the tilt sensor is tilted.

        Returns:
            bool: True if tilted, False otherwise.
        """
        return GPIO.input(self.pin) == GPIO.HIGH

    def __del__(self):
        """Release GPIO reference on object deletion."""
        releaseSharedGpio()
