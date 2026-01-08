import math
import time

import RPi.GPIO as GPIO

from ..Shared.SharedGpio import getSharedGpio, releaseSharedGpio, setupPin


class Stepmotor:
    """Stepper motor controller using GPIO pins.

    Controls a 4-phase stepper motor using 8-step half-stepping sequence
    for smooth rotation. Supports speed control and rotation by steps,
    degrees, or distance.

    Attributes:
        pinA: GPIO pin for coil A.
        pinB: GPIO pin for coil B.
        pinC: GPIO pin for coil C.
        pinD: GPIO pin for coil D.
    """

    def __init__(self, pinA: int = 5, pinB: int = 6, pinC: int = 13, pinD: int = 25):
        """Initialize the stepper motor on the specified GPIO pins.

        Args:
            pinA: GPIO pin for coil A (default 5).
            pinB: GPIO pin for coil B (default 6).
            pinC: GPIO pin for coil C (default 13).
            pinD: GPIO pin for coil D (default 25).
        """
        self.pinA = pinA
        self.pinB = pinB
        self.pinC = pinC
        self.pinD = pinD
        self._interval = 0.0011

        getSharedGpio()

        # Configure pins as output
        setupPin(self.pinA, GPIO.OUT)
        setupPin(self.pinB, GPIO.OUT)
        setupPin(self.pinC, GPIO.OUT)
        setupPin(self.pinD, GPIO.OUT)

        GPIO.output(self.pinA, False)
        GPIO.output(self.pinB, False)
        GPIO.output(self.pinC, False)
        GPIO.output(self.pinD, False)

    def setSpeed(self, speed: int) -> None:
        """Set the rotation speed of the stepper motor.

        Args:
            speed: Speed percentage from 1 (slowest) to 100 (fastest).
                   Higher values result in faster rotation.
        """
        if speed < 1:
            speed = 1
        elif speed > 100:
            speed = 100
        # Map speed 1-100 to interval 0.01-0.0011 seconds
        self._interval = 0.01 - (speed - 1) * (0.01 - 0.0011) / 99

    def _step1(self):
        GPIO.output(self.pinD, True)
        time.sleep(self._interval)
        GPIO.output(self.pinD, False)

    def _step2(self):
        GPIO.output(self.pinD, True)
        GPIO.output(self.pinC, True)
        time.sleep(self._interval)
        GPIO.output(self.pinD, False)
        GPIO.output(self.pinC, False)

    def _step3(self):
        GPIO.output(self.pinC, True)
        time.sleep(self._interval)
        GPIO.output(self.pinC, False)

    def _step4(self):
        GPIO.output(self.pinB, True)
        GPIO.output(self.pinC, True)
        time.sleep(self._interval)
        GPIO.output(self.pinB, False)
        GPIO.output(self.pinC, False)

    def _step5(self):
        GPIO.output(self.pinB, True)
        time.sleep(self._interval)
        GPIO.output(self.pinB, False)

    def _step6(self):
        GPIO.output(self.pinA, True)
        GPIO.output(self.pinB, True)
        time.sleep(self._interval)
        GPIO.output(self.pinA, False)
        GPIO.output(self.pinB, False)

    def _step7(self):
        GPIO.output(self.pinA, True)
        time.sleep(self._interval)
        GPIO.output(self.pinA, False)

    def _step8(self):
        GPIO.output(self.pinD, True)
        GPIO.output(self.pinA, True)
        time.sleep(self._interval)
        GPIO.output(self.pinD, False)
        GPIO.output(self.pinA, False)

    def _turn(self, count: int) -> None:
        """Execute a specified number of 8-step rotation cycles (forward).

        Args:
            count: Number of complete 8-step cycles to execute.
        """
        for i in range(count):
            self._step1()
            self._step2()
            self._step3()
            self._step4()
            self._step5()
            self._step6()
            self._step7()
            self._step8()

    def _turnReverse(self, count: int) -> None:
        """Execute a specified number of 8-step rotation cycles (reverse).

        Args:
            count: Number of complete 8-step cycles to execute.
        """
        for i in range(count):
            self._step8()
            self._step7()
            self._step6()
            self._step5()
            self._step4()
            self._step3()
            self._step2()
            self._step1()

    def turnSteps(self, steps: int) -> None:
        """Rotate the motor by a specified number of steps.

        Args:
            steps: Number of steps to rotate. Positive values rotate forward,
                   negative values rotate in reverse.
        """
        if steps < 0:
            self._turnReverse(abs(steps))
        else:
            self._turn(steps)

    def turnDegrees(self, deg: int) -> None:
        """Rotate the motor by a specified angle in degrees.

        Args:
            deg: Angle in degrees to rotate. Positive values rotate forward,
                 negative values rotate in reverse.
        """
        if deg < 0:
            self._turnReverse(int(abs(deg) * 512 // 360))
        else:
            self._turn(deg * 512 // 360)

    def turnDistance(self, distance: int, radius: int) -> None:
        """Rotate the motor to cover a specified linear distance.

        Calculates the required rotation based on the wheel/pulley radius
        attached to the motor shaft.

        Args:
            distance: Linear distance to travel in the same unit as radius.
                      Positive values move forward, negative values reverse.
            radius: Radius of the wheel or pulley attached to the motor shaft.
        """
        if distance < 0:
            self._turnReverse(int(abs(distance) * 512 / (2 * math.pi * radius)))
        else:
            self._turn(int(distance * 512 / (2 * math.pi * radius)))

    def release(self) -> None:
        """Release all coils to allow free rotation and reduce heat.

        Sets all motor coils to LOW, removing holding torque.
        The motor shaft can now rotate freely and will not heat up.
        Call this when the motor doesn't need to hold its position.
        """
        GPIO.output(self.pinA, False)
        GPIO.output(self.pinB, False)
        GPIO.output(self.pinC, False)
        GPIO.output(self.pinD, False)

    def __del__(self) -> None:
        """Release GPIO resources on object deletion."""
        try:
            self.release()
        except RuntimeError:
            pass  # GPIO already cleaned up
        releaseSharedGpio()
