import atexit
import threading
import time
from typing import Tuple

from JoyPiNoteBetterLib import (
    ButtonMatrix,
    Direction,
    Joystick,
    LcdDisplay,
    LedMatrix,
    ScrollingLinesLcd,
    Seg7x4,
    TouchSensor,
    UltrasonicSensor,
)

RgbaColor = Tuple[int, int, int, int]

led = LedMatrix(30)
seg = Seg7x4()
lcd = LcdDisplay()
scrLines = ScrollingLinesLcd(lcd)
touch = TouchSensor()
joystick = Joystick()
btns = ButtonMatrix()
ultSens = UltrasonicSensor()

led.clear()
seg.clear()
lcd.setBacklight(True)
lcd.clear()

colorList: list[RgbaColor] = [
    (255, 255, 255, 255),  # White
    (0, 0, 0, 0),  # Transparent
    (255, 0, 0, 255),  # Red
    (0, 255, 0, 255),  # Green
    (0, 0, 255, 255),  # Blue
    (255, 255, 0, 255),  # Yellow
    (0, 255, 255, 255),  # Cyan
    (255, 0, 255, 255),  # Magenta
    (255, 165, 0, 255),  # Orange
    (128, 0, 128, 255),  # Purple
    (255, 192, 203, 255),  # Pink
    (165, 42, 42, 255),  # Brown
    (128, 128, 128, 255),  # Gray
    (173, 216, 230, 255),  # Light Blue
    (34, 139, 34, 255),  # Dark Green
    (80, 224, 220, 255),  # Turquoise
]


pixelList: list[list[RgbaColor]] = []
cursorPos = (0, 0)
activeColor: RgbaColor = colorList[0]  # RGBA
bgColor: RgbaColor = (180, 255, 200, 25)  # RGBA
cursorBlinkState = False
isBgColorMode = False


updateThread: threading.Thread | None = None
controlThread: threading.Thread | None = None
brightnessThread: threading.Thread | None = None
threadEvent = threading.Event()


def clearPixellist() -> None:
    global pixelList
    pixelList = []
    for y in range(8):
        row: list[RgbaColor] = []
        for x in range(8):
            row.append((0, 0, 0, 0))
        pixelList.append(row)


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


def drawCanvas(update: bool = True) -> None:
    global pixelList, cursorPos, bgColor

    if isBgColorMode and cursorBlinkState:
        led.setAll(rgbaToRgb((180, 240, 200, 40)))
    else:
        led.setAll(rgbaToRgb(bgColor))

    for y in range(len(pixelList)):
        for x in range(len(pixelList[y])):
            if pixelList[y][x] != (0, 0, 0, 0):
                led.setPixel(x + (y * 8), rgbaToRgb(pixelList[y][x]))

    if update:
        led.update()


def handleMove() -> None:
    global cursorPos

    direction = joystick.getDirection()
    newX, newY = cursorPos
    if direction == Direction.N:
        newY -= 1
    elif direction == Direction.S:
        newY += 1
    elif direction == Direction.W:
        newX -= 1
    elif direction == Direction.E:
        newX += 1

    if 0 <= newX < 8 and 0 <= newY < 8:
        cursorPos = (newX, newY)


def handleColorselect() -> None:
    global activeColor, colorList, isBgColorMode, bgColor

    btnPressed = btns.getPressedKey()
    if btnPressed is not None and btnPressed < len(colorList):
        if isBgColorMode:
            bgColor = colorList[btnPressed]
        else:
            activeColor = colorList[btnPressed]


def getBightnessFromUltrasonic() -> int:
    distance = ultSens.getDistance()
    if distance is None:
        return 255
    if distance > 40:
        return 255
    if distance < 2:
        return 0
    brightness = int((distance - 2) / (40 - 2) * 255)
    return brightness


