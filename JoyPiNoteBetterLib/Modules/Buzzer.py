import time

import RPi.GPIO as GPIO

from ..Shared.SharedGpio import getSharedGpio, releaseSharedGpio, setupPin


class Buzzer:
    """Class to control a buzzer connected to a GPIO pin."""

    def __init__(self, pin: int = 18):
        """Initialize the buzzer on the specified GPIO pin.

        Args:
            pin (int): The GPIO pin number where the buzzer is connected.
        """
        self.pin = pin
        getSharedGpio()
        setupPin(self.pin, GPIO.OUT)

    def buzz(self, duration: float = 1.0) -> None:
        """Activate the buzzer for a specified duration.

        Args:
            duration (float): Duration in seconds to activate the buzzer.
        """
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.pin, GPIO.LOW)

    def setBuzz(self, doBuzz: bool) -> None:
        """Activate or deactivate the buzzer.

        Args:
            doBuzz (bool): True to activate the buzzer, False to deactivate.
        """
        if doBuzz:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)

    def stop(self) -> None:
        """Deactivate the buzzer."""
        GPIO.output(self.pin, GPIO.LOW)

    def __del__(self):
        """Release GPIO resources on object deletion."""
        releaseSharedGpio()


class PwmBuzzer:
    """Class to control a PWM buzzer connected to a GPIO pin."""

    def __init__(self, pin: int = 18, frequency: float = 1000):
        """Initialize the PWM buzzer on the specified GPIO pin.

        Args:
            pin (int): The GPIO pin number where the buzzer is connected.
        """
        self.pin = pin
        getSharedGpio()
        setupPin(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, frequency)

    def setFrequency(self, frequency: float) -> None:
        """Set the frequency of the PWM buzzer.

        Args:
            frequency (float): Frequency in Hertz.
        """
        self.pwm.ChangeFrequency(frequency)

    def setDutyCycle(self, duty_cycle: float) -> None:
        """Set the duty cycle of the PWM buzzer.

        Args:
            duty_cycle (float): Duty cycle percentage (0.0 to 100.0).
        """
        self.pwm.ChangeDutyCycle(duty_cycle)

    def buzz(self, duty_cycle: float = 50.0) -> None:
        """Start the PWM buzzer with a specified duty cycle.

        Args:
            duty_cycle (float): Duty cycle percentage (0.0 to 100.0).
        """
        self.pwm.start(duty_cycle)

    def stop(self) -> None:
        """Stop the PWM buzzer."""
        self.pwm.stop()

    def __del__(self) -> None:
        """Release GPIO resources on object deletion."""
        releaseSharedGpio()
