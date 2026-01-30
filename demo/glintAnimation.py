import atexit
import random
import threading
import time
from typing import Tuple

from JoyPiNoteBetterLib import (
    LedMatrix,
    TouchSensor,
)

RgbColor = Tuple[int, int, int]

led = LedMatrix(30)
touch = TouchSensor()


def randomColor(minBrightness: int = 0) -> RgbColor:
    r, g, b = 0, 0, 0

    while (r + g + b) // 3 < minBrightness:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

    return (r, g, b)


colorMinBrightness = 120
matrixSize = (8, 8)
cellBrightness: list[list[int]] = [
    [random.randint(-255, 255) for _ in range(matrixSize[0])]
    for _ in range(matrixSize[1])
]
color: RgbColor = randomColor(colorMinBrightness)
globalBrightness: int = 255

updateThread: threading.Thread | None = None
controlThread: threading.Thread | None = None
threadEvent = threading.Event()


def startAnimation() -> None:
    global updateThread, threadEvent

    if updateThread is not None and updateThread.is_alive():
        return

    def runAnimation() -> None:
        global color, cellBrightness, threadEvent

        while not threadEvent.is_set():
            for y in range(matrixSize[1]):
                for x in range(matrixSize[0]):
                    brightness = cellBrightness[y][x] - 1
                    if brightness <= -255:
                        brightness = 255

                    if brightness == 0 and random.random() < 0.75:
                        brightness = 5

                    cellBrightness[y][x] = brightness

                    b = abs(brightness) * abs(globalBrightness) // 255

                    pixelColor = (0, 0, 0)
                    if b != 0:
                        pixelColor = (
                            color[0] * b // 255,
                            color[1] * b // 255,
                            color[2] * b // 255,
                        )
                    led.setPixel(x + (y * 8), pixelColor)

            led.update()
            time.sleep(0.01)

    def runControl() -> None:
        global color, threadEvent, globalBrightness

        while not threadEvent.is_set():
            if not touch.isTouched():
                time.sleep(0.1)
                continue

            lastB = globalBrightness
            while globalBrightness > -255:
                if threadEvent.is_set():
                    break

                if globalBrightness <= 0 and lastB > 0:
                    color = randomColor(colorMinBrightness)

                lastB = globalBrightness
                globalBrightness -= 20
                time.sleep(0.02)
            globalBrightness = 255

            # wait for release
            while touch.isTouched():
                time.sleep(0.1)

    threadEvent.clear()
    updateThread = threading.Thread(target=runAnimation)
    controlThread = threading.Thread(target=runControl)
    updateThread.start()
    controlThread.start()


def stopAnimation() -> None:
    global updateThread, threadEvent
    threadEvent.set()

    if updateThread is not None:
        updateThread.join(0.1)
    if controlThread is not None:
        controlThread.join(0.1)

    led.clear()


def exitHandler() -> None:
    stopAnimation()


if __name__ == "__main__":
    atexit.register(exitHandler)

    print("Short press touch: randomize color")

    try:
        startAnimation()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(" Exiting....")
        exitHandler()
