import RPi.GPIO as GPIO

from ..Shared.SharedGpio import getSharedGpio, releaseSharedGpio, setupPin


class SoundSensor:
    """Sound sensor reader using shared GPIO handling.

    Uses the shared GPIO bus to reduce resource overhead and avoid conflicts
    when multiple GPIO-based components are used together.

    Attributes:
        pin: GPIO pin number (BCM mode).
    """

    def __init__(self, pin: int = 24) -> None:
        """Initialize the sound sensor.

        Args:
            pin: GPIO pin number in BCM mode (default 24).
        """
        self.pin = pin
        getSharedGpio()
        setupPin(self.pin, GPIO.IN)

    def isSoundDetected(self) -> bool:
        """Check if sound is detected by the sensor.

        Returns:
            bool: True if sound is detected, False otherwise.
        """
        return GPIO.input(self.pin) == GPIO.HIGH

    def __del__(self) -> None:
        """Release GPIO resources on object deletion."""
        releaseSharedGpio()
