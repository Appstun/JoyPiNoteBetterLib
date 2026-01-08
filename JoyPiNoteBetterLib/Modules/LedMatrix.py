import grp
import os
import sys
import time
from typing import List, Tuple

from rpi_ws281x import Color, PixelStrip

# Matrix configuration constants
MATRIX_LED_COUNT: int = 64  # Number of LED pixels
MATRIX_PIN: int = 12  # GPIO pin (must support PWM)
MATRIX_FREQ_HZ: int = 800000  # LED signal frequency
MATRIX_DMA: int = 10  # DMA channel
MATRIX_CHANNEL: int = 0  # Set to 1 if GPIOs 13, 19, 41, 45 or 53
DEFAULT_BRIGHTNESS: int = 100  # 0-255

# Legacy aliases for backwards compatibility
matrixLedCount = MATRIX_LED_COUNT
matrixPin = MATRIX_PIN
matrixFreq_Hz = MATRIX_FREQ_HZ
matrixDma = MATRIX_DMA
matrixChannel = MATRIX_CHANNEL
defaultMatrixBrightness = DEFAULT_BRIGHTNESS

# Type alias for RGB color tuples
ColorTuple = Tuple[int, int, int]

# 5x7 font for letters, numbers, and special characters (each row is a column)
FONT_5X7 = {
    # Uppercase letters
    "A": [0x7E, 0x09, 0x09, 0x09, 0x7E],
    "B": [0x7F, 0x49, 0x49, 0x49, 0x36],
    "C": [0x3E, 0x41, 0x41, 0x41, 0x22],
    "D": [0x7F, 0x41, 0x41, 0x41, 0x3E],
    "E": [0x7F, 0x49, 0x49, 0x49, 0x41],
    "F": [0x7F, 0x09, 0x09, 0x09, 0x01],
    "G": [0x3E, 0x41, 0x49, 0x49, 0x7A],
    "H": [0x7F, 0x08, 0x08, 0x08, 0x7F],
    "I": [0x00, 0x41, 0x7F, 0x41, 0x00],
    "J": [0x20, 0x40, 0x41, 0x3F, 0x01],
    "K": [0x7F, 0x08, 0x14, 0x22, 0x41],
    "L": [0x7F, 0x40, 0x40, 0x40, 0x40],
    "M": [0x7F, 0x02, 0x0C, 0x02, 0x7F],
    "N": [0x7F, 0x04, 0x08, 0x10, 0x7F],
    "O": [0x3E, 0x41, 0x41, 0x41, 0x3E],
    "P": [0x7F, 0x09, 0x09, 0x09, 0x06],
    "Q": [0x3E, 0x41, 0x51, 0x21, 0x5E],
    "R": [0x7F, 0x09, 0x19, 0x29, 0x46],
    "S": [0x46, 0x49, 0x49, 0x49, 0x31],
    "T": [0x01, 0x01, 0x7F, 0x01, 0x01],
    "U": [0x3F, 0x40, 0x40, 0x40, 0x3F],
    "V": [0x1F, 0x20, 0x40, 0x20, 0x1F],
    "W": [0x3F, 0x40, 0x38, 0x40, 0x3F],
    "X": [0x63, 0x14, 0x08, 0x14, 0x63],
    "Y": [0x07, 0x08, 0x70, 0x08, 0x07],
    "Z": [0x61, 0x51, 0x49, 0x45, 0x43],
    # Lowercase letters
    "a": [0x20, 0x54, 0x54, 0x54, 0x78],
    "b": [0x7F, 0x48, 0x44, 0x44, 0x38],
    "c": [0x38, 0x44, 0x44, 0x44, 0x20],
    "d": [0x38, 0x44, 0x44, 0x48, 0x7F],
    "e": [0x38, 0x54, 0x54, 0x54, 0x18],
    "f": [0x08, 0x7E, 0x09, 0x01, 0x02],
    "g": [0x0C, 0x52, 0x52, 0x52, 0x3E],
    "h": [0x7F, 0x08, 0x04, 0x04, 0x78],
    "i": [0x00, 0x44, 0x7D, 0x40, 0x00],
    "j": [0x20, 0x40, 0x44, 0x3D, 0x00],
    "k": [0x7F, 0x10, 0x28, 0x44, 0x00],
    "l": [0x00, 0x41, 0x7F, 0x40, 0x00],
    "m": [0x7C, 0x04, 0x18, 0x04, 0x78],
    "n": [0x7C, 0x08, 0x04, 0x04, 0x78],
    "o": [0x38, 0x44, 0x44, 0x44, 0x38],
    "p": [0x7C, 0x14, 0x14, 0x14, 0x08],
    "q": [0x08, 0x14, 0x14, 0x18, 0x7C],
    "r": [0x7C, 0x08, 0x04, 0x04, 0x08],
    "s": [0x48, 0x54, 0x54, 0x54, 0x20],
    "t": [0x04, 0x3F, 0x44, 0x40, 0x20],
    "u": [0x3C, 0x40, 0x40, 0x20, 0x7C],
    "v": [0x1C, 0x20, 0x40, 0x20, 0x1C],
    "w": [0x3C, 0x40, 0x30, 0x40, 0x3C],
    "x": [0x44, 0x28, 0x10, 0x28, 0x44],
    "y": [0x0C, 0x50, 0x50, 0x50, 0x3C],
    "z": [0x44, 0x64, 0x54, 0x4C, 0x44],
    # Numbers
    "0": [0x3E, 0x51, 0x49, 0x45, 0x3E],
    "1": [0x00, 0x42, 0x7F, 0x40, 0x00],
    "2": [0x42, 0x61, 0x51, 0x49, 0x46],
    "3": [0x21, 0x41, 0x45, 0x4B, 0x31],
    "4": [0x18, 0x14, 0x12, 0x7F, 0x10],
    "5": [0x27, 0x45, 0x45, 0x45, 0x39],
    "6": [0x3C, 0x4A, 0x49, 0x49, 0x30],
    "7": [0x01, 0x71, 0x09, 0x05, 0x03],
    "8": [0x36, 0x49, 0x49, 0x49, 0x36],
    "9": [0x06, 0x49, 0x49, 0x29, 0x1E],
    # Special characters
    " ": [0x00, 0x00, 0x00, 0x00, 0x00],
    ".": [0x00, 0x60, 0x60, 0x00, 0x00],
    ",": [0x00, 0x80, 0x60, 0x00, 0x00],
    "/": [0x20, 0x10, 0x08, 0x04, 0x02],
    "(": [0x00, 0x1C, 0x22, 0x41, 0x00],
    ")": [0x00, 0x41, 0x22, 0x1C, 0x00],
    "&": [0x36, 0x49, 0x55, 0x22, 0x50],
    "+": [0x08, 0x08, 0x3E, 0x08, 0x08],
    "-": [0x08, 0x08, 0x08, 0x08, 0x08],
    "%": [0x23, 0x13, 0x08, 0x64, 0x62],
    ":": [0x00, 0x36, 0x36, 0x00, 0x00],
    "_": [0x40, 0x40, 0x40, 0x40, 0x40],
    "!": [0x00, 0x00, 0x5F, 0x00, 0x00],
    "?": [0x02, 0x01, 0x51, 0x09, 0x06],
    "°": [0x00, 0x06, 0x09, 0x09, 0x06],
    "'": [0x00, 0x00, 0x07, 0x00, 0x00],
    "<": [0x08, 0x14, 0x22, 0x41, 0x00],
    ">": [0x00, 0x41, 0x22, 0x14, 0x08],
    "^": [0x04, 0x02, 0x01, 0x02, 0x04],
    "~": [0x04, 0x02, 0x04, 0x08, 0x04],
    # German umlauts
    "Ä": [0x7C, 0x0A, 0x09, 0x0A, 0x7C],
    "Ö": [0x3C, 0x42, 0x41, 0x42, 0x3C],
    "Ü": [0x3C, 0x42, 0x40, 0x42, 0x3C],
    "ä": [0x20, 0x55, 0x54, 0x55, 0x78],
    "ö": [0x38, 0x45, 0x44, 0x45, 0x38],
    "ü": [0x3C, 0x41, 0x40, 0x21, 0x7C],
}


