import threading
import time
from typing import List

import adafruit_character_lcd.character_lcd_i2c as LCD

from ..Shared.SharedI2C import getSharedI2C, releaseSharedI2C

# Default I2C address for the LCD display
LCD_ADDRESS: int = 0x21


# Legacy alias for backwards compatibility (deprecated)
lcdAdress = LCD_ADDRESS


class LcdDisplay:
    """I2C character LCD display controller.

    Provides methods for displaying text, controlling backlight and cursor,
    and handling text wrapping and scrolling for longer content.

    Attributes:
        lcd: The underlying Character_LCD_I2C instance.
        wordWrap: Whether to automatically wrap text across lines.
    """

    __slots__ = ("lcd", "wordWrap", "_cols", "_lines")

    def __init__(self, cols: int = 16, rows: int = 2, address: int = LCD_ADDRESS):
        """Initialize the LCD display.

        Args:
            cols: Number of display columns (default 16).
            rows: Number of display rows (default 2).
            address: I2C address of the display (default 0x21).
        """
        self.wordWrap = False
        self.lcd = LCD.Character_LCD_I2C(getSharedI2C(), cols, rows, address=address)

        # Cache dimensions for faster access
        self._cols = self.lcd.columns
        self._lines = self.lcd.lines

        self.clear()

    def clear(self) -> None:
        """Clear all text from the display."""
        self.lcd.clear()

    def displayMessage(self, message: str, line: int = 0) -> None:
        """Display a message on a specific line.

        If wordWrap is enabled, the message will automatically wrap to the
        second line if it exceeds the display width.

        Args:
            message: Text to display.
            line: Line number (0-indexed, default 0).

        Raises:
            ValueError: If line number is out of range.
        """
        if self.wordWrap:
            # Use cached dimensions
            line1 = message[: self._cols]
            self.lcd.cursor_position(0, 0)
            self.lcd.message = line1.ljust(self._cols)

            if self._lines > 1:
                line2 = message[self._cols : self._cols * 2]
                self.lcd.cursor_position(0, 1)
                self.lcd.message = line2.ljust(self._cols)
            return

        if not 0 <= line < self._lines:
            raise ValueError("Line number out of range")

        self.lcd.cursor_position(0, line)
        self.lcd.message = message.ljust(self._cols)

    def setBacklight(self, on: bool) -> None:
        """Turn the backlight on or off.

        Args:
            on: True to turn on, False to turn off.
        """
        self.lcd.backlight = on

    def setDisplay(self, show: bool) -> None:
        """Turn the display on or off.

        Args:
            show: True to turn on, False to turn off.
        """
        self.lcd.display = show

    def setBlink(self, blink: bool) -> None:
        """Enable or disable cursor blinking.

        Args:
            blink: True to enable blinking, False to disable.
        """
        self.lcd.blink = blink

    def setCursor(self, show: bool) -> None:
        """Show or hide the cursor.

        Args:
            show: True to show cursor, False to hide.
        """
        self.lcd.cursor = show

    def setCursorPosition(self, col: int, row: int) -> None:
        """Move the cursor to a specific position.

        Args:
            col: Column number (0-indexed).
            row: Row number (0-indexed).

        Raises:
            ValueError: If position is out of display bounds.
        """
        if row < 0 or row >= self.lcd.lines:
            raise ValueError("Row number out of range")
        if col < 0 or col >= self.lcd.columns:
            raise ValueError("Column number out of range")
        self.lcd.cursor_position(col, row)

    def setColumnAlign(self, enabled: bool) -> None:
        """Enable or disable column alignment for newlines.

        When enabled, text after '\\n' starts directly below the first
        character of the message. When disabled, text starts at column 0.

        Args:
            enabled: True to enable column alignment.
        """
        self.lcd.column_align = enabled

    def setDirection(self, rightToLeft: bool) -> None:
        """Set the text direction.

        Args:
            rightToLeft: True for right-to-left, False for left-to-right.
        """
        if rightToLeft:
            self.lcd.text_direction = self.lcd.RIGHT_TO_LEFT
        else:
            self.lcd.text_direction = self.lcd.LEFT_TO_RIGHT

    def showBigText(self, text: str, delay: float = 0.3) -> None:
        """Display text with smart wrapping and scrolling animation.

        Text is split intelligently and scrolled in blocks matching display height.

        Args:
            text: The text to display.
            delay: Delay in seconds between scroll steps (default 0.3).
        """
        # Split text into lines that fit display width
        lines: List[str] = []
        currentLine = ""
        cols = self._cols

        for word in text.split():
            testLine = f"{currentLine} {word}" if currentLine else word
            if len(testLine) <= cols:
                currentLine = testLine
            else:
                if currentLine:
                    lines.append(currentLine)
                currentLine = word

        if currentLine:
            lines.append(currentLine)

        # Display blocks of lines
        displayHeight = self._lines
        numLines = len(lines)

        for i in range(0, numLines, displayHeight):
            self.lcd.clear()

            for row in range(displayHeight):
                lineIndex = i + row
                if lineIndex < numLines:
                    self.lcd.cursor_position(0, row)
                    self.lcd.message = lines[lineIndex].ljust(cols)

            # Wait before next block (skip on last iteration)
            if i + displayHeight < numLines:
                time.sleep(delay)

    def showFileContent(self, filePath: str, delay: float = 0.3) -> None:
        """Display content of a text file with scrolling.

        Args:
            filePath: Path to the text file.
            delay: Delay in seconds between scroll steps (default 0.3).
        """
        with open(filePath, "r", encoding="utf-8") as file:
            self.showBigText(file.read(), delay=delay)

    def __del__(self):
        """Release shared I2C bus reference on object deletion."""
        releaseSharedI2C()


