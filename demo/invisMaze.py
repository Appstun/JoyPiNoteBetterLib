import atexit
import random
import threading
import time

from JoyPiNoteBetterLib import (
    ButtonMatrix,
    Direction,
    Joystick,
    LcdDisplay,
    LedMatrix,
    ScrollingLinesLcd,
    Seg7x4,
    TouchSensor,
    Vibrator,
)

led = LedMatrix(30)
led.clear()
joystick = Joystick()
seg = Seg7x4()
seg.clear()
touch = TouchSensor()
lcd = LcdDisplay()
lcd.setBacklight(True)
lcd.clear()
scrLines = ScrollingLinesLcd(lcd)
vib = Vibrator()
btns = ButtonMatrix()

MAZE_WIDTH = 8
MAZE_HEIGHT = 8
WALL_DISAPPEAR_DELAY = 15
WALL_MAX_BRIGHTNESS = 150
PLAYER_COLORS = [(0, 200, 0), (200, 100, 0), (150, 0, 100), (100, 100, 200)]

maze: list[list[None | int]] = []
pos = {"start": (0, 0), "end": (0, 0)}
lvl = 0
playerPos = (0, 0)
playerPath: list[tuple[int, int]] = []
playerMoveCount = 0
wallHits = 0
lcdInfoThread: threading.Thread | None = None
lcdInfoStopEvent: threading.Event | None = None
wallDelay = WALL_DISAPPEAR_DELAY


