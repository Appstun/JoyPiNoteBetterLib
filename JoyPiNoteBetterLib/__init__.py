"""JoyPiNote Better Library - Hardware Interface Library.

A Python library for JoyPi Note hardware components designed for Raspberry Pi.

Supported Components:
    - LedMatrix: 8x8 NeoPixel LED matrix with text rendering
    - LcdDisplay: I2C character LCD display
    - Seg7x4: 4-digit 7-segment I2C display
    - ButtonMatrix: 4x4 button matrix via MCP3008 ADC
    - Joystick: Analog joystick via MCP3008 ADC
    - Touch: GPIO touch sensor
    - Tilt: GPIO tilt sensor
"""

from .Modules.ButtonMatrix import ButtonMatrix
from .Modules.Buzzer import Buzzer, PwmBuzzer
from .Modules.HumTemp import HumidityTemperatureSensor
from .Modules.Joystick import Direction, Joystick
from .Modules.LcdDisplay import LcdDisplay, ScrollingLinesLcd
from .Modules.LedMatrix import LedMatrix
from .Modules.LightSensor import LightSensor
from .Modules.Nfc import NfcReader
from .Modules.Relay import Relay
from .Modules.Seg7x4 import Seg7x4
from .Modules.Servomotor import Servomotor
from .Modules.SoundSensor import SoundSensor
from .Modules.Stepmotor import Stepmotor
from .Modules.TiltSensor import TiltSensor
from .Modules.TouchSensor import TouchSensor
from .Modules.Ultrasonic import UltrasonicSensor
from .Modules.Vibrator import PwmVibrator, Vibrator
from .Other.Clear import ModuleReset

__all__ = [
    "LedMatrix",
    "LcdDisplay",
    "Seg7x4",
    "ButtonMatrix",
    "Joystick",
    "Direction",
    "TouchSensor",
    "HumidityTemperatureSensor",
    "Buzzer",
    "PwmBuzzer",
    "Vibrator",
    "PwmVibrator",
    "SoundSensor",
    "TiltSensor",
    "UltrasonicSensor",
    "LightSensor",
    "NfcReader",
    "Servomotor",
    "Stepmotor",
    "ModuleReset",
    "Relay",
    "ScrollingLinesLcd",
]

__version__ = "1.1.0"
__package_name__ = "JoyPiNoteBetterLib"
