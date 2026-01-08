from typing import Optional, Tuple

from ..Shared.SharedSpi import getSharedSpi, releaseSharedSpi


# Pre-computed ADC thresholds for button detection (tuple for faster iteration)
_ADC_KEY_THRESHOLDS: Tuple[int, ...] = (
    30,
    90,
    160,
    230,
    280,
    330,
    400,
    470,
    530,
    590,
    650,
    720,
    780,
    840,
    890,
    960,
)

# Pre-computed button index mapping (ADC value order to matrix position)
_BUTTON_MAP: Tuple[int, ...] = (12, 13, 14, 15, 8, 9, 10, 11, 4, 5, 6, 7, 0, 1, 2, 3)


class ButtonMatrix:
    """4x4 button matrix reader using MCP3008 ADC over SPI.

    Reads analog values from the MCP3008 and converts them to button indices
    (0-15) based on voltage thresholds. Uses shared SPI bus for efficient
    resource management.

    Attributes:
        keyChannel: ADC channel connected to the button matrix.
        spi: Shared SPI bus instance.
    """

    __slots__ = ("keyChannel", "spi", "_cmdBuffer")

    def __init__(self, keyChannel: int = 4):
        """Initialize the button matrix reader.

        Args:
            keyChannel: MCP3008 ADC channel (0-7, default 4).
        """
        self.keyChannel = keyChannel
        self.spi = getSharedSpi()
        # Pre-compute SPI command buffer for this channel
        self._cmdBuffer = [1, (8 + keyChannel) << 4, 0]

    def readChannel(self, channel: int) -> int:
        """Read raw ADC value from a specific MCP3008 channel.

        Args:
            channel: ADC channel number (0-7).

        Returns:
            10-bit ADC value (0-1023).
        """
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        return ((adc[1] & 3) << 8) + adc[2]

    def getAdcValue(self) -> int:
        """Read ADC value from the configured key channel.

        Uses a pre-computed command buffer for faster SPI communication.

        Returns:
            10-bit ADC value (0-1023).
        """
        # Use list() copy because xfer2 may modify the buffer in-place
        adc = self.spi.xfer2(list(self._cmdBuffer))
        return ((adc[1] & 3) << 8) + adc[2]

    def _checkMatrix(self) -> int:
        """Read ADC and determine which button is pressed.

        Compares the ADC value against pre-computed thresholds to identify
        the pressed button. Button indices are mapped from 0 (top-left)
        to 15 (bottom-right).

        Returns:
            Button index (0-15) or -1 if no button is pressed.
        """
        adcValue = self.getAdcValue()

        # Use pre-computed tuples for faster iteration
        for num, threshold in enumerate(_ADC_KEY_THRESHOLDS):
            if adcValue < threshold:
                return _BUTTON_MAP[num]
        return -1

    def getPressedKey(self) -> Optional[int]:
        """Get the currently pressed button.

        Returns:
            Button index (0-15) or None if no button is pressed.
        """
        button = self._checkMatrix()
        return None if button == -1 else button

    def __del__(self):
        """Release shared SPI bus reference on object deletion."""
        releaseSharedSpi()
