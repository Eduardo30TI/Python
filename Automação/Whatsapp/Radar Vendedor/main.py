from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
#from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pytesseract import pytesseract
import cv2
import time
from Acesso import Login
from Query import Query
import pandas as pd
import os
import glob
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

link_base='https://painel.targetmob.com.br/'

path_exe=r'C:\Users\eduardo\AppData\Local\Programs\Tesseract-OCR'

usuario='comercial@demarchibrasil.com.br'

senha='654321'

querys={

    'Vendedor':

    """
    
    SELECT LTRIM(RTRIM(v.[ID Vendedor])) AS [ID Vendedor],v.[Nome Resumido],s.Equipe,
	s.Supervisor,s.[DDD Sup],s.[Telefone Sup]
	,s.Gerente,s.[DDD Gerente],s.[Telefone Gerente]
    FROM netfeira.vw_vendedor v
    INNER JOIN netfeira.vw_supervisor s ON v.[ID Equipe]=s.[ID Equipe]
    WHERE Categoria='CLT' AND [Status do Vendedor]='ATIVO'
    
    """

}

espera=60

def Main():

    link=f'{link_base}frmDefault.aspx'

    df=sql.CriarTabela(kwargs=querys)

    whatsapp=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    opcao=Options()
    opcao.add_argument('--start-fullscreen')
    service=Service()

    with webdriver.Chrome(service=service,options=opcao) as driver:

        driver.get(link)

        temp_dict={'ctl00_cphPrincipal_uscLogin_txtLogin':'comercial@demarchibrasil.com.br','ctl00_cphPrincipal_uscLogin_txtSenha':'654321'}
        cont=0

        for id in ['ctl00_cphPrincipal_uscLogin_txtLogin','ctl00_cphPrincipal_uscLogin_txtSenha','ctl00_cphPrincipal_uscLogin_txtSenha']:

            cont+=1

            if cont==2:

                #ctl00_cphPrincipal_uscLogin_ButtonCookie

                btn=WebDriverWait(driver,timeout=espera).until(lambda d: d.find_element(By.ID,'ctl00_cphPrincipal_uscLogin_ButtonCookie'))
                action=ActionChains(driver)
                action.click(btn)
                action.perform()

                pass

            campo=WebDriverWait(driver,timeout=espera).until(lambda d: d.find_element(By.ID,id))
            campo.send_keys(temp_dict[id])
            time.sleep(1)

            pass
        
        btn=WebDriverWait(driver,timeout=espera).until(lambda d: d.find_element(By.XPATH,'//*[@id="ctl00_cphPrincipal_uscLogin_btnEntrar"]'))
        action=ActionChains(driver)
        action.click(btn)
        action.perform()

        WebDriverWait(driver,timeout=espera).until(lambda d: d.find_elements(By.ID,'menu'))
        opc=WebDriverWait(driver,timeout=espera).until(lambda d: d.find_element(By.XPATH,'//*[@id="menu"]/li[3]/a'))
        action=ActionChains(driver)
        action.click(opc)
        action.perform()
        time.sleep(1)

        #//*[@id="menu"]/li[3]/ul/li/a
        opc=WebDriverWait(driver,timeout=espera).until(lambda d: d.find_element(By.XPATH,'//*[@id="menu"]/li[3]/ul/li/a'))
        action=ActionChains(driver)
        action.click(opc)
        action.perform()
        time.sleep(1)

        driver.switch_to.window(driver.window_handles[-1])
        #//*[@id="bt-ocultar-mapa"]/div/span[2]/label
        
        while True:
        
            cont=len(WebDriverWait(driver,timeout=espera).until(lambda d: d.find_elements(By.ID,'exampleInput1')))
            print(cont)
            
            if cont>0:

                break

            pass

        #exampleInput1

        for c in df['Vendedor']['ID Vendedor'].unique().tolist():

            try:

                while True:

                    cont=len(driver.find_elements(By.ID,'exampleInput1'))

                    if cont>0:

                        break

                    pass

                campo=driver.find_element(By.ID,'exampleInput1')
                campo.send_keys(c)
                time.sleep(1)
                print(c)
                
                #//*[@id="RDV__lista-vendedores_filtro"]/div/div/form/div[2]/a/img
                btn=driver.find_element(By.XPATH,'//*[@id="RDV__lista-vendedores_filtro"]/div/div/form/div[2]/a/img')
                action=ActionChains(driver)
                action.click(btn)
                action.perform()

                pass

            except:

                continue

            pass

        time.sleep(espera)

        pass

    pass


if __name__=='__main__':

    data=datetime.now()

    if not data.isoweekday() in [6,7]:

        #snackbar-container

        Main()


        pass

    pass