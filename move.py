import pyautogui
import time

pyautogui.FAILSAFE = False

screenWidth, screenHeight = pyautogui.size()
currentMouseX, currentMouseY = pyautogui.position()

screenWidth, screenHeight = pyautogui.size()
currentMouseX, currentMouseY = pyautogui.position()
while True:
    pyautogui.moveRel( 150, 0)
    time.sleep(5)
    pyautogui.moveRel(-150, 0)
    time.sleep(5)