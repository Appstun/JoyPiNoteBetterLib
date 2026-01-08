from ..Modules.Buzzer import Buzzer, PwmBuzzer
from ..Modules.LcdDisplay import LcdDisplay
from ..Modules.LedMatrix import LedMatrix
from ..Modules.Relay import Relay
from ..Modules.Seg7x4 import Seg7x4
from ..Modules.Servomotor import Servomotor
from ..Modules.Stepmotor import Stepmotor
from ..Modules.Vibrator import Vibrator


class ModuleReset:
    """Utility class to reset and mute JoyPi hardware modules.

    Provides static methods to clear displays and mute sound-producing
    components. All methods handle errors silently to allow partial
    resets when some components are unavailable.
    """

    @staticmethod
    def clearAll() -> None:
        """Clear all connected components to their default state.

        Attempts to initialize and clear the LED matrix, LCD display, and
        7-segment display. Silently ignores failures for components that
        are not available.
        """
        ModuleReset.clearLedMatrix()
        ModuleReset.clearLcdDisplay()
        ModuleReset.clearSeg7x4()

    @staticmethod
    def clearLedMatrix() -> None:
        """Clear the LED matrix to its default state.

        Attempts to initialize and clear the LED matrix. Silently ignores
        errors if the matrix is not available.
        """
        try:
            led = LedMatrix()
            led.clear()
        except Exception:
            pass

    @staticmethod
    def clearLcdDisplay() -> None:
        """Clear the LCD display to its default state.

        Attempts to initialize and clear the LCD display. Silently ignores
        errors if the display is not available.
        """
        try:
            lcd = LcdDisplay()
            lcd.setBacklight(False)
            lcd.clear()
        except Exception:
            pass

    @staticmethod
    def clearSeg7x4() -> None:
        """Clear the 7-segment display to its default state.

        Attempts to initialize and clear the 7-segment display. Silently ignores
        errors if the display is not available.
        """
        try:
            seg = Seg7x4()
            seg.clear()
        except Exception:
            pass

    @staticmethod
    def muteAll() -> None:
        """Mute all sound-producing components.

        Attempts to deactivate the buzzer and vibrator. Silently ignores
        errors for components that are not available.
        """
        ModuleReset.muteBuzzer()
        ModuleReset.muteVibrator()

    @staticmethod
    def muteBuzzer() -> None:
        """Mute the buzzer component.

        Attempts to deactivate the buzzer. Silently ignores errors if
        the buzzer is not available.
        """
        try:
            buzzer = Buzzer()
            buzzer.stop()

            buzz = PwmBuzzer()
            buzz.stop()
        except Exception:
            pass

    @staticmethod
    def muteVibrator() -> None:
        """Mute the vibrator component.

        Attempts to deactivate the vibrator. Silently ignores errors if
        the vibrator is not available.
        """
        try:
            vibrator = Vibrator()
            vibrator.setVibrate(False)
        except Exception:
            pass

    @staticmethod
    def resetMotors() -> None:
        """
        Reset motor components to their default state.
        """
        sm = Stepmotor()
        sm.__del__()

        s = Servomotor(0)
        s.__del__()

    @staticmethod
    def releaseRelay() -> None:
        """
        Release the relay component.
        """
        r = Relay()
        r.__del__()
