import board
from typing import Optional, Any

_sharedI2C: Optional[Any] = None
_i2cRefCount: int = 0


def getSharedI2C() -> Any:
    """Get or create the shared I2C bus connection.

    Creates a new I2C connection on first call, then returns the same instance
    for subsequent calls. Uses reference counting to track active users.

    Returns:
        The shared I2C instance.
    """
    global _sharedI2C, _i2cRefCount
    if _sharedI2C is None:
        _sharedI2C = board.I2C()
    _i2cRefCount += 1
    return _sharedI2C


def releaseSharedI2C() -> None:
    """Release a reference to the shared I2C connection.

    Decrements the reference count. When the count reaches zero, the I2C
    connection is closed and cleaned up. Safe to call multiple times.
    """
    global _sharedI2C, _i2cRefCount
    _i2cRefCount -= 1
    if _i2cRefCount <= 0 and _sharedI2C is not None:
        _sharedI2C.deinit()
        _sharedI2C = None
        _i2cRefCount = 0
