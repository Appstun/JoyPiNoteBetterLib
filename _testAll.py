#!/usr/bin/env python3
"""Test script for JoyPiNoteBetterLib components.

This script tests all hardware components and their methods to verify
functionality. Each component is tested in isolation with visual/interactive
feedback where possible.

Usage:
    python testAll.py [component]

    Components: all, led, lcd, seg7, button, joystick, touch, tilt, buzzer, vibrator,
                humtemp, sound, light, ultrasonic, nfc, servo, stepmotor, clear, shared, imports
    Default: all
"""

import sys
import time

# Test results tracking
_testResults: dict = {"passed": 0, "failed": 0, "skipped": 0}


doSoundTest = True


def printHeader(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")


def printTest(name: str, passed: bool, message: str = "") -> None:
    """Print test result and update counters."""
    status = "✓ PASS" if passed else "✗ FAIL"
    _testResults["passed" if passed else "failed"] += 1
    msg = f" - {message}" if message else ""
    print(f"  {status}: {name}{msg}")


def printSkip(name: str, reason: str = "") -> None:
    """Print skipped test."""
    _testResults["skipped"] += 1
    msg = f" - {reason}" if reason else ""
    print(f"  ⊘ SKIP: {name}{msg}")


def testImports() -> bool:
    """Test that all modules can be imported."""
    printHeader("Testing Imports")

    allPassed = True

    try:
        from JoyPiNoteBetterLib import LedMatrix

        printTest("Import LedMatrix", True)
    except ImportError as e:
        printTest("Import LedMatrix", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import LcdDisplay

        printTest("Import LcdDisplay", True)
    except ImportError as e:
        printTest("Import LcdDisplay", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import Seg7x4

        printTest("Import Seg7x4", True)
    except ImportError as e:
        printTest("Import Seg7x4", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import ButtonMatrix

        printTest("Import ButtonMatrix", True)
    except ImportError as e:
        printTest("Import ButtonMatrix", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import Direction, Joystick

        printTest("Import Joystick, Direction", True)
    except ImportError as e:
        printTest("Import Joystick, Direction", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import TouchSensor

        printTest("Import TouchSensor", True)
    except ImportError as e:
        printTest("Import TouchSensor", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import TiltSensor

        printTest("Import TiltSensor", True)
    except ImportError as e:
        printTest("Import TiltSensor", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib.Shared.SharedSpi import getSharedSpi, releaseSharedSpi

        printTest("Import SharedSpi functions", True)
    except ImportError as e:
        printTest("Import SharedSpi functions", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import Buzzer

        printTest("Import Buzzer", True)
    except ImportError as e:
        printTest("Import Buzzer", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import Vibrator

        printTest("Import Vibrator", True)
    except ImportError as e:
        printTest("Import Vibrator", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import HumidityTemperatureSensor

        printTest("Import HumidityTemperatureSensor", True)
    except ImportError as e:
        printTest("Import HumidityTemperatureSensor", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import SoundSensor

        printTest("Import SoundSensor", True)
    except ImportError as e:
        printTest("Import SoundSensor", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import LightSensor

        printTest("Import LightSensor", True)
    except ImportError as e:
        printTest("Import LightSensor", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import UltrasonicSensor

        printTest("Import UltrasonicSensor", True)
    except ImportError as e:
        printTest("Import UltrasonicSensor", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import NfcReader

        printTest("Import NfcReader", True)
    except ImportError as e:
        printTest("Import NfcReader", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import PwmBuzzer

        printTest("Import PwmBuzzer", True)
    except ImportError as e:
        printTest("Import PwmBuzzer", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import PwmVibrator

        printTest("Import PwmVibrator", True)
    except ImportError as e:
        printTest("Import PwmVibrator", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import Servomotor

        printTest("Import Servo", True)
    except ImportError as e:
        printTest("Import Servo", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import Stepmotor

        printTest("Import Stepmotor", True)
    except ImportError as e:
        printTest("Import Stepmotor", False, str(e))
        allPassed = False

    try:
        from JoyPiNoteBetterLib import ModuleReset

        printTest("Import ModuleReset", True)
    except ImportError as e:
        printTest("Import ModuleReset", False, str(e))
        allPassed = False

    return allPassed

def testRelay() -> None:
    """Test Relay component."""
    printHeader("Testing Relay")

    try:
        from JoyPiNoteBetterLib import Relay

        # Test instantiation
        relay = Relay(pin=23)
        printTest("Relay instantiation", True)

        try:
            relay.turnOn()
            printTest("turnOn", True)
        except Exception as e:
            printTest("turnOn", False, str(e))

        try:
            relay.turnOff()
            printTest("turnOff", True)
        except Exception as e:
            printTest("turnOff", False, str(e))

    except Exception as e:
        printTest("Relay initialization", False, str(e))

def testLedMatrix() -> None:
    """Test LedMatrix component."""
    printHeader("Testing LedMatrix")

    try:
        from JoyPiNoteBetterLib import LedMatrix

        # Test instantiation
        matrix = LedMatrix(brightness=50)
        printTest("LedMatrix instantiation", True)

        # Test setBrightness
        try:
            matrix.setBrightness(100)
            printTest("setBrightness(100)", True)
        except Exception as e:
            printTest("setBrightness(100)", False, str(e))

        # Test setBrightness validation
        try:
            matrix.setBrightness(300)  # Should raise ValueError
            printTest(
                "setBrightness validation", False, "Should have raised ValueError"
            )
        except ValueError:
            printTest(
                "setBrightness validation", True, "Correctly rejected invalid value"
            )
        except Exception as e:
            printTest("setBrightness validation", False, str(e))

        # Test setPixel
        try:
            matrix.setPixel(0, (255, 0, 0))
            matrix.setPixel(63, (0, 255, 0))
            printTest("setPixel", True)
        except Exception as e:
            printTest("setPixel", False, str(e))

        # Test setPixel validation
        try:
            matrix.setPixel(100, (255, 0, 0))  # Should raise ValueError
            printTest("setPixel validation", False, "Should have raised ValueError")
        except ValueError:
            printTest(
                "setPixel validation", True, "Correctly rejected invalid position"
            )
        except Exception as e:
            printTest("setPixel validation", False, str(e))

        # Test setAll
        try:
            matrix.setAll((0, 0, 255))
            printTest("setAll", True)
        except Exception as e:
            printTest("setAll", False, str(e))

        # Test update
        try:
            matrix.update()
            printTest("update", True)
        except Exception as e:
            printTest("update", False, str(e))

        # Test clean
        try:
            matrix.clear()
            printTest("clean", True)
        except Exception as e:
            printTest("clean", False, str(e))

        # Test showChar
        try:
            matrix.showChar("A", (255, 255, 0))
            time.sleep(0.3)
            printTest("showChar", True)
        except Exception as e:
            printTest("showChar", False, str(e))

        # Test showText
        try:
            matrix.showText("Hi", (0, 255, 255))
            time.sleep(0.3)
            printTest("showText", True)
        except Exception as e:
            printTest("showText", False, str(e))

        # Test scrollText (short)
        try:
            matrix.scrollText("AB", (255, 0, 255), delay=0.05, loops=1)
            printTest("scrollText", True)
        except Exception as e:
            printTest("scrollText", False, str(e))

        # Clean up
        matrix.clear()

    except Exception as e:
        printTest("LedMatrix initialization", False, str(e))


def testLcdDisplay() -> None:
    """Test LcdDisplay component."""
    printHeader("Testing LcdDisplay")

    try:
        from JoyPiNoteBetterLib import LcdDisplay

        # Test instantiation
        lcd = LcdDisplay(cols=16, rows=2)
        printTest("LcdDisplay instantiation", True)

        # Test clear
        try:
            lcd.clear()
            printTest("clear", True)
        except Exception as e:
            printTest("clear", False, str(e))

        # Test displayMessage
        try:
            lcd.displayMessage("Test Line 1", line=0)
            lcd.displayMessage("Test Line 2", line=1)
            printTest("displayMessage", True)
        except Exception as e:
            printTest("displayMessage", False, str(e))

        time.sleep(0.5)

        # Test setBacklight
        try:
            lcd.setBacklight(False)
            time.sleep(0.2)
            lcd.setBacklight(True)
            printTest("setBacklight", True)
        except Exception as e:
            printTest("setBacklight", False, str(e))

        # Test setDisplay
        try:
            lcd.setDisplay(False)
            time.sleep(0.2)
            lcd.setDisplay(True)
            printTest("setDisplay", True)
        except Exception as e:
            printTest("setDisplay", False, str(e))

        # Test setCursor
        try:
            lcd.setCursor(True)
            time.sleep(0.2)
            lcd.setCursor(False)
            printTest("setCursor", True)
        except Exception as e:
            printTest("setCursor", False, str(e))

        # Test setBlink
        try:
            lcd.setBlink(True)
            time.sleep(0.3)
            lcd.setBlink(False)
            printTest("setBlink", True)
        except Exception as e:
            printTest("setBlink", False, str(e))

        # Test setCursorPosition
        try:
            lcd.setCursorPosition(0, 0)
            printTest("setCursorPosition", True)
        except Exception as e:
            printTest("setCursorPosition", False, str(e))

        # Test setCursorPosition validation
        try:
            lcd.setCursorPosition(100, 100)
            printTest(
                "setCursorPosition validation", False, "Should have raised ValueError"
            )
        except ValueError:
            printTest(
                "setCursorPosition validation",
                True,
                "Correctly rejected invalid position",
            )
        except Exception as e:
            printTest("setCursorPosition validation", False, str(e))

        # Test setColumnAlign
        try:
            lcd.setColumnAlign(True)
            lcd.setColumnAlign(False)
            printTest("setColumnAlign", True)
        except Exception as e:
            printTest("setColumnAlign", False, str(e))

        # Test setDirection
        try:
            lcd.setDirection(False)  # Left to right
            printTest("setDirection", True)
        except Exception as e:
            printTest("setDirection", False, str(e))

        # Test wordWrap property
        try:
            lcd.wordWrap = True
            lcd.displayMessage("This is a longer text that should wrap")
            time.sleep(0.5)
            lcd.wordWrap = False
            printTest("wordWrap", True)
        except Exception as e:
            printTest("wordWrap", False, str(e))

        # Clean up
        lcd.clear()
        lcd.displayMessage("Tests complete!", line=0)

    except Exception as e:
        printTest("LcdDisplay initialization", False, str(e))


def testSeg7x4() -> None:
    """Test Seg7x4 component."""
    printHeader("Testing Seg7x4")

    try:
        from JoyPiNoteBetterLib import Seg7x4

        # Test instantiation
        seg = Seg7x4()
        printTest("Seg7x4 instantiation", True)

        # Test clear
        try:
            seg.clear()
            seg.update()
            printTest("clear", True)
        except Exception as e:
            printTest("clear", False, str(e))

        # Test setFull with integer
        try:
            seg.setFull(1234)
            printTest("setFull(int)", True)
        except Exception as e:
            printTest("setFull(int)", False, str(e))

        time.sleep(0.5)

        # Test setFull with float
        try:
            seg.setFull(12.34, decimal=2)
            printTest("setFull(float)", True)
        except Exception as e:
            printTest("setFull(float)", False, str(e))

        time.sleep(0.5)

        # Test setFull with string
        try:
            seg.setFull("AbCd")
            printTest("setFull(str)", True)
        except Exception as e:
            printTest("setFull(str)", False, str(e))

        time.sleep(0.5)

        # Test set single position
        try:
            seg.clear()
            seg.set(0, 1)
            seg.set(1, 2)
            seg.set(2, 3)
            seg.set(3, 4)
            seg.update()
            printTest("set(position, value)", True)
        except Exception as e:
            printTest("set(position, value)", False, str(e))

        time.sleep(0.5)

        # Test set validation
        try:
            seg.set(10, 1)  # Should raise ValueError
            printTest("set validation", False, "Should have raised ValueError")
        except ValueError:
            printTest("set validation", True, "Correctly rejected invalid position")
        except Exception as e:
            printTest("set validation", False, str(e))

        # Test setBrightness
        try:
            seg.setBrightness(0.6)
            printTest("setBrightness", True)
        except Exception as e:
            printTest("setBrightness", False, str(e))

        # Test setBlinkRate
        try:
            seg.setBlinkRate(1)
            time.sleep(0.5)
            seg.setBlinkRate(0)
            printTest("setBlinkRate", True)
        except Exception as e:
            printTest("setBlinkRate", False, str(e))

        # Test showColon
        try:
            seg.setFull("12:34")
            seg.showColon()
            seg.update()
            printTest("showColon", True)
        except Exception as e:
            printTest("showColon", False, str(e))

        time.sleep(0.5)

        # Test setDigitRaw
        try:
            seg.clear()
            seg.setDigitRaw(0, 0x3F)  # Display "0"
            seg.setDigitRaw(1, 0x06)  # Display "1"
            seg.update()
            printTest("setDigitRaw", True)
        except Exception as e:
            printTest("setDigitRaw", False, str(e))

        # Test setDigitRaw validation
        try:
            seg.setDigitRaw(10, 0x3F)  # Should raise ValueError
            printTest("setDigitRaw validation", False, "Should have raised ValueError")
        except ValueError:
            printTest(
                "setDigitRaw validation", True, "Correctly rejected invalid index"
            )
        except Exception as e:
            printTest("setDigitRaw validation", False, str(e))

        # Clean up
        time.sleep(0.5)
        seg.clear()
        seg.update()

    except Exception as e:
        printTest("Seg7x4 initialization", False, str(e))


def testButtonMatrix() -> None:
    """Test ButtonMatrix component."""
    printHeader("Testing ButtonMatrix")

    try:
        from JoyPiNoteBetterLib import ButtonMatrix

        # Test instantiation
        buttons = ButtonMatrix(keyChannel=4)
        printTest("ButtonMatrix instantiation", True)

        # Test readChannel
        try:
            value = buttons.readChannel(4)
            printTest("readChannel", True, f"Value: {value}")
        except Exception as e:
            printTest("readChannel", False, str(e))

        # Test getAdcValue
        try:
            value = buttons.getAdcValue()
            printTest("getAdcValue", True, f"Value: {value}")
        except Exception as e:
            printTest("getAdcValue", False, str(e))

        # Test getPressedKey
        try:
            key = buttons.getPressedKey()
            adcVal = buttons.getAdcValue()
            if key is None:
                printTest("getPressedKey", True, f"No key pressed (ADC: {adcVal})")
            else:
                printTest(
                    "getPressedKey",
                    True,
                    f"Key: {key} (ADC: {adcVal}) - Note: unexpected if not pressing",
                )
        except Exception as e:
            printTest("getPressedKey", False, str(e))

        # Interactive test hint
        print("\n  ℹ Interactive test: Press a button within 3 seconds...")
        startTime = time.time()
        keyPressed = None
        while time.time() - startTime < 3:
            key = buttons.getPressedKey()
            if key is not None:
                keyPressed = key
                break
            time.sleep(0.05)

        if keyPressed is not None:
            printTest("Interactive button press", True, f"Button {keyPressed} detected")
        else:
            printSkip("Interactive button press", "No button pressed (timeout)")

    except Exception as e:
        printTest("ButtonMatrix initialization", False, str(e))


def testJoystick() -> None:
    """Test Joystick component."""
    printHeader("Testing Joystick")

    try:
        from JoyPiNoteBetterLib import Direction, Joystick

        # Test instantiation
        joy = Joystick(xChannel=1, yChannel=0)
        printTest("Joystick instantiation", True)

        # Test Direction enum
        try:
            _ = Direction.CENTER
            _ = Direction.N
            _ = Direction.NE
            printTest("Direction enum", True)
        except Exception as e:
            printTest("Direction enum", False, str(e))

        # Test getX
        try:
            x = joy.getX()
            printTest("getX", True, f"Value: {x}")
        except Exception as e:
            printTest("getX", False, str(e))

        # Test getY
        try:
            y = joy.getY()
            printTest("getY", True, f"Value: {y}")
        except Exception as e:
            printTest("getY", False, str(e))

        # Test getXY
        try:
            x, y = joy.getXY()
            # Values should be near 512 when centered
            if 400 < x < 600 and 400 < y < 600:
                printTest("getXY", True, f"Values: ({x}, {y}) - centered")
            elif x == 0 and y == 0:
                printTest(
                    "getXY", False, f"Values: ({x}, {y}) - likely SPI buffer issue"
                )
            else:
                printTest("getXY", True, f"Values: ({x}, {y}) - joystick moved?")
        except Exception as e:
            printTest("getXY", False, str(e))

        # Test getDirection (4 directions)
        try:
            x, y = joy.getXY()
            direction = joy.getDirection(do8Directions=False, threshold=100)
            if direction == Direction.CENTER:
                printTest(
                    "getDirection (4-dir)",
                    True,
                    f"Direction: {direction.name} (X:{x}, Y:{y})",
                )
            else:
                printTest(
                    "getDirection (4-dir)",
                    True,
                    f"Direction: {direction.name} (X:{x}, Y:{y}) - Note: expected CENTER if idle",
                )
        except Exception as e:
            printTest("getDirection (4-dir)", False, str(e))

        # Test getDirection (8 directions)
        try:
            direction = joy.getDirection(do8Directions=True, threshold=100)
            printTest("getDirection (8-dir)", True, f"Direction: {direction.name}")
        except Exception as e:
            printTest("getDirection (8-dir)", False, str(e))

        # Interactive test hint
        print("\n  ℹ Interactive test: Move joystick within 3 seconds...")
        startTime = time.time()
        directionMoved = None
        while time.time() - startTime < 3:
            direction = joy.getDirection(do8Directions=True, threshold=100)
            if direction != Direction.CENTER:
                directionMoved = direction
                break
            time.sleep(0.05)

        if directionMoved is not None:
            printTest(
                "Interactive joystick move", True, f"Direction: {directionMoved.name}"
            )
        else:
            printSkip("Interactive joystick move", "No movement detected (timeout)")

    except Exception as e:
        printTest("Joystick initialization", False, str(e))


def testTouch() -> None:
    """Test Touch component."""
    printHeader("Testing Touch")

    try:
        from JoyPiNoteBetterLib import TouchSensor

        # Test instantiation
        touch = TouchSensor(pin=17)
        printTest("Touch instantiation", True)

        # Test isTouched
        try:
            touched = touch.isTouched()
            printTest("isTouched", True, f"State: {touched}")
        except Exception as e:
            printTest("isTouched", False, str(e))

        # Interactive test hint
        print("\n  ℹ Interactive test: Touch the sensor within 3 seconds...")
        startTime = time.time()
        touchDetected = False
        while time.time() - startTime < 3:
            if touch.isTouched():
                touchDetected = True
                break
            time.sleep(0.05)

        if touchDetected:
            printTest("Interactive touch detection", True, "Touch detected")
        else:
            printSkip("Interactive touch detection", "No touch detected (timeout)")

        # Note: waitForTouch is blocking, so we skip it in automated tests
        printSkip("waitForTouch", "Blocking method - skipped in automated test")

    except Exception as e:
        printTest("Touch initialization", False, str(e))


def testTilt() -> None:
    """Test TiltSensor component."""
    printHeader("Testing TiltSensor")

    try:
        from JoyPiNoteBetterLib import TiltSensor

        # Test instantiation
        tilt = TiltSensor(pin=22)
        printTest("TiltSensor instantiation", True)

        # Test isTilted
        try:
            tilted = tilt.isTilted()
            printTest("isTilted", True, f"State: {tilted}")
        except Exception as e:
            printTest("isTilted", False, str(e))

        # Interactive test hint
        print("\n  ℹ Interactive test: Tilt the sensor within 3 seconds...")
        startTime = time.time()
        tiltDetected = False
        while time.time() - startTime < 3:
            if tilt.isTilted():
                tiltDetected = True
                break
            time.sleep(0.05)

        if tiltDetected:
            printTest("Interactive tilt detection", True, "Tilt detected")
        else:
            printSkip("Interactive tilt detection", "No tilt detected (timeout)")

    except Exception as e:
        printTest("TiltSensor initialization", False, str(e))


def testSharedResources() -> None:
    """Test shared SPI and I2C resources."""
    printHeader("Testing Shared Resources")

    # Test SharedSpi
    try:
        from JoyPiNoteBetterLib.Shared.SharedSpi import getSharedSpi, releaseSharedSpi

        spi1 = getSharedSpi()
        spi2 = getSharedSpi()

        # Both should return the same instance
        if spi1 is spi2:
            printTest("SharedSpi singleton", True, "Same instance returned")
        else:
            printTest("SharedSpi singleton", False, "Different instances returned")

        releaseSharedSpi()
        releaseSharedSpi()
        printTest("SharedSpi release", True)

    except Exception as e:
        printTest("SharedSpi", False, str(e))

    # Test shared I2C
    try:
        from JoyPiNoteBetterLib.Shared.SharedI2C import getSharedI2C, releaseSharedI2C

        i2c1 = getSharedI2C()
        i2c2 = getSharedI2C()

        if i2c1 is i2c2:
            printTest("SharedI2C singleton", True, "Same instance returned")
        else:
            printTest("SharedI2C singleton", False, "Different instances returned")

        releaseSharedI2C()
        releaseSharedI2C()
        printTest("SharedI2C release", True)

    except Exception as e:
        printTest("SharedI2C", False, str(e))


def testBuzzer() -> None:
    """Test Buzzer and PwmBuzzer components."""

    printHeader("Testing Buzzer")

    if not doSoundTest:
        printSkip("Buzzer tests", "Sound tests disabled")
        return

    try:
        from JoyPiNoteBetterLib import Buzzer

        # Test instantiation
        buzzer = Buzzer(pin=18)
        printTest("Buzzer instantiation", True)

        # Test setBuzz (activate)
        try:
            buzzer.setBuzz(True)
            time.sleep(0.1)
            buzzer.setBuzz(False)
            printTest("setBuzz", True)
        except Exception as e:
            printTest("setBuzz", False, str(e))

        # Test buzz with duration
        try:
            buzzer.buzz(duration=0.1)
            printTest("buzz(duration)", True)
        except Exception as e:
            printTest("buzz(duration)", False, str(e))

        # Test stop
        try:
            buzzer.stop()
            printTest("stop", True)
        except Exception as e:
            printTest("stop", False, str(e))

    except Exception as e:
        printTest("Buzzer initialization", False, str(e))


def testVibrator() -> None:
    """Test Vibrator component."""

    printHeader("Testing Vibrator")

    if not doSoundTest:
        printSkip("Vibrator tests", "Sound tests disabled")
        return

    try:
        from JoyPiNoteBetterLib import Vibrator

        # Test instantiation
        vibrator = Vibrator(pin=27)
        printTest("Vibrator instantiation", True)

        # Test setVibrate (activate)
        try:
            vibrator.setVibrate(True)
            time.sleep(0.1)
            vibrator.setVibrate(False)
            printTest("setVibrate", True)
        except Exception as e:
            printTest("setVibrate", False, str(e))

        # Test vibrate with duration
        try:
            vibrator.vibrate(duration=0.1)
            printTest("vibrate(duration)", True)
        except Exception as e:
            printTest("vibrate(duration)", False, str(e))

    except Exception as e:
        printTest("Vibrator initialization", False, str(e))


def testHumidityTemperatureSensor() -> None:
    """Test HumidityTemperatureSensor component."""
    printHeader("Testing HumidityTemperatureSensor")

    try:
        from JoyPiNoteBetterLib import HumidityTemperatureSensor

        # Test instantiation
        sensor = HumidityTemperatureSensor()
        printTest("HumidityTemperatureSensor instantiation", True)

        # Test getTemperature
        try:
            temp = sensor.getTemperature()
            if -40 <= temp <= 85:  # Reasonable temperature range
                printTest("getTemperature", True, f"Value: {temp:.1f}°C")
            else:
                printTest("getTemperature", False, f"Unreasonable value: {temp}°C")
        except Exception as e:
            printTest("getTemperature", False, str(e))

        # Test getHumidity
        try:
            humidity = sensor.getHumidity()
            if 0 <= humidity <= 100:  # Valid humidity range
                printTest("getHumidity", True, f"Value: {humidity:.1f}%")
            else:
                printTest("getHumidity", False, f"Unreasonable value: {humidity}%")
        except Exception as e:
            printTest("getHumidity", False, str(e))

    except Exception as e:
        printTest("HumidityTemperatureSensor initialization", False, str(e))


def testSoundSensor() -> None:
    """Test SoundSensor component."""
    printHeader("Testing SoundSensor")

    try:
        from JoyPiNoteBetterLib import SoundSensor

        # Test instantiation
        sensor = SoundSensor(pin=24)
        printTest("SoundSensor instantiation", True)

        # Test isSoundDetected
        try:
            detected = sensor.isSoundDetected()
            printTest("isSoundDetected", True, f"State: {detected}")
        except Exception as e:
            printTest("isSoundDetected", False, str(e))

        # Interactive test hint
        print("\n  ℹ Interactive test: Make a loud sound within 3 seconds...")
        startTime = time.time()
        soundDetected = False
        while time.time() - startTime < 3:
            if sensor.isSoundDetected():
                soundDetected = True
                break
            time.sleep(0.05)

        if soundDetected:
            printTest("Interactive sound detection", True, "Sound detected")
        else:
            printSkip("Interactive sound detection", "No sound detected (timeout)")

    except Exception as e:
        printTest("SoundSensor initialization", False, str(e))


def testLightSensor() -> None:
    """Test LightSensor component."""
    printHeader("Testing LightSensor")

    try:
        from JoyPiNoteBetterLib import LightSensor

        # Test instantiation
        sensor = LightSensor()
        printTest("LightSensor instantiation", True)

        # Test readLight
        try:
            lux = sensor.readLight()
            if 0 <= lux <= 65535:  # Valid lux range for BH1750
                printTest("readLight", True, f"Value: {lux:.2f} lux")
            else:
                printTest("readLight", False, f"Unreasonable value: {lux} lux")
        except Exception as e:
            printTest("readLight", False, str(e))

        # Test multiple readings for consistency
        try:
            readings = [sensor.readLight() for _ in range(3)]
            avg = sum(readings) / len(readings)
            printTest("Multiple readings", True, f"Avg: {avg:.2f} lux")
        except Exception as e:
            printTest("Multiple readings", False, str(e))

    except Exception as e:
        printTest("LightSensor initialization", False, str(e))


def testUltrasonicSensor() -> None:
    """Test UltrasonicSensor component."""
    printHeader("Testing UltrasonicSensor")

    try:
        from JoyPiNoteBetterLib import UltrasonicSensor

        # Test instantiation
        sensor = UltrasonicSensor(triggerPin=16, echoPin=26)
        printTest("UltrasonicSensor instantiation", True)

        # Test getDistance
        try:
            distance = sensor.getDistance()
            if distance == -1.0:
                printTest("getDistance", True, "Timeout (no object detected)")
            elif 2 <= distance <= 400:  # Valid range for HC-SR04 (2-400cm)
                printTest("getDistance", True, f"Value: {distance:.2f} cm")
            else:
                printTest("getDistance", False, f"Unreasonable value: {distance} cm")
        except Exception as e:
            printTest("getDistance", False, str(e))

        # Test sendTriggerPulse
        try:
            sensor.sendTriggerPulse()
            printTest("sendTriggerPulse", True)
        except Exception as e:
            printTest("sendTriggerPulse", False, str(e))

        # Test multiple distance readings
        try:
            distances = []
            for _ in range(3):
                d = sensor.getDistance()
                if d != -1.0:
                    distances.append(d)
                time.sleep(0.1)
            if distances:
                avg = sum(distances) / len(distances)
                printTest(
                    "Multiple readings",
                    True,
                    f"Avg: {avg:.2f} cm ({len(distances)}/3 valid)",
                )
            else:
                printSkip("Multiple readings", "All readings timed out")
        except Exception as e:
            printTest("Multiple readings", False, str(e))

    except Exception as e:
        printTest("UltrasonicSensor initialization", False, str(e))


def testNfcReader() -> None:
    """Test NfcReader component."""
    printHeader("Testing NfcReader")

    try:
        from JoyPiNoteBetterLib import NfcReader

        # Test instantiation
        reader = NfcReader()
        printTest("NfcReader instantiation", True)

        # Test read (non-blocking check)
        try:
            id, text = reader.read()
            if id is not None:
                printTest("read", True, f"ID: {id}, Text: '{text}'")
            else:
                printTest("read", True, "No tag present")
        except Exception as e:
            printTest("read", False, str(e))

        # Interactive test hint
        print("\n  ℹ Interactive test: Place an NFC tag within 3 seconds...")
        startTime = time.time()
        tagDetected = False
        while time.time() - startTime < 3:
            id, text = reader.read()
            if id is not None:
                tagDetected = True
                printTest("Interactive NFC detection", True, f"ID: {id}")
                break
            time.sleep(0.2)

        if not tagDetected:
            printSkip("Interactive NFC detection", "No tag detected (timeout)")

        # Note: waitForTag is blocking, so we skip it in automated tests
        printSkip("waitForTag", "Blocking method - skipped in automated test")
        printSkip("write", "Requires tag presence - skipped in automated test")

    except Exception as e:
        printTest("NfcReader initialization", False, str(e))


def testPwmBuzzer() -> None:
    """Test PwmBuzzer component.

    Note: Uses pin 12 instead of 18 to avoid conflicts with regular Buzzer test.
    When running 'all' tests, the regular Buzzer already uses pin 18.
    """

    printHeader("Testing PwmBuzzer")

    if not doSoundTest:
        printSkip("PwmBuzzer tests", "Sound tests disabled")
        return

    try:
        import RPi.GPIO as GPIO

        from JoyPiNoteBetterLib import PwmBuzzer

        # Clean up pin 12 first to avoid "different mode" error
        try:
            GPIO.cleanup(12)
        except Exception:
            pass

        # Use pin 12 (alternative PWM pin) to avoid conflict with regular Buzzer on pin 18
        # In production, both use pin 18, but for testing we need different pins
        buzzer = PwmBuzzer(pin=12, frequency=1000)
        printTest("PwmBuzzer instantiation", True)

        # Test setFrequency
        try:
            buzzer.setFrequency(440)  # A4 note
            printTest("setFrequency", True)
        except Exception as e:
            printTest("setFrequency", False, str(e))

        # Test setDutyCycle
        try:
            buzzer.setDutyCycle(50)
            printTest("setDutyCycle", True)
        except Exception as e:
            printTest("setDutyCycle", False, str(e))

        # Test buzz
        try:
            buzzer.buzz(duty_cycle=50)
            time.sleep(0.1)
            buzzer.stop()
            printTest("buzz", True)
        except Exception as e:
            printTest("buzz", False, str(e))

        # Test stop
        try:
            buzzer.stop()
            printTest("stop", True)
        except Exception as e:
            printTest("stop", False, str(e))

    except Exception as e:
        printTest("PwmBuzzer initialization", False, str(e))


def testPwmVibrator() -> None:
    """Test PwmVibrator component.

    Note: Uses pin 13 instead of 27 to avoid conflicts with regular Vibrator test.
    When running 'all' tests, the regular Vibrator already uses pin 27.
    """

    printHeader("Testing PwmVibrator")

    if not doSoundTest:
        printSkip("PwmVibrator tests", "Sound tests disabled")
        return

    try:
        import RPi.GPIO as GPIO

        from JoyPiNoteBetterLib import PwmVibrator

        # Clean up pin 13 first to avoid "different mode" error
        try:
            GPIO.cleanup(13)
        except Exception:
            pass

        # Use pin 13 to avoid conflict with regular Vibrator on pin 27
        vibrator = PwmVibrator(pin=13, frequency=100)
        printTest("PwmVibrator instantiation", True)

        # Test setIntensity
        try:
            vibrator.setIntensity(50)
            time.sleep(0.1)
            vibrator.setIntensity(0)
            printTest("setIntensity", True)
        except Exception as e:
            printTest("setIntensity", False, str(e))

        # Test stop
        try:
            vibrator.stop()
            printTest("stop", True)
        except Exception as e:
            printTest("stop", False, str(e))

    except Exception as e:
        printTest("PwmVibrator initialization", False, str(e))


def testServo() -> None:
    """Test Servo component."""
    printHeader("Testing Servo")

    try:
        from JoyPiNoteBetterLib import Servomotor

        # Test instantiation with start direction
        servo = Servomotor(startDirection=90, pin=19)
        printTest("Servo instantiation", True)

        # Test getDirection
        try:
            direction = servo.getDirection()
            printTest("getDirection", True, f"Current angle: {direction}°")
        except Exception as e:
            printTest("getDirection", False, str(e))

        # Test setDirection (move slowly)
        try:
            servo.setDirection(45, speed=5)
            time.sleep(0.2)
            printTest("setDirection (to 45°)", True)
        except Exception as e:
            printTest("setDirection (to 45°)", False, str(e))

        # Test setDirection (move back)
        try:
            servo.setDirection(90, speed=5)
            time.sleep(0.2)
            printTest("setDirection (back to 90°)", True)
        except Exception as e:
            printTest("setDirection (back to 90°)", False, str(e))

        # Test setDirection with instant move (speed=0)
        try:
            servo.setDirection(120, speed=0)
            time.sleep(0.2)
            servo.setDirection(90, speed=0)
            printTest("setDirection (instant)", True)
        except Exception as e:
            printTest("setDirection (instant)", False, str(e))

        # Verify final position
        try:
            finalDir = servo.getDirection()
            if finalDir == 90:
                printTest("Final position verification", True, f"Angle: {finalDir}°")
            else:
                printTest(
                    "Final position verification",
                    False,
                    f"Expected 90°, got {finalDir}°",
                )
        except Exception as e:
            printTest("Final position verification", False, str(e))

    except Exception as e:
        printTest("Servo initialization", False, str(e))


def testStepmotor() -> None:
    """Test Stepmotor component."""
    printHeader("Testing Stepmotor")

    try:
        from JoyPiNoteBetterLib import Stepmotor

        # Test instantiation
        motor = Stepmotor(pinA=5, pinB=6, pinC=13, pinD=25)
        printTest("Stepmotor instantiation", True)

        # Test setSpeed
        try:
            motor.setSpeed(50)  # Medium speed
            printTest("setSpeed(50)", True)
        except Exception as e:
            printTest("setSpeed(50)", False, str(e))

        # Test setSpeed validation (min/max)
        try:
            motor.setSpeed(1)  # Slowest
            motor.setSpeed(100)  # Fastest
            motor.setSpeed(50)  # Back to medium
            printTest("setSpeed validation", True)
        except Exception as e:
            printTest("setSpeed validation", False, str(e))

        # Test turnSteps (small movement)
        try:
            motor.turnSteps(10)  # Small forward rotation
            printTest("turnSteps (forward)", True)
        except Exception as e:
            printTest("turnSteps (forward)", False, str(e))

        # Test turnSteps reverse
        try:
            motor.turnSteps(-10)  # Small reverse rotation
            printTest("turnSteps (reverse)", True)
        except Exception as e:
            printTest("turnSteps (reverse)", False, str(e))

        # Test turnDegrees (small angle)
        try:
            motor.turnDegrees(15)  # Small angle forward
            printTest("turnDegrees (forward)", True)
        except Exception as e:
            printTest("turnDegrees (forward)", False, str(e))

        # Test turnDegrees reverse
        try:
            motor.turnDegrees(-15)  # Small angle reverse
            printTest("turnDegrees (reverse)", True)
        except Exception as e:
            printTest("turnDegrees (reverse)", False, str(e))

        # Test turnDistance (simulated with small radius)
        try:
            motor.turnDistance(5, radius=10)  # Small distance
            printTest("turnDistance (forward)", True)
        except Exception as e:
            printTest("turnDistance (forward)", False, str(e))

        # Test turnDistance reverse
        try:
            motor.turnDistance(-5, radius=10)  # Small distance reverse
            printTest("turnDistance (reverse)", True)
        except Exception as e:
            printTest("turnDistance (reverse)", False, str(e))

    except Exception as e:
        printTest("Stepmotor initialization", False, str(e))


def testClearFunctions() -> None:
    """Test ModuleReset utility class."""
    printHeader("Testing ModuleReset")

    try:
        from JoyPiNoteBetterLib import ModuleReset

        # Test clearLedMatrix
        try:
            ModuleReset.clearLedMatrix()
            printTest("ModuleReset.clearLedMatrix", True)
        except Exception as e:
            printTest("ModuleReset.clearLedMatrix", False, str(e))

        # Test clearLcdDisplay
        try:
            ModuleReset.clearLcdDisplay()
            printTest("ModuleReset.clearLcdDisplay", True)
        except Exception as e:
            printTest("ModuleReset.clearLcdDisplay", False, str(e))

        # Test clearSeg7x4
        try:
            ModuleReset.clearSeg7x4()
            printTest("ModuleReset.clearSeg7x4", True)
        except Exception as e:
            printTest("ModuleReset.clearSeg7x4", False, str(e))

        # Test clearAll
        try:
            ModuleReset.clearAll()
            printTest("ModuleReset.clearAll", True)
        except Exception as e:
            printTest("ModuleReset.clearAll", False, str(e))

        # Test muteBuzzer
        try:
            ModuleReset.muteBuzzer()
            printTest("ModuleReset.muteBuzzer", True)
        except Exception as e:
            printTest("ModuleReset.muteBuzzer", False, str(e))

        # Test muteVibrator
        try:
            ModuleReset.muteVibrator()
            printTest("ModuleReset.muteVibrator", True)
        except Exception as e:
            printTest("ModuleReset.muteVibrator", False, str(e))

        # Test muteAll
        try:
            ModuleReset.muteAll()
            printTest("ModuleReset.muteAll", True)
        except Exception as e:
            printTest("ModuleReset.muteAll", False, str(e))

    except Exception as e:
        printTest("ModuleReset import", False, str(e))


def printSummary() -> None:
    """Print test summary."""
    total = _testResults["passed"] + _testResults["failed"] + _testResults["skipped"]

    print(f"\n{'=' * 50}")
    print("  TEST SUMMARY")
    print(f"{'=' * 50}")
    print(f"  Total:   {total}")
    print(f"  Passed:  {_testResults['passed']} ✓")
    print(f"  Failed:  {_testResults['failed']} ✗")
    print(f"  Skipped: {_testResults['skipped']} ⊘")
    print(f"{'=' * 50}")

    if _testResults["failed"] == 0:
        print("  ✓ All tests passed!")
    else:
        print(f"  ✗ {_testResults['failed']} test(s) failed")
    print()


def main() -> int:
    """Main test runner."""
    print("\n" + "=" * 50)
    print("  JoyPiNoteBetterLib Test Suite")
    print("=" * 50)

    # Parse command line arguments
    component = "all"
    if len(sys.argv) > 1:
        component = sys.argv[1].lower()

    validComponents = [
        "all",
        "led",
        "lcd",
        "seg7",
        "button",
        "joystick",
        "touch",
        "tilt",
        "buzzer",
        "pwmbuzzer",
        "vibrator",
        "pwmvibrator",
        "humtemp",
        "sound",
        "light",
        "ultrasonic",
        "nfc",
        "servo",
        "stepmotor",
        "clear",
        "shared",
        "imports",
    ]

    if component not in validComponents:
        print(f"\nUnknown component: {component}")
        print(f"Valid options: {', '.join(validComponents)}")
        return 1

    # Run tests
    if component in ("all", "imports"):
        if not testImports():
            if component == "all":
                print("\n⚠ Import errors detected. Some tests may fail.")

    if component in ("all", "shared"):
        testSharedResources()

    if component in ("all", "led"):
        testLedMatrix()

    if component in ("all", "lcd"):
        testLcdDisplay()

    if component in ("all", "seg7"):
        testSeg7x4()

    if component in ("all", "button"):
        testButtonMatrix()

    if component in ("all", "joystick"):
        testJoystick()

    if component in ("all", "touch"):
        testTouch()

    if component in ("all", "tilt"):
        testTilt()

    if component in ("all", "buzzer"):
        testBuzzer()

    if component in ("all", "vibrator"):
        testVibrator()

    if component in ("all", "humtemp"):
        testHumidityTemperatureSensor()

    if component in ("all", "sound"):
        testSoundSensor()

    if component in ("all", "light"):
        testLightSensor()

    if component in ("all", "ultrasonic"):
        testUltrasonicSensor()

    if component in ("all", "pwmbuzzer"):
        testPwmBuzzer()

    if component in ("all", "pwmvibrator"):
        testPwmVibrator()

    if component in ("all", "servo"):
        testServo()

    if component in ("all", "stepmotor"):
        testStepmotor()

    # NFC test last - SimpleMFRC522 can interfere with GPIO state
    if component in ("all", "nfc"):
        testNfcReader()

    if component in ("all", "clear"):
        testClearFunctions()

    # Print summary
    printSummary()

    return 0 if _testResults["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
