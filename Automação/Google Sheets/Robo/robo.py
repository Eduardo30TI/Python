import pyautogui as gui
import time

def Robo():

    for image in ['login.png','continuar.png','continuar.png']:

        gui.hotkey('ctrl','end')
        img=gui.locateCenterOnScreen(image)
        print(img)
        gui.click(img.x,img.y)

        pass

    pass



if __name__=='__main__':

    Robo()

    pass