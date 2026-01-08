import RPi.GPIO as GPIO

from ..Shared.SharedGpio import getSharedGpio, releaseSharedGpio, setupPin

class Relay:
    def __init__(self, pin: int = 21) -> None:
        self.pin = pin
        getSharedGpio()
        setupPin(self.pin, GPIO.OUT)

    def turnOn(self) -> None:
        GPIO.output(self.pin, GPIO.HIGH)

    def turnOff(self) -> None:
        GPIO.output(self.pin, GPIO.LOW)

    def __del__(self) -> None:
        releaseSharedGpio()
