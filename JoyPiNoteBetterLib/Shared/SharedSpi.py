import spidev
from typing import Optional

_sharedSpi: Optional[spidev.SpiDev] = None
_spiRefCount: int = 0


def getSharedSpi(
    bus: int = 0, device: int = 1, speedHz: int = 1000000
) -> spidev.SpiDev:
    """Get or create the shared SPI bus connection.

    Creates a new SPI connection on first call, then returns the same instance
    for subsequent calls. Uses reference counting to track active users.

    Args:
        bus: SPI bus number (default 0).
        device: SPI device/chip select (default 1).
        speedHz: SPI clock speed in Hz (default 1 MHz).

    Returns:
        The shared SpiDev instance.
    """
    global _sharedSpi, _spiRefCount
    if _sharedSpi is None:
        spi = spidev.SpiDev()
        spi.open(bus, device)
        spi.max_speed_hz = speedHz
        _sharedSpi = spi
    _spiRefCount += 1
    return _sharedSpi


def releaseSharedSpi() -> None:
    """Release a reference to the shared SPI connection.

    Decrements the reference count. When the count reaches zero, the SPI
    connection is closed and cleaned up. Safe to call multiple times.
    """
    global _sharedSpi, _spiRefCount
    _spiRefCount -= 1
    if _spiRefCount <= 0 and _sharedSpi is not None:
        _sharedSpi.close()
        _sharedSpi = None
        _spiRefCount = 0
