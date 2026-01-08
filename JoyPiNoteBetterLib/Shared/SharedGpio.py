import atexit

import RPi.GPIO as GPIO

_gpioInitialized: bool = False
_gpioRefCount: int = 0


def getSharedGpio() -> None:
    """Initialize the shared GPIO bus connection.

    Sets up GPIO in BCM mode on first call, then increments reference count
    for subsequent calls. Uses reference counting to track active users.
    """
    global _gpioInitialized, _gpioRefCount
    _gpioRefCount += 1
    if not _gpioInitialized:
        GPIO.setmode(GPIO.BCM)
        _gpioInitialized = True
        # Register cleanup on program exit
        atexit.register(releaseSharedGpio)


def releaseSharedGpio() -> None:
    """Release a reference to the shared GPIO connection.

    Decrements the reference count. When the count reaches zero, GPIO
    is cleaned up. Safe to call multiple times.
    """
    global _gpioInitialized, _gpioRefCount
    _gpioRefCount -= 1
    if _gpioRefCount <= 0 and _gpioInitialized:
        GPIO.cleanup()
        _gpioInitialized = False
        _gpioRefCount = 0


def setupPin(pin: int, mode, pull_up_down=GPIO.PUD_OFF) -> None:
    """Set up a GPIO pin with error handling.

    Safely sets up a GPIO pin, handling cases where the pin is already
    configured.

    Args:
        pin: GPIO pin number in BCM mode.
        mode: GPIO mode (GPIO.IN or GPIO.OUT).
        pull_up_down: Pull-up/down mode (default GPIO.PUD_OFF).
    """
    try:
        GPIO.setup(pin, mode, pull_up_down=pull_up_down)
    except RuntimeError:
        pass  # Pin already configured


def isGpioInitialized() -> bool:
    """Check if GPIO has been initialized.

    Returns:
        True if GPIO is initialized, False otherwise.
    """
    return _gpioInitialized
