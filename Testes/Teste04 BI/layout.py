import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pyautogui as gui


biblioteca={'selenium':'pip install selenium','DriverManager':'pip install webdriver-manager'}

def Instalador():

    for comando in biblioteca.values():

        os.system(comando)

        comando=comando.split()

        comando=f'pip install --upgrade {comando[-1]}'

        os.system(comando)

        pass

    pass


if __name__=='__main__':

    Instalador()

    links=['https://app.powerbi.com/groups/me/dashboards/4bf589a9-c41f-422d-a46b-057737a09526?chromeless=true','https://app.powerbi.com/groups/me/dashboards/4bf589a9-c41f-422d-a46b-057737a09526?chromeless=true','https://app.powerbi.com/groups/me/dashboards/4bf589a9-c41f-422d-a46b-057737a09526?chromeless=true']

    usuario='netfeira14@netfeira.onmicrosoft.com'

    senha='Net@2019'

    service=Service(ChromeDriverManager().install())

    driver=webdriver.Chrome(service=service)

    driver.maximize_window()

    for i,link in enumerate(links):
        
        if(i==0):

            driver.get(link)

            pass

        else:
            
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(link)

            pass

        indice=len(driver.find_elements(By.ID,'email'))
        
        if(indice>0):

            while indice<=0:

                time.sleep(1)

                pass

            campo=driver.find_element(By.ID,'email')
            time.sleep(1)
            campo.click()
            time.sleep(1)
            campo.send_keys(usuario)

            indice=len(driver.find_elements(By.ID,'submitBtn'))

            while indice<=0:

                time.sleep(1)

                pass            

            campo=driver.find_element(By.ID,'submitBtn')
            time.sleep(1)
            campo.click()

            time.sleep(1)
            janela=driver.window_handles

            driver.switch_to.window(janela[-1])

            time.sleep(1)
            indice=len(driver.find_elements(By.ID,'i0118'))

            while indice<=0:

                time.sleep(1)

                pass

            campo=driver.find_element(By.ID,'i0118')
            time.sleep(1)
            campo.send_keys(senha)
            time.sleep(1)
            campo.send_keys(Keys.ENTER)

            time.sleep(1)
            janela=driver.window_handles

            driver.switch_to.window(janela[-1])

            time.sleep(1)
            indice=len(driver.find_elements(By.ID,'KmsiCheckboxField'))

            while indice<=0:

                time.sleep(1)

                pass

            campo=driver.find_element(By.ID,'KmsiCheckboxField')
            time.sleep(1)
            campo.click()
            time.sleep(1)
            campo.send_keys(Keys.ENTER)

            pass

        #//*[@id="pbiThemed0"]/full-screen-controls/div/span[2]/button[1]

        time.sleep(1)
        indice=len(driver.find_elements(By.ID,'pbiAppPlaceHolder'))

        while indice<=0:

            time.sleep(1)

            pass

        time.sleep(1)
        botao=driver.find_element(By.XPATH,'//*[@id="pbiThemed0"]/full-screen-controls/div/span[2]/button[1]')
        time.sleep(1)
        botao.click()

        time.sleep(2)

        pass

    gui.hotkey('ctrl','tab')
    gui.press('f11')
    
    pass