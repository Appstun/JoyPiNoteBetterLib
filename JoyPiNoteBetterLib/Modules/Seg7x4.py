from typing import Union

from adafruit_ht16k33.segments import Seg7x4 as AdafruitSeg7x4

# Import shared I2C bus
from ..Shared.SharedI2C import getSharedI2C, releaseSharedI2C

# 7-segment character bitmaps (tuple for faster indexed access)
# Each byte represents which segments are lit: 0bGFEDCBA
NUMBERS: tuple = (
    0x3F,  # 0
    0x06,  # 1
    0x5B,  # 2
    0x4F,  # 3
    0x66,  # 4
    0x6D,  # 5
    0x7D,  # 6
    0x07,  # 7
    0x7F,  # 8
    0x6F,  # 9
    0x77,  # a
    0x7C,  # b
    0x39,  # C
    0x5E,  # d
    0x79,  # E
    0x71,  # F
    0x40,  # -
)

# Character lookup sets for O(1) membership testing
_HEX_CHARS: frozenset = frozenset("abcdef")
_DIGIT_CHARS: frozenset = frozenset("0123456789")

# Default I2C address and display configuration
SEG_ADDRESS: int = 0x70
CHAR_COUNT: int = 4

# Legacy aliases (deprecated)
segAdress = SEG_ADDRESS
charCount = CHAR_COUNT


