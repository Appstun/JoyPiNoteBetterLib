#  JoyPiNote Modules & Components

All JoyPiNoteBetterLib modules with imports, methods, and examples.

## 📋 Table of Contents

1. [Button Matrix](#1-button-matrix)
2. [Buzzer](#2-buzzer)
3. [Temperature & Humidity Sensor](#3-temperature--humidity-sensor)
4. [Joystick](#4-joystick)
5. [LCD Text Display](#5-lcd-text-display)
6. [Led Matrix](#6-led-matrix)
7. [Light Sensor](#7-light-sensor)
8. [NFC/RFID Reader](#8-nfcrfid-reader)
9. [Relay](#9-relay)
10. [7-Segment Display](#10-7-segment-display)
11. [Servo Motor](#11-servo-motor)
12. [Sound Sensor](#12-sound-sensor)
13. [Stepper Motor](#13-stepper-motor)
14. [Tilt Sensor](#14-tilt-sensor)
15. [Touch Sensor](#15-touch-sensor)
16. [Ultrasonic Sensor](#16-ultrasonic-sensor)
17. [Vibrator](#17-vibrator)

---

## 1. Button Matrix

A 4x4 keypad with 16 buttons (0-15).

### Import & Initialization
```python
from JoyPiNoteBetterLib import ButtonMatrix

matrix = ButtonMatrix()
```

### Available Methods

| Method                 | Description                          | Returns                |
| ---------------------- | ------------------------------------ | ---------------------- |
| `getPressedKey()`      | Returns the currently pressed button | `int` (0-15) or `None` |
| `getAdcValue()`        | Reads the raw ADC value              | `int` (0-1023)         |
| `readChannel(channel)` | Reads raw ADC from specific channel  | `int` (0-1023)         |

### Example
```python
matrix = ButtonMatrix()

while True:
    key = matrix.getPressedKey()
    if key is not None:
        print(f"Button {key} was pressed")
```

---

## 2. Buzzer

A small speaker that can produce beeping sounds.

### Import & Initialization
```python
from JoyPiNoteBetterLib import Buzzer, PwmBuzzer

# Simple buzzer (on/off only)
buzzer = Buzzer()

# PWM buzzer (with pitch control)
pwm_buzzer = PwmBuzzer()
```

### Available Methods

**Simple Buzzer:**
| Method                | Description                               |
| --------------------- | ----------------------------------------- |
| `buzz(duration=1.0)`  | Beeps for the specified time (in seconds) |
| `setBuzz(True/False)` | Turns the buzzer on or off                |
| `stop()`              | Turns the buzzer off                      |

**PWM Buzzer:**
| Method                     | Description                |
| -------------------------- | -------------------------- |
| `setFrequency(frequency)`  | Changes the pitch (in Hz)  |
| `setDutyCycle(duty_cycle)` | Changes the volume (0-100) |
| `buzz(duty_cycle=50)`      | Starts the tone            |
| `stop()`                   | Stops the tone             |

### Example
```python
buzzer = Buzzer()
buzzer.buzz(0.5)  # Beeps for 0.5 seconds

# Or with PWM for melodies
pwm = PwmBuzzer()
pwm.setFrequency(440)  # Note A4
pwm.buzz(50)
time.sleep(1)
pwm.stop()
```

---

## 3. Temperature & Humidity Sensor

A sensor that measures the current temperature and humidity.

### Import & Initialization
```python
from JoyPiNoteBetterLib import HumidityTemperatureSensor

sensor = HumidityTemperatureSensor()
```

### Available Methods

| Method             | Description         | Returns         |
| ------------------ | ------------------- | --------------- |
| `getTemperature()` | Current temperature | `float` (in °C) |
| `getHumidity()`    | Current humidity    | `float` (in %)  |

### Example
```python
sensor = HumidityTemperatureSensor()

temperature = sensor.getTemperature()
humidity = sensor.getHumidity()

print(f"Temperature: {temperature:.1f}°C")
print(f"Humidity: {humidity:.1f}%")
```

---

## 4. Joystick

A control stick that can be moved in all directions.

### Import & Initialization
```python
from JoyPiNoteBetterLib import Joystick, Direction

joystick = Joystick()
```

### Available Methods

| Method                                   | Description                  | Returns                     |
| ---------------------------------------- | ---------------------------- | --------------------------- |
| `getX()`                                 | X-axis position (left/right) | `int` (0-1023, center ~512) |
| `getY()`                                 | Y-axis position (up/down)    | `int` (0-1023, center ~512) |
| `getXY()`                                | Both values as tuple         | `(x, y)`                    |
| `getDirection(do8Directions, threshold)` | Direction as enum            | `Direction`                 |

### Directions (Direction Enum)
- `Direction.CENTER` - Center
- `Direction.N` - Up (North)
- `Direction.S` - Down (South)
- `Direction.E` - Right (East)
- `Direction.W` - Left (West)
- `Direction.NE, SE, SW, NW` - Diagonals (only with `do8Directions=True`)

### Example
```python
joystick = Joystick()

while True:
    direction = joystick.getDirection()
    
    if direction == Direction.N:
        print("Moving up")
    elif direction == Direction.S:
        print("Moving down")
    elif direction == Direction.E:
        print("Moving right")
    elif direction == Direction.W:
        print("Moving left")
```

---

## 5. LCD Text Display

A 16x2 character LCD display for showing text.

### Import & Initialization
```python
from JoyPiNoteBetterLib import LcdDisplay, ScrollingLinesLcd

lcd = LcdDisplay()

# For auto-scrolling multiple messages per line
scroller = ScrollingLinesLcd()
# Or with existing LCD instance
scroller = ScrollingLinesLcd(lcdDisplay=lcd)
```

### Available Methods

**LcdDisplay:**
| Method                                 | Description                         |
| -------------------------------------- | ----------------------------------- |
| `clear()`                              | Clears the entire screen            |
| `displayMessage(text, line=0)`         | Shows text on a line                |
| `setBacklight(True/False)`             | Backlight on/off                    |
| `setDisplay(True/False)`               | Display on/off                      |
| `setCursor(True/False)`                | Show/hide cursor                    |
| `setBlink(True/False)`                 | Cursor blinking on/off              |
| `setCursorPosition(col, row)`          | Set cursor position                 |
| `setColumnAlign(True/False)`           | Column alignment on/off             |
| `setDirection(True/False)`             | Text direction (RTL/LTR)            |
| `showBigText(text, delay=0.3)`         | Long text with auto-scroll          |
| `showFileContent(filePath, delay=0.3)` | Display file content with scrolling |

**ScrollingLinesLcd:**
| Method                             | Description                                 |
| ---------------------------------- | ------------------------------------------- |
| `show(messages, line, delay=None)` | Set messages for a line and start scrolling |
| `start()`                          | Start the scrolling animation               |
| `stop(True)`                       | Stop the scrolling animation                |

### Example
```python
lcd = LcdDisplay()

lcd.clear()
lcd.displayMessage("Hello", 0)      # Line 1
lcd.displayMessage("World", 1)      # Line 2

# Auto-scroll long text
lcd.showBigText("This is a very long text that scrolls automatically")

# Scrolling multiple messages per line
scroller = ScrollingLinesLcd(lcd)
scroller.show(["Message 1", "Message 2", "Message 3"], line=0, delay=1.0)
scroller.show(["Line 2 A", "Line 2 B"], line=1)

# Stop scrolling
time.sleep(5)
scroller.stop()
```

---

## 6. Led Matrix

An 8x8 matrix with 64 colored LEDs (NeoPixel).

> [!IMPORTANT]
> Requires `sudo` to run!

### Import & Initialization
```python
from JoyPiNoteBetterLib import LedMatrix

matrix = LedMatrix()
```

### Available Methods

| Method                                              | Description                    |
| --------------------------------------------------- | ------------------------------ |
| `clear()`                                           | Turns off all LEDs             |
| `setAll(color)`                                     | Fills all LEDs with a color    |
| `setPixel(position, color)`                         | Sets a single pixel (0-63)     |
| `setBrightness(brightness)`                         | Change brightness (0-255)      |
| `showChar(char, color, offsetX, background)`        | Shows a character              |
| `showText(text, color, background)`                 | Shows text (first char on 8x8) |
| `scrollText(text, color, delay, loops, background)` | Scroll text across display     |
| `update()`                                          | Apply changes to matrix        |

### Colors
Colors are specified as RGB tuples: `(Red, Green, Blue)` with values 0-255.

```python
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
```

### Example
```python
matrix = LedMatrix(brightness=20)

# Set individual pixels
matrix.setPixel(0, (255, 0, 0))  # Red pixel at position 0
matrix.update()

# Show single character
matrix.showChar("A", (0, 255, 0))

# Scroll text
matrix.scrollText("Hello", (0, 255, 0), delay=0.1)

# Scroll text with loops and background color
matrix.scrollText("Hi", (255, 0, 0), delay=0.1, loops=2, background=(0, 0, 50))

# Turn everything off
matrix.clear()
```

---

## 7. Light Sensor

A sensor that measures the ambient brightness (in Lux) via I2C.

### Import & Initialization
```python
from JoyPiNoteBetterLib import LightSensor

sensor = LightSensor()
```

### Available Methods

| Method                  | Description                     | Returns          |
| ----------------------- | ------------------------------- | ---------------- |
| `readLight()`           | Measures current brightness     | `float` (in Lux) |
| `convertToNumber(data)` | Converts raw sensor data to lux | `float` (in Lux) |

### Example
```python
sensor = LightSensor()

brightness = sensor.readLight()
print(f"Brightness: {brightness:.1f} Lux")

if brightness < 50:
    print("It's dark")
else:
    print("It's bright")
```

---

## 8. NFC/RFID Reader

A reader for NFC tags and RFID cards.

### Import & Initialization
```python
from JoyPiNoteBetterLib import NfcReader

nfc = NfcReader()
```

### Available Methods

| Method         | Description                   | Returns                        |
| -------------- | ----------------------------- | ------------------------------ |
| `read()`       | Reads data from a tag         | `(id, text)` or `(None, None)` |
| `write(text)`  | Writes data to a tag          | `(id, text)` or `(None, None)` |
| `waitForTag()` | Waits until a tag is detected | `(id, text)`                   |

### Example
```python
nfc = NfcReader()

print("Hold an NFC tag to the reader...")
id, text = nfc.waitForTag()

print(f"Tag ID: {id}")
print(f"Stored text: {text}")

# Write text to tag
nfc.write("Hello NFC")
```

---

## 9. Relay

An electrical switch for turning devices on/off.

### Import & Initialization
```python
from JoyPiNoteBetterLib import Relay

relay = Relay()
```

### Available Methods

| Method      | Description         |
| ----------- | ------------------- |
| `turnOn()`  | Turns the relay on  |
| `turnOff()` | Turns the relay off |

### Example
```python
relay = Relay()

relay.turnOn()   # Turn device on
time.sleep(5)
relay.turnOff()  # Turn device off
```

---

## 10. 7-Segment Display

A 4-digit 7-segment display for numbers and simple characters.

### Import & Initialization
```python
from JoyPiNoteBetterLib import Seg7x4

display = Seg7x4()
```

### Available Methods

| Method                      | Description                  |
| --------------------------- | ---------------------------- |
| `setFull(value, decimal=0)` | Shows number/text on display |
| `set(position, value)`      | Sets a single digit (0-3)    |
| `showColon()`               | Shows the colon              |
| `clear()`                   | Clears the display           |
| `setBrightness(0.0-1.0)`    | Set brightness               |
| `setBlinkRate(0-3)`         | Set blink rate               |
| `update()`                  | Apply changes to display     |

### Example
```python
display = Seg7x4()

# Show number
display.setFull(1234)
display.update()

# Show time (e.g., 12:30)
display.setFull(1230)
display.showColon()
display.update()

# Decimal number
display.setFull(3.14, decimal=2)
display.update()

# Set individual digits
display.set(0, '1')
display.set(1, '2')
display.set(2, '3')
display.set(3, '4')
display.update()
```

---

## 11. Servo Motor

A motor that can rotate to a specific angle (0-180°).

### Import & Initialization
```python
from JoyPiNoteBetterLib import Servomotor

servo = Servomotor(90)  # Starting position at 90°
```

### Available Methods

| Method                       | Description                    |
| ---------------------------- | ------------------------------ |
| `setDirection(angle, speed)` | Rotates to the specified angle |
| `getDirection()`             | Returns current angle          |

### Parameters
- `startDirection`: Initial angle position (0-180 degrees, required)
- `angle`: Target angle (0-180 degrees)
- `speed`: Step size (0 = single step, higher values = faster transitions)

### Example
```python
servo = Servomotor(90)  # Starts at center position

servo.setDirection(0, 5)    # Rotates to 0° (slowly)
servo.setDirection(180, 10) # Rotates to 180° (faster)
servo.setDirection(90, 0)   # Back to center (single-step movement)
```

---

## 12. Sound Sensor

A sensor that detects when a sound is made.

### Import & Initialization
```python
from JoyPiNoteBetterLib import SoundSensor

sensor = SoundSensor()
```

### Available Methods

| Method              | Description                   | Returns      |
| ------------------- | ----------------------------- | ------------ |
| `isSoundDetected()` | Checks if a sound is detected | `True/False` |

### Example
```python
sensor = SoundSensor()

while True:
    if sensor.isSoundDetected():
        print("Sound detected")
    time.sleep(0.1)
```

---

## 13. Stepper Motor

A motor that can rotate precisely in small steps.

### Import & Initialization
```python
from JoyPiNoteBetterLib import Stepmotor

motor = Stepmotor()
```

### Available Methods

| Method                           | Description                            |
| -------------------------------- | -------------------------------------- |
| `setSpeed(1-100)`                | Set speed                              |
| `turnSteps(steps)`               | Rotate by X steps (negative = reverse) |
| `turnDegrees(degrees)`           | Rotate by X degrees                    |
| `turnDistance(distance, radius)` | Rotate for a distance (with wheel)     |
| `release()`                      | Release coils (free rotation, no heat) |

### Example
```python
motor = Stepmotor()

motor.setSpeed(50)           # Medium speed
motor.turnDegrees(90)        # 90° clockwise
motor.turnDegrees(-90)       # 90° counter-clockwise
motor.turnSteps(512)         # 512 steps forward
motor.release()              # Release motor coils
```

---

## 14. Tilt Sensor

A sensor that detects if the board is tilted.

### Import & Initialization
```python
from JoyPiNoteBetterLib import TiltSensor

sensor = TiltSensor()
```

### Available Methods

| Method       | Description                   | Returns      |
| ------------ | ----------------------------- | ------------ |
| `isTilted()` | Checks if the board is tilted | `True/False` |

### Example
```python
sensor = TiltSensor()

while True:
    if sensor.isTilted():
        print("The board is tilted")
    else:
        print("The board is level")
    time.sleep(0.5)
```

---

## 15. Touch Sensor

A sensor that detects touch.

### Import & Initialization
```python
from JoyPiNoteBetterLib import TouchSensor

sensor = TouchSensor()
```

### Available Methods

| Method                   | Description                           | Returns      |
| ------------------------ | ------------------------------------- | ------------ |
| `isTouched()`            | Checks if the sensor is being touched | `True/False` |
| `waitForTouch(interval)` | Waits for a touch                     | - (blocks)   |

### Example
```python
sensor = TouchSensor()

print("Touch the sensor...")
sensor.waitForTouch()
print("Touch detected")

# Or in a loop
while True:
    if sensor.isTouched():
        print("Touched")
    time.sleep(0.1)
```

---

## 16. Ultrasonic Sensor

A sensor that measures distance to objects (like a parking sensor).

### Import & Initialization
```python
from JoyPiNoteBetterLib import UltrasonicSensor

sensor = UltrasonicSensor()
```

### Available Methods

| Method                 | Description                    | Returns                              |
| ---------------------- | ------------------------------ | ------------------------------------ |
| `getDistance(timeout)` | Measures the distance          | `float` (in cm) or `-1.0` on timeout |
| `sendTriggerPulse()`   | Send a trigger pulse to sensor | -                                    |
| `waitForEcho(timeout)` | Wait for echo signal           | `True/False`                         |

### Example
```python
sensor = UltrasonicSensor()

while True:
    distance = sensor.getDistance()
    
    if distance == -1:
        print("No object detected")
    elif distance < 10:
        print(f"Warning! Object only {distance:.1f} cm away")
    else:
        print(f"Distance: {distance:.1f} cm")
    
    time.sleep(0.5)
```

---

## 17. Vibrator

A small motor that produces vibrations (like in a phone).

### Import & Initialization
```python
from JoyPiNoteBetterLib import Vibrator, PwmVibrator

# Simple vibrator (on/off only)
vibrator = Vibrator()

# PWM vibrator (with intensity control)
pwm_vibrator = PwmVibrator()
```

### Available Methods

**Simple Vibrator:**
| Method                   | Description            |
| ------------------------ | ---------------------- |
| `vibrate(duration=1.0)`  | Vibrates for X seconds |
| `setVibrate(True/False)` | Vibration on/off       |

**PWM Vibrator:**
| Method                | Description             |
| --------------------- | ----------------------- |
| `setIntensity(0-100)` | Set vibration intensity |
| `stop()`              | Stop vibration          |

### Example
```python
# Simple vibration
vibrator = Vibrator()
vibrator.vibrate(0.5)  # Vibrate for 0.5 seconds

# With variable intensity
pwm = PwmVibrator()
pwm.setIntensity(30)   # Light vibration
time.sleep(1)
pwm.setIntensity(100)  # Strong vibration
time.sleep(1)
pwm.stop()
```

---

## 🔧 General Tips

### Cleanup
Modules automatically clean up when the program ends. If you have issues, you can also manually call `del {object}`.

### Error Handling
```python
try:
    sensor = UltrasonicSensor()
    distance = sensor.getDistance()
except Exception as e:
    print(f"Error: {e}")
```

### Root Privileges (sudo)
Some modules (e.g., `LedMatrix`) require root privileges:
```bash
sudo python3 my_script.py
```
