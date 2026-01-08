import time

import RPi.GPIO as GPIO

from ..Shared.SharedGpio import getSharedGpio, releaseSharedGpio, setupPin


class Servomotor:
    """Servo motor controller using PWM on GPIO.

    Controls a standard servo motor using pulse-width modulation.
    Supports smooth transitions between angles with configurable speed.

    Attributes:
        pin: GPIO pin number for PWM signal.
        direction: Current angle position of the servo (0-180 degrees).
    """

    def __init__(self, startDirection: int, pin: int = 19) -> None:
        """Initialize the servo motor.

        Args:
            startDirection: Initial angle position (0-180 degrees).
            pin: GPIO pin number for PWM signal (default 19).
        """
        self.pin = pin
        self.direction = startDirection

        getSharedGpio()
        setupPin(self.pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.pin, 50)
        self._pwm.start(self._dutycycle(self.direction))

    def _dutycycle(self, angle: int) -> float:
        """Convert angle to PWM duty cycle percentage.

        Args:
            angle: Servo angle in degrees.

        Returns:
            Duty cycle percentage (0-100) for the given angle.
        """
        duty_percent = 0.05 * angle + 7.0
        if duty_percent < 0:
            duty_percent = 0
        if duty_percent > 100:
            duty_percent = 100
        return duty_percent

    def setDirection(self, direction: int, speed: int) -> None:
        """Move the servo to a new angle position.

        Smoothly transitions from the current position to the target
        angle using the specified step size for each increment.

        Args:
            direction: Target angle in degrees (0-180).
            speed: Step size for smooth transition. Use 0 for single-step
                   movement, higher values for faster transitions.
        """
        step = speed
        if step == 0:
            step = 1 if (direction > self.direction) else -1

        if direction > self.direction:
            rng = range(self.direction, direction, step)
        else:
            rng = range(self.direction, direction, -step)

        for d in rng:
            self._pwm.ChangeDutyCycle(self._dutycycle(d))
            self.direction = d
            time.sleep(0.1)

        self._pwm.ChangeDutyCycle(self._dutycycle(direction))
        self.direction = direction

    def getDirection(self) -> int:
        """Get the current servo angle position.

        Returns:
            Current angle in degrees.
        """
        return self.direction

    def __del__(self) -> None:
        """Stop PWM and release GPIO resources on object deletion."""
        self._pwm.stop()
        releaseSharedGpio()