class Seg7x4:
    """4-digit 7-segment display controller using HT16K33 over I2C.

    Supports displaying decimal numbers (0-9999), hexadecimal values,
    and a limited set of characters. Uses shared I2C bus for efficient
    resource management.

    Attributes:
        POSITIONS: Buffer positions for each digit.
    """

    # Buffer positions for each digit (tuple for faster indexing)
    POSITIONS: tuple = (0, 2, 4, 6)

    __slots__ = ("_display", "_chars", "_colon", "_bufferSize", "_bytesPerChar")

    def __init__(self, address: int = SEG_ADDRESS) -> None:
        """Initialize the 7-segment display.

        Args:
            address: I2C address of the display (default 0x70).
        """
        # Use shared I2C bus
        self._display = AdafruitSeg7x4(getSharedI2C(), address)

        # Cache frequently used values
        self._chars = CHAR_COUNT * len(self._display.i2c_device)
        self._bufferSize = self._display._buffer_size
        self._bytesPerChar = self._display._bytes_per_char

        # Colon control
        self._colon = Colon(self)

    def showColon(self) -> None:
        """Turn on the center colon indicator."""
        self._colon[0] = True

    def setBrightness(self, value: float) -> None:
        """Set the display brightness.

        Args:
            value: Brightness level from 0.0 (off) to 1.0 (maximum).
        """
        self._display.brightness = value

    def setBlinkRate(self, value: int) -> None:
        """Set the display blink rate.

        Args:
            value: Blink rate from 0 (off) to 3 (fastest).
        """
        self._display.blink_rate = value

    def update(self) -> None:
        """Push the current buffer to the display."""
        self._display.show()

    def clear(self) -> None:
        """Clear all segments on the display."""
        self._display.fill(False)

    def setFull(self, value: str | int | float, decimal: int = 0) -> None:
        """Display a value on the 7-segment display.

        Automatically formats strings, integers, and floating-point numbers
        for the 4-character display.

        Args:
            value: The value to display (str, int, or float).
            decimal: Number of decimal places for numeric values (default 0).

        Raises:
            ValueError: If value type is not str, int, or float.
        """
        if isinstance(value, str):
            self._text(value)
        elif isinstance(value, (int, float)):
            self._number(value, decimal)
        else:
            raise ValueError(f"Unsupported display value type: {type(value)}")

    def set(self, position: int, value: str | int | float) -> None:
        """Set a specific digit position to a value.

        Args:
            position: Display position (0=leftmost, 3=rightmost).
            value: The value to display (str, int, or float).

        Raises:
            ValueError: If position is out of range or value type is unsupported.
        """
        if not 0 <= position < 4:
            raise ValueError("Position must be between 0 and 3.")

        if isinstance(value, str):
            char = value[0] if value else " "
            self._put(char, position)
        elif isinstance(value, int):
            if not 0 <= value <= 9:
                raise ValueError("Integer value must be between 0 and 9.")
            self._put(str(value), position)
        elif isinstance(value, float):
            str_value = str(value)
            if len(str_value) > 4:
                raise ValueError("Float value too long for single character display.")
            self._put(str_value[0], position)
        else:
            raise ValueError(f"Unsupported display value type: {type(value)}")

    def _scroll(self, count: int = 1) -> None:
        """Scroll the display buffer by a number of positions.

        Shifts characters left (positive count) or right (negative count).
        Used internally for text scrolling effects.

        Args:
            count: Number of positions to scroll (default 1).
        """
        if count >= 0:
            offset = 0
        else:
            offset = 1

        for i in range(self._chars - 1):
            self._setBuffer(
                self._adjustedIndex(i + offset),
                self._getBuffer(self._adjustedIndex(i + count)),
            )

    def _put(
        self, char: str, index: int = 0, colon: bool = False, dot: bool = False
    ) -> None:
        """Set a character at the specified display position.

        Converts a character to its 7-segment representation and places it
        at the given index with optional colon and decimal point markers.

        Args:
            char: The character to display.
            index: Position on display (0=leftmost, 3=rightmost).
            colon: Whether to show a colon after the character.
            dot: Whether to show a decimal point.
        """
        if not 0 <= index < self._chars:
            return

        adjIndex = self._adjustedIndex(index)

        # Custom Character Dictionary
        chardict = self._display._chardict
        if chardict and char in chardict:
            self._setBuffer(adjIndex, chardict[char])
            return

        charLower = char.lower()

        # Decimal point
        if charLower == ".":
            targetIdx = adjIndex - 2 if dot else adjIndex
            self._setBuffer(targetIdx, self._getBuffer(targetIdx) | 0b10000000)
            return

        # Use frozen sets for faster membership testing
        if charLower in _HEX_CHARS:
            character = ord(charLower) - 87  # ord('a') - 10 = 87
        elif charLower == "-":
            character = 16
        elif charLower in _DIGIT_CHARS:
            character = ord(charLower) - 48
        elif charLower == " ":
            self._setBuffer(adjIndex, 0x00)
            return
        elif charLower in ":;":
            if charLower == ";":
                self._setBuffer(adjIndex, 0x00)
            return
        elif charLower in "lo":
            self._setBuffer(adjIndex, 0b00111000 if charLower == "l" else 0b00111111)
            return
        else:
            return

        # Set the character with or without colon
        self._setBuffer(adjIndex, NUMBERS[character] | (0x80 if colon else 0))

    def _push(self, char: str, colon: bool = False, dot: bool = False) -> None:
        """Scroll the display and add a character at the end.

        Shifts all characters left by one position and inserts the new
        character at the rightmost position.

        Args:
            char: Character to add.
            colon: Whether to show colon marker.
            dot: Whether to show decimal point marker.
        """
        if char in ":;":
            self._put(char)
        else:
            if (
                char != "."
                or self._getBuffer(self._adjustedIndex(self._chars - 1)) & 0b10000000
            ):
                self._scroll()
                self._put(" ", self._chars - 1, colon, dot)
            self._put(char, self._chars - 1, colon, dot)

    def _text(self, text: str) -> None:
        """Display text on the 7-segment display.

        Processes and displays the input text with support for special
        characters like colons and decimal points.

        Args:
            text: The text string to display.
        """
        # Clear the display before writing new text
        self.clear()

        colonVar = ":" in text
        dotPos = text.find(".")

        if dotPos == 1:
            raise ValueError("The segment display cannot show this decimal.")

        dot = dotPos == 2

        # Right-align the text on a 4-character display
        startPos = max(0, self._chars - len(text))

        for i, character in enumerate(text):
            pos = startPos + i
            colon = False
            dotFlag = False

            if i == 1:
                colon = colonVar
            elif i == 2:
                dotFlag = dot

            self._put(character, pos, colon, dotFlag)

        self.update()

    def _number(self, number: Union[int, float], decimal: int = 0) -> str:
        """Display a number on the 7-segment display.

        Converts numeric values to text and handles decimal formatting.
        Maximum displayable value is 9999.

        Args:
            number: The number to display (0-9999).
            decimal: Number of decimal places to show.

        Returns:
            The formatted text string that was displayed.

        Raises:
            ValueError: If the number is too large for the display.
        """
        stnum = str(number)
        dot = stnum.find(".")

        if (len(stnum) > self._chars + 1) or ((len(stnum) > self._chars) and (dot < 0)):
            raise ValueError(f"Input overflow - {number} is too large for the display!")

        if dot < 0:
            # No decimal point (integer)
            places = len(stnum)
        else:
            places = len(stnum[:dot])

        if places <= 0 < decimal:
            self.clear()
            places = self._chars
            if "." in stnum:
                places += 1

        # Set decimal places if specified
        if places > 0 < decimal < len(stnum[places:]) and dot > 0:
            txt = stnum[: dot + decimal + 1]
        elif places > 0:
            txt = stnum[:places]
        else:
            txt = stnum

        if len(txt) > self._chars + 1:
            raise ValueError(f"Output string ('{txt}') is too long!")

        self._text(txt)
        return txt

    def _adjustedIndex(self, index: int) -> int:
        """Calculate the adjusted buffer index for multi-display setups.

        Maps character position to the correct location in the I2C buffer,
        accounting for daisy-chained display modules.

        Args:
            index: Character position on the display.

        Returns:
            Adjusted index in the buffer.
        """
        offset = (index // self._bytesPerBuffer()) * self._display._buffer_size
        return offset + self.POSITIONS[index % self._bytesPerBuffer()]

    def _charsPerBuffer(self) -> int:
        """Get the number of characters per display buffer.

        Returns:
            Number of character positions in one buffer.
        """
        return self._chars // len(self._display.i2c_device)

    def _bytesPerBuffer(self) -> int:
        """Get the number of bytes per display buffer.

        Returns:
            Buffer size in bytes.
        """
        return self._display._bytes_per_char * self._charsPerBuffer()

    def _charBufferIndex(self, charPos: int) -> int:
        """Calculate the buffer index for a character position.

        Determines where in the I2C buffer a specific character position
        should be stored.

        Args:
            charPos: Character position to convert.

        Returns:
            Corresponding buffer index.
        """
        offset = (charPos // self._charsPerBuffer()) * self._display._buffer_size
        return (
            offset + (charPos % self._charsPerBuffer()) * self._display._bytes_per_char
        )

    def _setBuffer(self, i: int, value: int) -> None:
        """Set a value in the display buffer.

        Args:
            i: Buffer index.
            value: Byte value to set (0x00-0xFF).
        """
        self._display._set_buffer(i, value)

    def _getBuffer(self, i: int) -> int:
        """Get a value from the display buffer.

        Args:
            i: Buffer index.

        Returns:
            Byte value at the specified index.
        """
        return self._display._get_buffer(i)

    def setDigitRaw(self, index: int, bitmask: int) -> None:
        """Set a digit to a raw segment bitmask.

        Allows direct control over individual segments by specifying a bitmask.
        Each bit corresponds to one segment: 0bGFEDCBA.

        Args:
            index: Display position (0=leftmost, 3=rightmost).
            bitmask: Byte with bits set for segments to enable (0x00-0xFF).

        Raises:
            ValueError: If index is out of valid range (0-3).
        """
        if not isinstance(index, int) or not 0 <= index < self._chars:
            raise ValueError(
                f"Index value must be an integer in the range: 0-{self._chars - 1}"
            )

        self._setBuffer(self._adjustedIndex(index), bitmask & 0xFF)

    def __del__(self):
        """Release shared I2C bus reference on object deletion."""
        releaseSharedI2C()


class Colon:
    """Helper class for controlling colon indicators on the display.

    Internal class used by Seg7x4 for managing colon state.
    Not intended for direct instantiation.

    Attributes:
        MASKS: Segment bitmasks for colon positions.
    """

    # pylint: disable=protected-access
    MASKS = (0x80, 0x0C)

    def __init__(self, disp: Seg7x4, numOfColons: int = 1) -> None:
        """Initialize the colon controller.

        Args:
            disp: Parent Seg7x4 display instance.
            numOfColons: Number of colons supported (default 1).
        """
        self._disp = disp
        self._numOfColons = numOfColons

    def __setitem__(self, key: int, value: bool) -> None:
        if key > self._numOfColons - 1:
            raise ValueError("Trying to set a non-existent colon.")

        current = self._disp._getBuffer(0x02)
        if value:
            self._disp._setBuffer(0x02, current | self.MASKS[key])
        else:
            self._disp._setBuffer(0x02, current & ~self.MASKS[key])

    def __getitem__(self, key: int) -> bool:
        if key > self._numOfColons - 1:
            raise ValueError("Trying to access a non-existent colon.")
        return bool(self._disp._getBuffer(0x02) & self.MASKS[key])
