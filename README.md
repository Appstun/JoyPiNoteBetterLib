# JoyPiNoteBetterLib

A Python library for the JoyPi Note – making hardware modules easy to use.

## Installation 

> [!WARNING]
> Using `sudo pip install` can affect system packages. Use virtual environments if possible.

```bash
# Clone the repository
git clone https://github.com/Appstun/JoyPiNoteBetterLib.git
cd JoyPiNoteBetterLib

# Install the library
sudo pip install . --break-system-packages # install globally
# OR
pip install . # install in existing virtual environment
```



## Modules supported
See [modules.md](Modules.md) for full documentation.

| Module       | Description               |
| ------------ | ------------------------- |
| ButtonMatrix | 4x4 keypad                |
| Buzzer       | Sound output              |
| HumTemp      | Temperature & humidity    |
| Joystick     | Analog stick              |
| LcdDisplay   | 16x2 LCD                  |
| LedMatrix    | 8x8 RGB LEDs (needs sudo) |
| LightSensor  | Brightness in Lux         |
| Nfc          | NFC/RFID reader           |
| Relay        | Electrical switch         |
| Seg7x4       | 7-segment display         |
| Servomotor   | 0-180° rotation           |
| SoundSensor  | Sound detection           |
| Stepmotor    | Precise rotation          |
| TiltSensor   | Tilt detection            |
| TouchSensor  | Touch detection           |
| Ultrasonic   | Distance measurement      |
| Vibrator     | Vibration motor           |

<br>

> [!IMPORTANT]
> Some modules (e.g., LedMatrix) require root privileges:
> ```bash
> sudo python3 your_script.py
> ```
