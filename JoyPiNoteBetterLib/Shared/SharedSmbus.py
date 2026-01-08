import smbus2
from typing import Optional

_sharedSmbus: Optional[smbus2.SMBus] = None
_smbusRefCount: int = 0


def getSharedSmbus(bus: int = 1) -> smbus2.SMBus:
    """Get or create the shared SMBus connection.

    Creates a new SMBus connection on first call, then returns the same instance
    for subsequent calls. Uses reference counting to track active users.

    Args:
        bus: SMBus number (default 1 for Raspberry Pi).

    Returns:
        The shared SMBus instance.
    """
    global _sharedSmbus, _smbusRefCount
    if _sharedSmbus is None:
        _sharedSmbus = smbus2.SMBus(bus)
    _smbusRefCount += 1
    return _sharedSmbus


def releaseSharedSmbus() -> None:
    """Release a reference to the shared SMBus connection.

    Decrements the reference count. When the count reaches zero, the SMBus
    connection is closed and cleaned up. Safe to call multiple times.
    """
    global _sharedSmbus, _smbusRefCount
    _smbusRefCount -= 1
    if _smbusRefCount <= 0 and _sharedSmbus is not None:
        _sharedSmbus.close()
        _sharedSmbus = None
        _smbusRefCount = 0
