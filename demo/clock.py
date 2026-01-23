import time

from JoyPiNoteBetterLib import Seg7x4

seg = Seg7x4()

print("Look at the 7x4 segment display for the current time.")

colOn = True
try:
    while True:
        curTime = time.strftime("%H%M")
        timeDigs = [int(d) for d in curTime]

        seg.set(0, timeDigs[0])
        seg.set(1, timeDigs[1])
        seg.set(2, timeDigs[2])
        seg.set(3, timeDigs[3])

        # Blink when on the hour
        if timeDigs[2] == 0 and timeDigs[3] == 0:
            seg.setBlinkRate(1)
        else:
            seg.setBlinkRate(0)

        hour = int(str(timeDigs[0]) + str(timeDigs[1]))
        # Dim the display at night
        if hour < 6 or hour >= 19:
            seg.setBrightness(0.05)
        else:
            seg.setBrightness(1.0)

        if colOn:
            seg.showColon()
        colOn = not colOn

        seg.update()
        time.sleep(0.5)
except KeyboardInterrupt:
    seg.clear()
    print(" Exiting...")