class ScrollingLinesLcd:
    """LCD display controller for scrolling messages on individual lines.

    Allows setting multiple messages per line that cycle through automatically
    in a background thread. Each line scrolls independently.

    Attributes:
        lcdDisplay: The underlying LcdDisplay instance.
        stopEvent: Threading event to signal stop.
        thread: Background thread for scrolling animation.
        lineMessages: Dictionary mapping line numbers to message lists.
        delay_s: Delay in seconds between message changes.
    """

    def __init__(self, lcdDisplay: LcdDisplay | None = None):
        """Initialize the scrolling LCD controller.

        Args:
            lcdDisplay: Existing LcdDisplay instance to use, or None to create a new one.
        """
        self.lcdDisplay = lcdDisplay if lcdDisplay is not None else LcdDisplay()
        self.stopEvent: threading.Event | None = None
        self.thread = None
        self.lineMessages: dict[str, list[str]] = {"0": [], "1": []}
        self.delay_s = 1.0

    def stop(self, clearMessages: bool = True) -> None:
        """Stop the scrolling animation.

        Args:
            clearMessages: If True, clear all stored messages (default True).
        """
        if self.stopEvent is not None:
            self.stopEvent.set()
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=2)

        if clearMessages:
            self.lineMessages = {"0": [], "1": []}

    def start(self) -> None:
        """Start or restart the scrolling animation.

        Stops any existing animation and starts a new background thread
        that cycles through messages on each line.
        """
        self.stop(False)
        self.stopEvent = threading.Event()
        se = self.stopEvent

        def worker():
            self.lcdDisplay.setBacklight(True)
            
            index = {"0": 0, "1": 0}
            while not se.is_set():
                for i in range(2):
                    lineKey = str(i)
                    if (
                        lineKey in self.lineMessages
                        and len(self.lineMessages[lineKey]) > 0
                    ):
                        self.lcdDisplay.displayMessage(
                            self.lineMessages[lineKey][index[lineKey]], i
                        )

                        index[lineKey] = (index[lineKey] + 1) % len(
                            self.lineMessages[lineKey]
                        )

                for _ in range(int(self.delay_s * 10)):
                    if se.is_set():
                        break
                    time.sleep(0.1)

        self.thread = threading.Thread(target=worker, daemon=True)
        self.thread.start()

    def show(self, messages: list[str], line: int, delay: float | None = None) -> None:
        """Set messages for a line and start scrolling.

        Args:
            messages: List of messages to cycle through.
            line: Line number (0 or 1).
            delay: Optional delay in seconds between messages.
        """
        self.lineMessages[str(line)] = messages
        if delay is not None:
            self.delay_s = delay
        self.start()

    def __del__(self):
        """Stop scrolling on object deletion."""
        self.stop()