def generateMaze(
    start: tuple[int, int], end: tuple[int, int]
) -> list[list[None | int]]:
    # 0 = Wall, None = Path
    # Start with everything FREE - then add walls
    gen: list[list[None | int]] = [
        [None for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)
    ]

    wallDensity = 0.2 + (lvl * 0.10)

    # 1. Teile das Grid in 4 Quadranten und platziere Wände gleichmäßig
    quadrants = [
        (0, 0, MAZE_WIDTH // 2, MAZE_HEIGHT // 2),  # oben links
        (MAZE_WIDTH // 2, 0, MAZE_WIDTH, MAZE_HEIGHT // 2),  # oben rechts
        (0, MAZE_HEIGHT // 2, MAZE_WIDTH // 2, MAZE_HEIGHT),  # unten links
        (MAZE_WIDTH // 2, MAZE_HEIGHT // 2, MAZE_WIDTH, MAZE_HEIGHT),  # unten rechts
    ]

    for qx1, qy1, qx2, qy2 in quadrants:
        # Mindestens 2-3 Wände pro Quadrant
        wallsInQuadrant = 0
        targetWalls = random.randint(2, 4) + lvl
        attempts = 0

        while wallsInQuadrant < targetWalls and attempts < 30:
            x = random.randint(qx1, qx2 - 1)
            y = random.randint(qy1, qy2 - 1)

            if (x, y) != start and (x, y) != end and gen[y][x] is None:
                gen[y][x] = 0
                wallsInQuadrant += 1
            attempts += 1

    # 2. Diagonale Wandlinien (kurz, 2-3 Felder)
    numDiagonals = 2 + lvl
    for _ in range(numDiagonals):
        diagStartX = random.randint(1, MAZE_WIDTH - 2)
        diagStartY = random.randint(1, MAZE_HEIGHT - 2)
        diagDir = random.choice([(1, 1), (1, -1), (-1, 1), (-1, -1)])
        diagLen = random.randint(2, 3)

        for i in range(diagLen):
            dx = diagStartX + diagDir[0] * i
            dy = diagStartY + diagDir[1] * i
            if 0 <= dx < MAZE_WIDTH and 0 <= dy < MAZE_HEIGHT:
                if (dx, dy) != start and (dx, dy) != end:
                    gen[dy][dx] = 0

    # 3. Isolierte Einzelwände verteilt über das ganze Feld
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if (x, y) != start and (x, y) != end and gen[y][x] is None:
                # Prüfe ob Nachbarn frei sind (für isolierte Wand)
                neighbors = [
                    (x + dx, y + dy)
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    if 0 <= x + dx < MAZE_WIDTH and 0 <= y + dy < MAZE_HEIGHT
                ]
                wallNeighbors = sum(1 for nx, ny in neighbors if gen[ny][nx] == 0)

                # Isolierte Wände haben höhere Chance
                if wallNeighbors == 0 and random.random() < wallDensity * 0.4:
                    gen[y][x] = 0

    # 4. Prüfe jeden 2x2 Bereich - füge Wand hinzu wenn komplett frei
    for y in range(MAZE_HEIGHT - 1):
        for x in range(MAZE_WIDTH - 1):
            block = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
            allFree = all(gen[py][px] is None for px, py in block)
            if allFree:
                # Wähle zufällige Position im 2x2 Block
                wx, wy = random.choice(block)
                if (wx, wy) != start and (wx, wy) != end:
                    gen[wy][wx] = 0

    # Solvability check
    def isSolvable() -> bool:
        visited = set()
        stack = [start]

        while stack:
            current = stack.pop()
            if current == end:
                return True
            if current in visited:
                continue
            visited.add(current)

            x, y = current
            neighbors = [
                (x + dx, y + dy)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= x + dx < MAZE_WIDTH and 0 <= y + dy < MAZE_HEIGHT
            ]
            for neighbor in neighbors:
                nx, ny = neighbor
                if gen[ny][nx] is None and neighbor not in visited:
                    stack.append(neighbor)

        return False

    while not isSolvable():
        # Entferne zufällige Wände bis lösbar
        wall_positions = [
            (x, y)
            for y in range(MAZE_HEIGHT)
            for x in range(MAZE_WIDTH)
            if gen[y][x] == 0
        ]
        if wall_positions:
            wx, wy = random.choice(wall_positions)
            gen[wy][wx] = None  # Wand entfernen

    return gen


def updateWalls():
    # update wall brightness
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            cell = maze[y][x]
            if cell is not None and cell > 0:
                maze[y][x] -= WALL_MAX_BRIGHTNESS // wallDelay  # type: ignore
    led.update()


def printMaze():
    for row in maze:
        print(
            " ".join(
                "." if cell is None else str(cell // 25)
                for cell in row  # type: ignore
            )
        )
    print()


def drawPlayer(oldPos: tuple[int, int] | None, newPos: tuple[int, int], doDim: bool):
    if oldPos is not None:
        led.setPixel(oldPos[0] + (oldPos[1] * 8), (0, 0, 0))
    
    col = PLAYER_COLORS[lvl % len(PLAYER_COLORS)]
    if doDim:
        led.setPixel( playerPos[0] + (playerPos[1] * 8),(col[0] // 3, col[1] // 3, col[2] // 3))
    else:  
        led.setPixel(newPos[0] + (newPos[1] * 8), col)
    led.update()


def drawField(
    overrideShowMaze: bool | None = None, showPlayer: bool = True, showEnd: bool = True
):
    # draw walls
    if overrideShowMaze is None or overrideShowMaze:
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                cell = maze[y][x]
                if cell is not None and (cell > 0 or overrideShowMaze):
                    led.setPixel(
                        x + (y * 8),
                        (WALL_MAX_BRIGHTNESS if overrideShowMaze else int(cell), 0, 0),
                    )
                else:
                    led.setPixel(x + (y * 8), (0, 0, 0))

    if showEnd:
        led.setPixel(pos["end"][0] + (pos["end"][1] * 8), (0, 0, 255))

    if showPlayer:
        drawPlayer(None, playerPos, False)
        # Updates already the matrix
    else:
        led.update()


def prepareGame():
    global maze, pos, playerPos, wallHits, wallDelay, lvl, playerMoveCount

    wallHits = 0
    if lvl == 0:
        wallDelay = 999
    else:
        wallDelay = (
            WALL_DISAPPEAR_DELAY
            if lvl < 3
            else WALL_DISAPPEAR_DELAY + (WALL_DISAPPEAR_DELAY * 0.6)
        )

    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    pos["start"] = random.choice(corners)
    opposite_corners = {
        (0, 0): (7, 7),
        (0, 7): (7, 0),
        (7, 0): (0, 7),
        (7, 7): (0, 0),
    }
    if random.random() < 0.7:
        pos["end"] = opposite_corners[pos["start"]]
    else:
        other_corners = [
            c
            for c in corners
            if c != pos["start"] and c != opposite_corners[pos["start"]]
        ]
        pos["end"] = random.choice(other_corners)

    playerPos = pos["start"]
    playerPath.clear()
    playerMoveCount = 0

    maze = generateMaze(pos["start"], pos["end"])


def lcdClear():
    lcd.clear()
    lcd.setBacklight(False)


def gameLoop():
    global playerPos, pos, wallHits, playerMoveCount

    def startLcdInfo():
        scrLines.show(["Joystick to move", "Touch to see"], 1, 2)

    # show maze briefly at start of lvl 0
    if lvl <= 1:
        lcd.displayMessage("The maze will be    \ninvisible soon     ")
        drawField(True, False, True)
        drawPlayer(None, playerPos, True)

        countdown = 1000
        if lvl == 0:
            countdown = 2400
        while countdown >= 0:
            seg.setFull(countdown)
            time.sleep(0.1)
            countdown -= 100

    drawField(None, True, True)
    lcd.displayMessage("Go to the blue!", 0)
    startLcdInfo()
    seg.setFull(wallHits)

    # main game loop until player reaches the end
    while playerPos != pos["end"]:
        direction = joystick.getDirection()

        # when touch, draw complete maze briefly
        if touch.isTouched():
            drawField(True, False, True)
            drawPlayer(None, playerPos, True)

            wallHits += 7
            seg.setFull(wallHits)

            scrLines.stop()
            lcd.displayMessage("Reveal the Maze!      \n(Game paused)      ")

            time.sleep(3)
            drawField(None, lvl < 3, True)
            startLcdInfo()

        # skip if no direction is pressed
        if direction == Direction.CENTER:
            continue

        # set new player position based on joystick direction
        newX, newY = playerPos
        if direction == Direction.N:
            newY -= 1
        elif direction == Direction.S:
            newY += 1
        elif direction == Direction.W:
            newX -= 1
        elif direction == Direction.E:
            newX += 1

        # check if new position is valid
        if 0 <= newX < MAZE_WIDTH and 0 <= newY < MAZE_HEIGHT:
            block = maze[newY][newX]

            # move player when path
            if block is None:
                playerPos = (newX, newY)
                if playerPos not in playerPath or playerPos != pos["end"]:
                    playerPath.append(playerPos)
                updateWalls()
                playerMoveCount += 1
            # hit wall & reset player to start
            elif block == 0:
                maze[newY][newX] = WALL_MAX_BRIGHTNESS
                playerPos = pos["start"]
                playerPath.clear()

                vib.vibrate(0.05)

                wallHits += 1
                seg.setFull(wallHits)
                playerMoveCount += 1
            drawField(None, lvl < 3, True)

        time.sleep(0.26)

    # game end logic

    seg.clear()
    scrLines.show(
        [
            f"You win! (Lvl {lvl + 1})",
            f"Walls hit: {wallHits}",
            f"Tiles moved: {playerMoveCount}",
        ],
        0,
    )

    # show complete maze with player, player's path & end
    drawField(True, False, False)
    for point in playerPath:
        led.setPixel(point[0] + (point[1] * 8), (25, 30, 25))
    led.setPixel(
        pos["start"][0] + (pos["start"][1] * 8), PLAYER_COLORS[lvl % len(PLAYER_COLORS)]
    )
    led.setPixel(pos["end"][0] + (pos["end"][1] * 8), (0, 0, WALL_MAX_BRIGHTNESS))
    led.update()


if __name__ == "__main__":
    print(
        "Look at the LCD display for instructions!"
        + "\n  - Touch sensor = start game & see maze walls"
        + "\n  - Button 16 (bottom right) in button matrix = change level/difficulty"
        + "\n  - Joystick = move player"
    )
    stopEvent = threading.Event()

    def progStartAnim(stopEvent: threading.Event):
        fileArea = [
            (2, 2),
            (2, 3),
            (3, 2),
            (3, 3),
            (4, 2),
            (4, 3),
            (5, 2),
            (5, 3),
            (2, 4),
            (2, 5),
            (3, 4),
            (3, 5),
            (4, 4),
            (4, 5),
            (5, 4),
            (5, 5),
        ]
        pathAnim = [
            (2, 2),
            (2, 3),
            (2, 2),
            (2, 2),
            (2, 3),
            (3, 3),
            (3, 4),
            (2, 2),
            (2, 3),
            (3, 3),
            (3, 4),
            (4, 4),
            (2, 2),
        ]
        wallAnim = [
            None,
            (2, 4),
            (3, 2),
            None,
            None,
            None,
            (3, 5),
            None,
            None,
            None,
            (5, 4),
            None,
        ]

        i = 0
        while not stopEvent.is_set():
            led.clear()
            for j in fileArea:
                led.setPixel(j[0] + (j[1] * 8), (20, 27, 20))

            for j in range(i):
                if wallAnim[j] is not None:
                    led.setPixel(
                        wallAnim[j][0] + (wallAnim[j][1] * 8),
                        (WALL_MAX_BRIGHTNESS, 0, 0),
                    )
            if pathAnim[i] is not None:
                led.setPixel(
                    pathAnim[i][0] + (pathAnim[i][1] * 8),
                    PLAYER_COLORS[lvl % len(PLAYER_COLORS)],
                )
            led.setPixel(5 + (5 * 8), (0, 0, WALL_MAX_BRIGHTNESS))
            led.update()

            i = (i + 1) % len(pathAnim)
            for _ in range(5):
                if stopEvent.is_set():
                    break
                time.sleep(0.1)

    def exitHandler():
        scrLines.stop()
        stopEvent.set()

        led.clear()
        seg.clear()
        lcdClear()

        vib.setVibrate(False)

    atexit.register(exitHandler)  # rehgister program exit event

    def menuWait(isProgStart: bool):
        global lvl, pos

        scrLines.show(
            [
                "Touch to start" if isProgStart else "Touch to restart",
                "Btn. 16 = LvlSel",
            ],
            1,
            1.2,
        )

        while not touch.isTouched():
            key = btns.getPressedKey()
            if key == 15:
                lvl += 1
                if lvl > (len(PLAYER_COLORS) - 1):
                    lvl = 0

                if not isProgStart:
                    led.setPixel(
                        pos["start"][0] + (pos["start"][1] * 8),
                        PLAYER_COLORS[lvl % len(PLAYER_COLORS)],
                    )
                    led.update()

                # wait for button release
                while btns.getPressedKey() == 15:
                    time.sleep(0.1)

            time.sleep(0.1)
        scrLines.stop()
        # wait for touch release
        while touch.isTouched():
            time.sleep(0.1)

    try:
        threading.Thread(
            target=progStartAnim, args=(stopEvent,), daemon=True
        ).start()  # show animation
        lcd.displayMessage("Invis. Maze Game      ", 0)
        menuWait(True)  # show menu
        stopEvent.set()  # stop animation

        while True:
            prepareGame()  # set game variables & generate new maze
            gameLoop()  # start game
            menuWait(False)  # show menu
    except KeyboardInterrupt:
        print(" Exiting...")
