import time

from JoyPiNoteBetterLib import LcdDisplay, TouchSensor

lcd = LcdDisplay()
touch = TouchSensor()

lcd.setBacklight(True)
lcd.clear()
lcd.wordWrap = True

text = ""

try:
    print(
        "Press the touch sensor to input Morse code.\n- short press = '.'\n- long press = '-'\nlonger > 1s = reset"
    )
    lcd.displayMessage("Morse Code Input\nPress the touch sensor")

    while True:
        if touch.isTouched():
            startTime = time.time() * 1000

            elapsed = 0

            # wait for release or timeout
            while touch.isTouched():
                elapsed = (time.time() * 1000) - startTime

                if elapsed >= 1000:
                    break

                time.sleep(0.02)

            if elapsed < 200:
                text += "."
            elif elapsed < 1000:
                text += "-"
            else:
                text = ""  # reset on long press

            lcd.displayMessage(text)

            # ensure touch is released
            while touch.isTouched():
                time.sleep(0.01)

        time.sleep(0.1)
except KeyboardInterrupt:
    lcd.clear()
    lcd.setBacklight(False)
    print(" Exiting...")