class LedMatrix:
    """8x8 NeoPixel LED matrix controller with optimized rendering.

    Provides methods for displaying pixels, characters, and scrolling text
    on an 8x8 WS281x LED matrix.

    Attributes:
        matrix: The underlying PixelStrip instance.
    """

    __slots__ = ("matrix", "_numPixels", "_colorCache", "_black")

    # GPIO pins that require root (PWM/PCM mode)
    _PWM_PINS = {12, 13, 18, 19, 21, 40, 41, 45, 52, 53}
    # GPIO pins that work without root (SPI mode)
    _SPI_PINS = {10, 38}

    @staticmethod
    def _checkPermissions() -> None:
        """Check if the user has sufficient permissions to control the LED matrix.

        The WS281x library requires:
        - PWM mode (GPIO 12, 18, etc.): Root privileges (sudo) required
        - SPI mode (GPIO 10): User must be in 'gpio' and/or 'spi' group

        Raises:
            PermissionError: If the user lacks the required permissions.
        """
        is_root = os.geteuid() == 0
        using_spi_pin = MATRIX_PIN in LedMatrix._SPI_PINS

        # PWM/PCM pins always require root
        if not using_spi_pin:
            if not is_root:
                raise PermissionError(
                    f"Error: GPIO {MATRIX_PIN} (PWM/PCM mode) requires root privileges.\n"
                    "Please run the script with sudo: 'sudo python3 your_script.py'"
                )
            return  # Root with PWM pin is fine

        # SPI pin: root always works
        if is_root:
            return

        # SPI pin without root: check group membership
        user_groups = os.getgroups()
        has_gpio = False
        has_spi = False

        try:
            gpio_group = grp.getgrnam("gpio")
            has_gpio = gpio_group.gr_gid in user_groups
        except KeyError:
            pass

        try:
            spi_group = grp.getgrnam("spi")
            has_spi = spi_group.gr_gid in user_groups
        except KeyError:
            pass

        if not (has_gpio or has_spi):
            print(
                f"Error: GPIO {MATRIX_PIN} (SPI mode) requires membership in 'gpio' or 'spi' group.\n"
                "Please run one of the following:\n"
                "  1. Run with sudo: 'sudo python3 your_script.py'\n"
                "  2. Add user to groups: 'sudo usermod -a -G gpio,spi $USER'\n"
                "     (requires logout/login to take effect)",
                file=sys.stderr,
            )
            sys.exit(1)

    def __init__(self, brightness: int = DEFAULT_BRIGHTNESS):
        """Initialize the LED matrix.

        Args:
            brightness: Initial brightness level (0-255, default 100).
        """
        # Check permissions before initializing
        self._checkPermissions()

        # Create NeoPixel object
        self.matrix = PixelStrip(
            MATRIX_LED_COUNT,
            MATRIX_PIN,
            MATRIX_FREQ_HZ,
            MATRIX_DMA,
            False,  # Signal inversion
            brightness,
            MATRIX_CHANNEL,
        )

        # Initialize library
        self.matrix.begin()

        # Cache frequently used values
        self._numPixels = self.matrix.numPixels()
        self._colorCache: dict = {}  # Cache Color objects
        self._black = Color(0, 0, 0)

    def _getColor(self, color: ColorTuple) -> int:
        """Get or create a cached Color object for the given RGB tuple.

        Args:
            color: RGB color tuple (R, G, B).

        Returns:
            Cached Color integer value.
        """
        if color not in self._colorCache:
            self._colorCache[color] = Color(*color)
        return self._colorCache[color]

    @staticmethod
    def _validateColor(color: ColorTuple) -> ColorTuple:
        """Validate that the color is a valid RGB tuple.

        Args:
            color: RGB color tuple to validate.

        Returns:
            The validated color tuple.

        Raises:
            ValueError: If color is not a 3-element tuple.
        """
        if len(color) != 3:
            raise ValueError("Color must be (R, G, B) tuple")
        return color

    def clear(self) -> None:
        """Turn off all LEDs on the matrix."""
        for i in range(self._numPixels):
            self.matrix.setPixelColor(i, self._black)
        self.matrix.show()

    def setPixel(self, position: int, color: ColorTuple) -> None:
        """Set a single pixel to the specified color.

        Args:
            position: LED index (0-63).
            color: RGB color tuple (R, G, B).

        Raises:
            ValueError: If position is out of range.
        """
        if not 0 <= position < MATRIX_LED_COUNT:
            raise ValueError("Position out of range")
        r, g, b = self._validateColor(color)
        self.matrix.setPixelColorRGB(position, r, g, b)

    def setBrightness(self, brightness: int) -> None:
        """Set the brightness of the LED matrix.

        Args:
            brightness: Brightness level (0-255).

        Raises:
            ValueError: If brightness is out of range.
        """
        if not 0 <= brightness <= 255:
            raise ValueError("Brightness out of range")
        self.matrix.setBrightness(brightness)

    def setAll(self, color: ColorTuple) -> None:
        """Set all pixels to the same color.

        Args:
            color: RGB color tuple (R, G, B).
        """
        c = self._getColor(self._validateColor(color))
        for i in range(self._numPixels):
            self.matrix.setPixelColor(i, c)

    def update(self) -> None:
        """Push the current pixel buffer to the LED matrix."""
        self.matrix.show()

    @staticmethod
    def _xyToIndex(x: int, y: int) -> int:
        """Convert x,y coordinates to LED index.

        Args:
            x: X coordinate (0-7).
            y: Y coordinate (0-7).

        Returns:
            LED index in the strip (0-63).
        """
        return (y << 3) + x  # y * 8 + x using bit shift

    @staticmethod
    def _getCharBitmap(char: str) -> List[int]:
        """Get the 5x7 bitmap for a character.

        Args:
            char: Single character to look up.

        Returns:
            List of column bytes for the character bitmap.
        """
        return FONT_5X7.get(char, FONT_5X7[" "])

    def _textToBitmap(self, text: str) -> List[int]:
        """Convert a text string to a contiguous bitmap.

        Args:
            text: Text string to convert.

        Returns:
            List of column bytes representing the text.
        """
        bitmap: List[int] = []
        for char in text:
            bitmap.extend(self._getCharBitmap(char))
            bitmap.append(0x00)  # Space between characters
        return bitmap

    def scrollText(
        self,
        text: str,
        color: ColorTuple,
        delay: float = 0.1,
        loops: int = 1,
        background: ColorTuple = (0, 0, 0),
    ) -> None:
        """Scroll text from right to left across the 8x8 LED matrix.

        Args:
            text: Text to display.
            color: Text color as (R, G, B) tuple.
            delay: Delay between frames in seconds (default 0.1).
            loops: Number of repetitions, 0 for infinite (default 1).
            background: Background color as (R, G, B) tuple (default (0, 0, 0)).
        """
        r, g, b = self._validateColor(color)
        bgR, bgG, bgB = self._validateColor(background)

        # Convert text to bitmap with padding
        bitmap = [0x00] * 8 + self._textToBitmap(text) + [0x00] * 8
        totalWidth = len(bitmap)
        loopCount = 0

        # Pre-compute xy to index mapping for the 8x7 display area
        xyToIdx = [(x, y, (y << 3) + x) for x in range(8) for y in range(7)]

        while loops == 0 or loopCount < loops:
            for offset in range(totalWidth - 7):
                # Clear matrix buffer
                for i in range(MATRIX_LED_COUNT):
                    self.matrix.setPixelColorRGB(i, bgR, bgG, bgB)

                # Draw current frame
                for x, y, idx in xyToIdx:
                    bitmapIdx = offset + x
                    if bitmapIdx < totalWidth:
                        if bitmap[bitmapIdx] & (1 << y):
                            self.matrix.setPixelColorRGB(idx, r, g, b)

                self.matrix.show()
                time.sleep(delay)

            loopCount += 1

    def showChar(
        self,
        char: str,
        color: ColorTuple,
        offsetX: int = 1,
        background: ColorTuple = (0, 0, 0),
    ) -> None:
        """Display a single character on the matrix.

        Args:
            char: Character to display.
            color: Text color as (R, G, B) tuple.
            offsetX: Horizontal offset for centering (default 1).
            background: Background color as (R, G, B) tuple (default (0, 0, 0)).
        """
        r, g, b = self._validateColor(color)
        bgR, bgG, bgB = self._validateColor(background)

        # Set background
        for i in range(MATRIX_LED_COUNT):
            self.matrix.setPixelColorRGB(i, bgR, bgG, bgB)

        # Draw character
        charBitmap = self._getCharBitmap(char)
        for colIdx, column in enumerate(charBitmap):
            x = offsetX + colIdx
            if 0 <= x < 8:
                for y in range(7):
                    if column & (1 << y):
                        self.matrix.setPixelColorRGB((y << 3) + x, r, g, b)

        self.matrix.show()

    def showText(
        self,
        text: str,
        color: ColorTuple,
        background: ColorTuple = (0, 0, 0),
    ) -> None:
        """Display text on the matrix (only first visible character for 8x8).

        For longer text, use scrollText().

        Args:
            text: Text to display.
            color: Text color as (R, G, B) tuple.
            background: Background color as (R, G, B) tuple (default (0, 0, 0)).
        """
        if text:
            self.showChar(text[0], color, background=background)
