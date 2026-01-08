from typing import List

from ..Shared.SharedSmbus import getSharedSmbus, releaseSharedSmbus


class LightSensor:
    """Light sensor (BH1750) reader via I2C/SMBus.

    Provides methods for reading ambient light levels in lux.
    """

    def __init__(self) -> None:
        """Initialize the light sensor and configure I2C communication."""
        self.DEVICE = 0x5C
        self.POWER_DOWN = 0x00
        self.POWER_ON = 0x01
        self.RESET = 0x07

        self.CONTINUOUS_LOW_RES_MODE = 0x13
        self.CONTINUOUS_HIGH_RES_MODE_1 = 0x10
        self.CONTINUOUS_HIGH_RES_MODE_2 = 0x11
        self.ONE_TIME_HIGH_RES_MODE_1 = 0x20
        self.ONE_TIME_HIGH_RES_MODE_2 = 0x21
        self.ONE_TIME_LOW_RES_MODE = 0x23

        self.bus = getSharedSmbus(1)

    def convertToNumber(self, data: List[int]) -> float:
        """Convert raw sensor data to lux value.

        Args:
            data: Two bytes of raw sensor data.

        Returns:
            Light level in lux.
        """
        return (data[1] + (256 * data[0])) / 1.2

    def readLight(self) -> float:
        """Read the current light level from the sensor.

        Returns:
            Light level in lux.
        """
        data = self.bus.read_i2c_block_data(
            self.DEVICE, self.ONE_TIME_HIGH_RES_MODE_1, 2
        )
        return self.convertToNumber(data)

    def __del__(self) -> None:
        releaseSharedSmbus()
