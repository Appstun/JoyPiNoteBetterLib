from enum import IntEnum
from typing import Tuple

# Import shared SPI bus singleton
from ..Shared.SharedSpi import getSharedSpi, releaseSharedSpi


class Direction(IntEnum):
    """Enumeration for joystick directions.

    Uses IntEnum for faster integer comparisons than regular Enum.

    Attributes:
        CENTER: Joystick at rest position.
        N, E, S, W: Cardinal directions.
        NE, SE, SW, NW: Diagonal directions (8-direction mode only).
    """

    CENTER = 0
    N = 1
    E = 2
    S = 3
    W = 4
    NE = 5
    SE = 6
    SW = 7
    NW = 8


# Center value for 10-bit ADC (0-1023 range)
_ADC_CENTER = 512


class Joystick:
    """Analog joystick reader using MCP3008 ADC over SPI.

    Reads X and Y axis values from an analog joystick connected to the MCP3008.
    Supports both raw ADC values and direction detection with configurable
    dead zone threshold.

    Attributes:
        xChannel: ADC channel for X axis.
        yChannel: ADC channel for Y axis.
        spi: Shared SPI bus instance.
    """

    __slots__ = ("xChannel", "yChannel", "spi", "_xCmd", "_yCmd")

    def __init__(self, xChannel: int = 1, yChannel: int = 0):
        """Initialize the joystick reader.

        Args:
            xChannel: MCP3008 ADC channel for X axis (0-7, default 1).
            yChannel: MCP3008 ADC channel for Y axis (0-7, default 0).
        """
        self.xChannel = xChannel
        self.yChannel = yChannel

        # Get shared SPI bus instance
        self.spi = getSharedSpi()

        # Pre-compute SPI command buffers
        self._xCmd = [1, (8 + xChannel) << 4, 0]
        self._yCmd = [1, (8 + yChannel) << 4, 0]

    def _readAdc(self, cmd: list) -> int:
        """Read ADC value using a pre-computed command buffer.

        Args:
            cmd: Pre-computed SPI command bytes.

        Returns:
            10-bit ADC value (0-1023).
        """
        # Use list() copy because xfer2 may modify the buffer in-place
        adc = self.spi.xfer2(list(cmd))
        return ((adc[1] & 3) << 8) + adc[2]

    def getX(self) -> int:
        """Get the current X axis ADC value.

        Returns:
            10-bit ADC value (0-1023), ~512 at center.
        """
        return self._readAdc(self._xCmd)

    def getY(self) -> int:
        """Get the current Y axis ADC value.

        Returns:
            10-bit ADC value (0-1023), ~512 at center.
        """
        return self._readAdc(self._yCmd)

    def getXY(self) -> Tuple[int, int]:
        """Get both X and Y axis values in a single call.

        More efficient than calling getX() and getY() separately.

        Returns:
            Tuple of (X, Y) ADC values, each 0-1023.
        """
        return self._readAdc(self._xCmd), self._readAdc(self._yCmd)

    def getDirection(
        self, do8Directions: bool = False, threshold: int = 100
    ) -> Direction:
        """Get the current joystick direction.

        Determines direction based on X and Y axis deviation from center.

        Args:
            do8Directions: If True, includes diagonal directions (NE, SE, SW, NW).
                          If False, only returns cardinal directions (N, E, S, W).
            threshold: Dead zone radius around center position. Values within
                      this range from center (512) are considered centered.

        Returns:
            Direction enum value indicating current joystick position.
        """
        # Get both values at once for efficiency
        x, y = self.getXY()

        # Pre-compute threshold boundaries
        low = _ADC_CENTER - threshold
        high = _ADC_CENTER + threshold

        # Check center first (most common case)
        xCentered = low <= x <= high
        yCentered = low <= y <= high

        if xCentered and yCentered:
            return Direction.CENTER

        yLow = y < low
        yHigh = y > high
        xLow = x < low
        xHigh = x > high

        if do8Directions:
            if yLow:
                if xLow:
                    return Direction.SE
                if xHigh:
                    return Direction.SW
                return Direction.S
            if yHigh:
                if xLow:
                    return Direction.NE
                if xHigh:
                    return Direction.NW
                return Direction.N
            if xLow:
                return Direction.E
            if xHigh:
                return Direction.W
        else:
            if yLow:
                return Direction.S
            if yHigh:
                return Direction.N
            if xLow:
                return Direction.E
            if xHigh:
                return Direction.W

        return Direction.CENTER

    def __del__(self):
        """Release shared SPI bus reference on object deletion."""
        releaseSharedSpi()
