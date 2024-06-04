import pyautogui
import time
import os

n = input("nbr min")

for i in range(n):
    pyautogui.moveRel( 150, 0)
    time.sleep(5)
    pyautogui.moveRel(-150, 0)
    time.sleep(5)

os.system("shutdown /s")