import atexit
import random
import threading
import time
from typing import Tuple

from JoyPiNoteBetterLib import (
    LedMatrix,
    TouchSensor,
)

RgbaColor = Tuple[int, int, int, int]

led = LedMatrix(30)
touch = TouchSensor()


def randomColor(minBrightness: int = 0) -> RgbaColor:
    r, g, b = 0, 0, 0

    while (r + g + b) // 3 < minBrightness:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

    return (r, g, b, 255)


matrixSize = (8, 8)
fieldColors: list[list[RgbaColor]] = [
    [randomColor(80) for _ in range(matrixSize[0])] for _ in range(matrixSize[1])
]
snakeList: list[Tuple[float, float]] = []
snakeBrightness: list[float] = []  # Brightness for each point (0-255)
snakeVelocities: list[Tuple[float, float]] = []
position: list[float] = [0.0, 0.0]
velocity: list[float] = [random.uniform(-0.80, 1.0), random.uniform(-0.73, 0.52)]
snakeColor: RgbaColor = randomColor(150)
useFieldColors = False

updateThread: threading.Thread | None = None
controlThread: threading.Thread | None = None
threadEvent = threading.Event()


def mixColors(base: RgbaColor, overlay: RgbaColor) -> RgbaColor:
    inv_alpha = 255 - overlay[3]
    r = (base[0] * inv_alpha + overlay[0] * overlay[3]) // 255
    g = (base[1] * inv_alpha + overlay[1] * overlay[3]) // 255
    b = (base[2] * inv_alpha + overlay[2] * overlay[3]) // 255
    a = max(base[3], overlay[3])
    return (r, g, b, a)


def rgbaToRgb(color: RgbaColor) -> Tuple[int, int, int]:
    if color[3] == 0:
        return (0, 0, 0)
    r = color[0] * color[3] // 255
    g = color[1] * color[3] // 255
    b = color[2] * color[3] // 255
    return (r, g, b)


def reduceAlpha(color: RgbaColor, amount: int) -> RgbaColor:
    new_alpha = max(0, color[3] - amount)
    return (color[0], color[1], color[2], new_alpha)


def addSnakePoint(count: int = 1) -> None:
    global snakeList, snakeBrightness
    for _ in range(count):
        snakeList.append((position[0], position[1]))
        snakeBrightness.append(0.0)  # Starts at 0 brightness


def removeSnakePoint(count: int = 1) -> None:
    global snakeList, snakeBrightness
    for _ in range(count):
        if len(snakeList) > 0:
            snakeList.pop()
            snakeBrightness.pop()


def startAnimation() -> None:
    global \
        updateThread, \
        threadEvent, \
        position, \
        velocity, \
        snakeList, \
        snakeColor, \
        snakeBrightness

    if updateThread is not None and updateThread.is_alive():
        return

    # Initialize starting position
    position[0] = random.uniform(0, matrixSize[0] - 1)
    position[1] = random.uniform(0, matrixSize[1] - 1)
    snakeList = [(position[0], position[1])]
    snakeBrightness = [255.0]
    snakeColor = randomColor(150)

    def runAnimation() -> None:
        global \
            position, \
            velocity, \
            snakeList, \
            snakeColor, \
            snakeBrightness, \
            useFieldColors

        while not threadEvent.is_set():
            oldPositions = snakeList.copy()

            # Update head position (DVD logo movement)
            position[0] += velocity[0]
            position[1] += velocity[1]

            # Bounce at the edges
            bounced = False
            if position[0] <= 0 or position[0] >= matrixSize[0] - 1:
                velocity[0] = -velocity[0]
                position[0] = max(0, min(matrixSize[0] - 1, position[0]))
                bounced = True
            if position[1] <= 0 or position[1] >= matrixSize[1] - 1:
                velocity[1] = -velocity[1]
                position[1] = max(0, min(matrixSize[1] - 1, position[1]))
                bounced = True

            # On bounce: change color
            if bounced:
                snakeColor = randomColor(150)

            # Update snake list: set head
            if len(snakeList) > 0:
                snakeList[0] = (position[0], position[1])

            # Remaining points take the position of the predecessor
            for i in range(1, len(snakeList)):
                snakeList[i] = oldPositions[i - 1]

            # Update brightness: fade in and fade out
            snakeLen = len(snakeList)
            for i in range(snakeLen):
                # Target brightness based on position in the snake
                # Head = bright (255), tail = dark (approx. 50)
                if snakeLen == 1:
                    targetBrightness = 255.0
                else:
                    targetBrightness = 255.0 - (i / (snakeLen - 1)) * 205.0

                # Smoothly fade to target brightness (only increase, not decrease)
                # This way new points fade in slowly
                if snakeBrightness[i] < targetBrightness:
                    snakeBrightness[i] = min(
                        targetBrightness, snakeBrightness[i] + 9999
                    )

            # Draw LED matrix
            led.clear()

            # Draw all snake points (from back to front)
            for idx in range(len(snakeList) - 1, -1, -1):
                px, py = snakeList[idx]
                # Brightness from the array
                brightness = int(snakeBrightness[idx])
                color = (
                    snakeColor[0] * brightness // 255,
                    snakeColor[1] * brightness // 255,
                    snakeColor[2] * brightness // 255,
                )
                pixelIndex = int(round(px)) + (int(round(py)) * 8)
                if 0 <= pixelIndex < 64:
                    if useFieldColors:
                        fieldColor = fieldColors[int(round(py))][int(round(px))]
                        fieldColor = (
                            fieldColor[0] * brightness // 255,
                            fieldColor[1] * brightness // 255,
                            fieldColor[2] * brightness // 255,
                        )
                        led.setPixel(pixelIndex, fieldColor)
                    else:
                        led.setPixel(pixelIndex, color)

            led.update()
            time.sleep(0.06)

    def runControl() -> None:
        global threadEvent, useFieldColors

        while not threadEvent.is_set():
            if not touch.isTouched():
                time.sleep(0.1)
                continue

            sT = time.time()
            el = 0

            # wait until touch is released
            while touch.isTouched():
                el = (time.time() - sT) * 1000

                if el >= 700:
                    break

                time.sleep(0.01)

            if el >= 700:
                # Long press: randomize velocity
                velocity[0] = random.uniform(-0.80, 1.0)
                velocity[1] = random.uniform(-0.73, 0.52)
            else:
                # Short press: toggle useFieldColors
                useFieldColors = not useFieldColors

            # Don't proceed until touch is released
            while touch.isTouched():
                time.sleep(0.1)

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

    print(
        "Short press touch: color mode toggle"
        + "\nLong press touch: randomize velocity"
    )

    try:
        startAnimation()
        addSnakePoint(6)

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(" Exiting....")
        exitHandler()
