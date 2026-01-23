from JoyPiNoteBetterLib import LcdDisplay

lcd = LcdDisplay()
lcd.setBacklight(True)
lcd.clear()

try:
    while True:
        inText = input("Enter text to display: ") # Get user input
        lcd.showBigText(inText, 2)  # Display scrolling text
except KeyboardInterrupt:
    lcd.setBacklight(False)
    lcd.clear()
