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
finishBrightness = 255


def generateMaze(
    start: tuple[int, int], end: tuple[int, int]
) -> list[list[None | int]]:
    gen: list[list[None | int]] = [
        [None for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)
    ]

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
            cx, cy = current
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT:
                    if gen[ny][nx] is None and (nx, ny) not in visited:
                        stack.append((nx, ny))
        return False

    def count_paths() -> int:
        """Count distinct paths from start to end"""
        from collections import deque

        queue = deque([(start, [start])])
        visited_states = {start: 1}
        paths_found = 0
        min_length = float("inf")

        while queue:
            current, path = queue.popleft()

            if len(path) > min_length + 3:
                continue

            if current == end:
                if len(path) <= min_length + 3:
                    paths_found += 1
                    min_length = min(min_length, len(path))
                continue

            cx, cy = current
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT:
                    if gen[ny][nx] is None and (nx, ny) not in path:
                        new_path = path + [(nx, ny)]
                        if (nx, ny) not in visited_states or visited_states[
                            (nx, ny)
                        ] < 3:
                            visited_states[(nx, ny)] = (
                                visited_states.get((nx, ny), 0) + 1
                            )
                            queue.append(((nx, ny), new_path))

        return min(paths_found, 5)

    def count_adjacent_walls(x: int, y: int) -> int:
        count = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT:
                if gen[ny][nx] == 0:
                    count += 1
        return count

    all_positions = [
        (x, y)
        for y in range(MAZE_HEIGHT)
        for x in range(MAZE_WIDTH)
        if (x, y) != start and (x, y) != end
    ]

    target_walls = random.randint(22, 28)
    walls_placed = 0

    # Komplett zufällige Wandplatzierung - keine Struktur-Regeln
    random.shuffle(all_positions)

    for x, y in all_positions:
        if walls_placed >= target_walls:
            break

        gen[y][x] = 0

        if not isSolvable():
            gen[y][x] = None
        else:
            walls_placed += 1

    # Phase 2: Sackgassen erzeugen - Wände die fast einschließen
    def count_free_neighbors(x: int, y: int) -> int:
        count = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT:
                if gen[ny][nx] is None:
                    count += 1
            else:
                count += 1  # Rand zählt als "frei" für Sackgassen
        return count

    # Finde Positionen für Sackgassen (Stellen mit nur 1 freien Nachbarn)
    empty_positions = [(x, y) for x, y in all_positions if gen[y][x] is None]
    random.shuffle(empty_positions)

    dead_ends_added = 0
    for x, y in empty_positions:
        if dead_ends_added >= random.randint(6, 12):
            break
        # Platziere Wand wenn es eine Sackgasse erzeugt
        if count_free_neighbors(x, y) == 2:  # Würde einen Engpass/Sackgasse erzeugen
            gen[y][x] = 0
            if not isSolvable():
                gen[y][x] = None
            else:
                dead_ends_added += 1

    # Phase 3: Zufällige Löcher in Wand-Clustern öffnen (verwirrt den Spieler)
    wall_positions = [(x, y) for x, y in all_positions if gen[y][x] == 0]
    random.shuffle(wall_positions)

    holes_opened = 0
    for x, y in wall_positions:
        if holes_opened >= random.randint(12, 18):
            break
        # Öffne Loch nur wenn es von mindestens 2 Wänden umgeben ist
        wall_neighbors = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT:
                if gen[ny][nx] == 0:
                    wall_neighbors += 1
        if wall_neighbors >= 2:
            gen[y][x] = None
            holes_opened += 1

    # Phase 3.5: Lange gerade Pfade unterbrechen
    def find_straight_path_length(x: int, y: int, dx: int, dy: int) -> int:
        """Zählt wie viele freie Felder in einer Richtung"""
        length = 0
        cx, cy = x, y
        while True:
            cx, cy = cx + dx, cy + dy
            if not (0 <= cx < MAZE_WIDTH and 0 <= cy < MAZE_HEIGHT):
                break
            if gen[cy][cx] is not None:
                break
            length += 1
        return length

    empty_positions = [(x, y) for x, y in all_positions if gen[y][x] is None]
    random.shuffle(empty_positions)

    blockers_added = 0
    for x, y in empty_positions:
        if blockers_added >= random.randint(3, 6):
            break
        # Prüfe ob Teil eines langen geraden Pfads (3+ in eine Richtung)
        h_length = find_straight_path_length(x, y, -1, 0) + find_straight_path_length(
            x, y, 1, 0
        )
        v_length = find_straight_path_length(x, y, 0, -1) + find_straight_path_length(
            x, y, 0, 1
        )

        if h_length >= 3 or v_length >= 3:
            gen[y][x] = 0
            if not isSolvable():
                gen[y][x] = None
            else:
                blockers_added += 1

    # Phase 4: Fülle große freie Flächen
    def has_large_empty_area(x: int, y: int) -> bool:
        """Prüft ob um (x,y) herum eine 2x2 oder größere freie Fläche ist"""
        for dy in range(-1, 1):
            for dx in range(-1, 1):
                all_empty = True
                for cy in range(2):
                    for cx in range(2):
                        nx, ny = x + dx + cx, y + dy + cy
                        if not (0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT):
                            all_empty = False
                            break
                        if gen[ny][nx] is not None:
                            all_empty = False
                            break
                    if not all_empty:
                        break
                if all_empty:
                    return True
        return False

    empty_positions = [(x, y) for x, y in all_positions if gen[y][x] is None]
    random.shuffle(empty_positions)

    for x, y in empty_positions:
        if has_large_empty_area(x, y):
            gen[y][x] = 0
            if not isSolvable():
                gen[y][x] = None

    return gen


