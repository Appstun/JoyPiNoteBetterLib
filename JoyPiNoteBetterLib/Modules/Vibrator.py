import time

import RPi.GPIO as GPIO

from ..Shared.SharedGpio import getSharedGpio, releaseSharedGpio, setupPin


class Vibrator:
    """Vibrator motor controller using GPIO.

    Controls a simple vibration motor connected to a GPIO pin.
    Supports timed vibration and manual on/off control.

    Attributes:
        pin: GPIO pin number where the vibrator motor is connected.
    """

    def __init__(self, pin: int = 27) -> None:
        """Initialize the vibrator motor on the specified GPIO pin.

        Args:
            pin (int): The GPIO pin number where the vibrator motor is connected.
        """
        self.pin = pin
        getSharedGpio()
        setupPin(self.pin, GPIO.OUT)

    def vibrate(self, duration: float = 1.0) -> None:
        """Activate the vibrator motor for a specified duration.

        Args:
            duration (float): Duration in seconds to activate the vibrator motor.
        """
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.pin, GPIO.LOW)

    def setVibrate(self, doVibrate: bool) -> None:
        """Activate or deactivate the vibrator motor.

        Args:
            doVibrate (bool): True to activate the vibrator motor, False to deactivate.
        """
        if doVibrate:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)

    def __del__(self) -> None:
        """Release GPIO resources on object deletion."""
        releaseSharedGpio()


class PwmVibrator:
    """Class to control a PWM vibrator motor connected to a GPIO pin."""

    def __init__(self, pin: int = 27, frequency: float = 100) -> None:
        """Initialize the PWM vibrator motor on the specified GPIO pin.

        Args:
            pin (int): The GPIO pin number where the vibrator motor is connected.
        """
        self.pin = pin
        getSharedGpio()
        setupPin(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, frequency)
        self.pwm.start(0)

    def setIntensity(self, duty_cycle: float) -> None:
        """Set the intensity of the vibrator motor using PWM.

        Args:
            duty_cycle (float): Duty cycle percentage (0 to 100) to set the intensity.
        """
        self.pwm.ChangeDutyCycle(duty_cycle)

    def stop(self) -> None:
        """Deactivate the vibrator motor."""
        self.pwm.ChangeDutyCycle(0)

    def __del__(self) -> None:
        """Release GPIO resources on object deletion."""
        releaseSharedGpio()
