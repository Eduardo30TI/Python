import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pyautogui as gui
from SQLite import Query
from Tempo import DataHora

sql=Query('MOINHO.db')

data=DataHora()

if __name__=='__main__':

    querys=dict()

    querys['Consulta']="""
    
    SELECT * FROM configuracao WHERE codigo=1
    
    """

    tabelas_df=sql.DataBase(querys=querys)
    
    usuario=tabelas_df['Consulta']['usuario'].tolist()[-1]

    senha=tabelas_df['Consulta']['senha'].tolist()[-1]

    querys['Consulta']="""
    
    SELECT * FROM links
    
    """

    tabelas_df=sql.DataBase(querys=querys)    

    links=tabelas_df['Consulta']['link'].tolist()

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

    querys['Consulta']="""
        
        SELECT * FROM configuracao WHERE codigo=1
        
        """

    tabelas_df=sql.DataBase(querys=querys)

    tempo=tabelas_df['Consulta']['tempo'].tolist()[-1]
    
    while True:

        time.sleep(tempo)
        gui.hotkey('ctrl','tab')

        data_atual=data.HoraAtual()

        hora=data_atual.hour

        if(hora>=19):

            gui.hotkey('alt','f4')

            break

        pass

    pass