def updateWalls():
    # update wall brightness
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            cell = maze[y][x]
            if cell is not None and cell > 0:
                maze[y][x] -= WALL_MAX_BRIGHTNESS // wallDelay  # type: ignore
    led.update()


def printMaze(points: list[tuple[int, int]] | None = None):
    for y, row in enumerate(maze):
        print(
            " ".join(
                "#"
                if points and (x, y) in points
                else ("." if cell is None else str(cell // 25))
                for x, cell in enumerate(row)  # type: ignore
            )
        )

    print()


def drawPlayer(oldPos: tuple[int, int] | None, newPos: tuple[int, int], doDim: bool):
    if oldPos is not None:
        led.setPixel(oldPos[0] + (oldPos[1] * 8), (0, 0, 0))

    col = PLAYER_COLORS[lvl % len(PLAYER_COLORS)]
    if doDim:
        led.setPixel(
            playerPos[0] + (playerPos[1] * 8), (col[0] // 3, col[1] // 3, col[2] // 3)
        )
    else:
        led.setPixel(newPos[0] + (newPos[1] * 8), col)
    led.update()


def drawField(
    overrideShowMaze: bool | None = None, showPlayer: bool = True, showEnd: bool = True
):
    global finishBrightness
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
        led.setPixel(
            pos["end"][0] + (pos["end"][1] * 8), (0, 0, min(abs(finishBrightness), 255))
        )

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


def gameLogic():
    global playerPos, pos, wallHits, playerMoveCount, finishBrightness

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

        finishBrightness -= 40
        if finishBrightness < -255:
            finishBrightness = 255
        if finishBrightness < 120 and finishBrightness > 0:
            finishBrightness = -120

        # check if new position is valid
        if 0 <= newX < MAZE_WIDTH and 0 <= newY < MAZE_HEIGHT:
            block = maze[newY][newX]

            # move player when path
            if block is None:
                playerPos = (newX, newY)

                if (
                    playerPos not in playerPath
                    and playerPos != pos["start"]
                    and playerPos != pos["end"]
                ):
                   playerPath.append(playerPos)

                playerMoveCount += 1

                updateWalls()
            # hit wall & reset player to start
            elif block == 0:
                maze[newY][newX] = WALL_MAX_BRIGHTNESS
                playerPos = pos["start"]
                playerPath.clear()

                wallHits += 1
                playerMoveCount += 1

                vib.vibrate(0.05)
                seg.setFull(wallHits)

        drawField(None, lvl < 3, True)

        time.sleep(0.2)

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
    # for i in range(5):
    #     print(f"Maze #{i + 1}")
    #     prepareGame()
    #     printMaze([pos["start"], pos["end"]])
    # exit(0)

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

            time.sleep(0.05)
        scrLines.stop()
        stopEvent.set()  # stop animation

        # wait for touch release
        t = 0
        while touch.isTouched():
            time.sleep(0.1)
            t += 1

            if t == 5:
                led.clear()
                lcd.displayMessage("Release touch      \nnow to begin...      ")

    try:
        threading.Thread(
            target=progStartAnim, args=(stopEvent,), daemon=True
        ).start()  # show animation
        lcd.displayMessage("Invis. Maze Game      ", 0)
        menuWait(True)  # show menu

        while True:
            prepareGame()  # set game variables & generate new maze
            gameLogic()  # start game
            menuWait(False)  # show menu
    except KeyboardInterrupt:
        print(" Exiting...")
