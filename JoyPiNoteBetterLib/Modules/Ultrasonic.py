import time

import RPi.GPIO as GPIO

from ..Shared.SharedGpio import getSharedGpio, releaseSharedGpio, setupPin


class UltrasonicSensor:
    """Ultrasonic distance sensor (HC-SR04) using GPIO.

    Measures distance by sending ultrasonic pulses and measuring
    the time for the echo to return. Uses shared GPIO for efficient
    resource management.

    Attributes:
        triggerPin: GPIO pin for trigger signal output.
        echoPin: GPIO pin for echo signal input.
    """

    def __init__(self, triggerPin: int = 16, echoPin: int = 26) -> None:
        """Initialize the ultrasonic sensor.

        Args:
            triggerPin: GPIO pin for trigger signal (default 16).
            echoPin: GPIO pin for echo signal (default 26).
        """
        self.triggerPin = triggerPin
        self.echoPin = echoPin
        getSharedGpio()
        setupPin(self.triggerPin, GPIO.OUT)
        setupPin(self.echoPin, GPIO.IN)

    def getDistance(self, timeout: float = 0.04) -> float:
        """Measure distance using the ultrasonic sensor.

        Args:
            timeout: Maximum time to wait for echo in seconds (default 0.04).
                    This corresponds to ~6.8m max distance.

        Returns:
            Distance in centimeters, or -1.0 if timeout occurred.
        """
        # Send a 10us pulse to trigger the measurement
        self.sendTriggerPulse()

        pulseStart = time.time()
        pulseEnd = pulseStart
        startTime = pulseStart

        # Wait for the echo start with timeout
        while GPIO.input(self.echoPin) == GPIO.LOW:
            pulseStart = time.time()
            if pulseStart - startTime > timeout:
                return -1.0

        # Wait for the echo end with timeout
        while GPIO.input(self.echoPin) == GPIO.HIGH:
            pulseEnd = time.time()
            if pulseEnd - pulseStart > timeout:
                return -1.0

        # Calculate pulse duration
        pulse_duration = pulseEnd - pulseStart

        # Calculate distance (speed of sound is 34300 cm/s)
        distance = (pulse_duration * 34300) / 2

        return distance

    def sendTriggerPulse(self) -> None:
        """Send a trigger pulse to the ultrasonic sensor."""
        GPIO.output(self.triggerPin, GPIO.LOW)
        time.sleep(0.000002)
        GPIO.output(self.triggerPin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.triggerPin, GPIO.LOW)

    def waitForEcho(self, timeout: float = 0.02) -> bool:
        """Wait for the echo signal with a timeout.

        Args:
            timeout: Maximum time to wait for the echo in seconds.
        Returns:
            True if echo received, False if timeout occurred.
        """
        startTime = time.time()
        while GPIO.input(self.echoPin) == GPIO.LOW:
            if (time.time() - startTime) > timeout:
                return False
        return True

    def __del__(self):
        """Release GPIO reference on object deletion."""
        releaseSharedGpio()