def handleTouch() -> None:
    global pixelList, cursorPos, activeColor, isBgColorMode

    if not touch.isTouched():
        return

    sT = time.time()
    el = 0

    # wait until touch is released
    while touch.isTouched():
        el = (time.time() - sT) * 1000

        if el >= 700:
            break

        time.sleep(0.1)

    doDefText = False
    if el < 700 and not isBgColorMode:
        setPixel(cursorPos[0], cursorPos[1], activeColor)
    else:
        doDefText = isBgColorMode
        isBgColorMode = not isBgColorMode

    if isBgColorMode or doDefText:
        scrLines.stop()
        text = "BG color mode"
        if doDefText:
            text = "Draw mode"
        lcd.displayMessage(f"{text}          \n(Release Touch)     ")

    while touch.isTouched():
        time.sleep(0.1)

    if isBgColorMode:
        scrLines.show(
            [
                "Touch to set &",
                "Button press to",
                "Ultrason. dist.",
            ],
            0,
        )
        scrLines.show(["exit mode", "select color", "for brightness"], 1, 2)
    elif doDefText:
        defaultInfoText()


def drawCursor(update: bool = False) -> None:
    global cursorPos, activeColor, cursorBlinkState, pixelList

    if cursorBlinkState:
        led.setPixel(
            cursorPos[0] + (cursorPos[1] * 8),
            rgbaToRgb(activeColor),
        )
    else:
        col = mixColors(
            pixelList[cursorPos[1]][cursorPos[0]], reduceAlpha(activeColor, 100)
        )
        led.setPixel(
            cursorPos[0] + (cursorPos[1] * 8),
            rgbaToRgb(col),
        )

    if update:
        led.update()


def setPixel(x: int, y: int, color: RgbaColor) -> None:
    global pixelList
    pixelList[y][x] = color


def controlLoop() -> None:
    global controlThread, threadEvent, cursorBlinkState

    while not threadEvent.is_set():
        handleMove()
        handleColorselect()
        handleTouch()

        for _ in range(2):
            if threadEvent.is_set():
                break
            time.sleep(0.1)


def brightnessLoop() -> None:
    global brightnessThread, threadEvent, bgColor, activeColor, isBgColorMode

    while not threadEvent.is_set():

        brightness = getBightnessFromUltrasonic()
        if isBgColorMode:
            bgColor = (bgColor[0], bgColor[1], bgColor[2], brightness)
        else:
            activeColor = (
                activeColor[0],
                activeColor[1],
                activeColor[2],
                brightness,
            )

        seg.setFull(brightness)

        for _ in range(7):
            if threadEvent.is_set():
                break
            time.sleep(0.1)

def updateLoop() -> None:
    global updateThread, threadEvent, cursorBlinkState

    while not threadEvent.is_set():
        drawCanvas(False)
        if not isBgColorMode:
            drawCursor(False)
        led.update()

        cursorBlinkState = not cursorBlinkState

        for _ in range(2):
            if threadEvent.is_set():
                break
            time.sleep(0.1)


def exitHandler() -> None:
    global updateThread, threadEvent
    threadEvent.set()

    if updateThread is not None:
        updateThread.join(0.1)

    if controlThread is not None:
        controlThread.join(0.1)

    if brightnessThread is not None:
        brightnessThread.join(0.1)

    led.clear()
    lcd.clear()
    lcd.setBacklight(False)
    seg.clear()


def defaultInfoText() -> None:
    scrLines.stop()
    scrLines.show(
        [
            "Joystick to move",
            "Buttons to",
            "Short press",
            "Long press touch",
            "Ultrason. dist.",
        ],
        0,
    )
    scrLines.show(
        ["", "select color", "touch to draw", "to change BG", "for brightness"], 1, 2
    )


try:
    atexit.register(exitHandler)

    print(
        "- Joystick to move cursor"
        + "\n- Buttons to select color"
        + "\n- Touch to draw"
        + "\n- Long press touch to change BG color"
        + "\n- Ultrasonic sensor to adjust brightness"
    )

    defaultInfoText()

    clearPixellist()

    updateThread = threading.Thread(target=updateLoop)
    updateThread.start()
    controlThread = threading.Thread(target=controlLoop)
    controlThread.start()
    brightnessThread = threading.Thread(target=brightnessLoop)
    brightnessThread.start()

    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(" Exiting...")
    exitHandler()
