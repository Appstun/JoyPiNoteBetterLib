import time

from mfrc522 import SimpleMFRC522


class NfcReader:
    """NFC/RFID tag reader using MFRC522 module.

    Provides methods for reading from and writing to NFC/RFID tags
    using the MFRC522 reader module over SPI.

    Attributes:
        reader: The underlying SimpleMFRC522 instance.
    """

    def __init__(self) -> None:
        """Initialize the NFC reader."""
        self.reader = SimpleMFRC522()

    def read(self) -> tuple:
        """Read data from an NFC tag.

        Returns:
            A tuple containing (id, text) where id is the tag's unique
            identifier and text is the stored data. Returns (None, None)
            if reading fails or no tag is present.
        """
        try:
            id, text = self.reader.read()
            if text is not None:
                text = text.strip()
            return id, text
        except Exception:
            return None, None

    def write(self, text: str) -> tuple:
        """Write data to an NFC tag.

        Args:
            text: The text data to write to the tag.

        Returns:
            A tuple containing (id, text) where id is the tag's unique
            identifier and text is the written data. Returns (None, None)
            if writing fails or no tag is present.
        """
        try:
            id, text = self.reader.write(text)
            return id, text
        except Exception:
            return None, None

    def waitForTag(self):
        """Block until an NFC tag is detected, then return its ID and text."""
        while True:
            id, text = self.read()
            if id is not None:
                return id, text
            time.sleep(0.5)
