import adafruit_ahtx0

from ..Shared.SharedI2C import getSharedI2C, releaseSharedI2C


class HumidityTemperatureSensor:
    """Humidity and temperature sensor reader via I2C.

    Provides methods for reading relative humidity and temperature values
    from an AHTx0 sensor connected over the shared I2C bus.
    """

    def __init__(self):
        """Initialize the humidity/temperature sensor."""
        self.sensor = adafruit_ahtx0.AHTx0(getSharedI2C())

    def getHumidity(self) -> float:
        """Get the current relative humidity reading.

        Returns:
            Relative humidity as a percentage (0-100).
        """
        return self.sensor.relative_humidity

    def getTemperature(self) -> float:
        """Get the current temperature reading.

        Returns:
            Temperature in degrees Celsius.
        """
        return self.sensor.temperature

    def __del__(self):
        """Release shared I2C bus reference on object deletion."""
        releaseSharedI2C()
