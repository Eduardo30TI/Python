import pysftp
import os
from getpass import getuser
from glob import glob
from RemoverArquivo import Remover
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import pyautogui as gui
from selenium.webdriver.common.alert import Alert


hostname='20.96.234.129'

port=22

user='usr_dist113'

password='BB103613281368100610'

espera=3600


def Main():

    temp_path=os.path.join(os.getcwd(),'*.txt')

    arquivos=glob(temp_path)

    cnOpts=pysftp.CnOpts()
    cnOpts.hostkeys=None

    with pysftp.Connection(host=hostname,port=port,username=user,password=password,cnopts=cnOpts) as sftp:

        print('Conectado')

        for arq in arquivos:

            sftp.put(arq)

            pass

        pass

    Remover.RemoverArquivo('.txt')

    pass

def Web():

    print('Aguarde ...')

    link_base='https://painel.targetmob.com.br/'

    usuario='comercial@demarchibrasil.com.br'

    senha='654321'

    link=f'{link_base}frmDefault.aspx'

    opcao=ChromeOptions()
    #opcao.add_argument('--start-fullscreen')
    opcao.add_argument('--headless=new')
    opcao.add_experimental_option('prefs',{'download.default_directory':os.getcwd(),'safebrowsing.enabled':'false'})

    service=Service(ChromeDriverManager().install())
    driver=webdriver.Chrome(service=service,options=opcao)
    driver.get(link)

    lista=['ctl00_cphPrincipal_uscLogin_txtLogin','ctl00_cphPrincipal_uscLogin_ButtonCookie','ctl00_cphPrincipal_uscLogin_txtSenha','ctl00_cphPrincipal_uscLogin_btnEntrar']

    temp_dict={'ctl00_cphPrincipal_uscLogin_txtLogin':usuario,'ctl00_cphPrincipal_uscLogin_txtSenha':senha}

    for i,id in enumerate(lista):

        if i in [1,3]:

            #aceitar os cookies
            #ctl00_cphPrincipal_uscLogin_ButtonCookie
            botao=WebDriverWait(driver,timeout=espera).until(lambda d: d.find_element(By.ID,id))
            botao.click()
            time.sleep(1)

            pass

        else:

            campo=WebDriverWait(driver=driver,timeout=espera).until(lambda d: d.find_element(By.ID,id))
            campo.send_keys(temp_dict[id])

            pass

        pass

    time.sleep(2)

    combox=WebDriverWait(driver=driver,timeout=espera).until(lambda d: d.find_element(By.ID,'ctl00_uscUsuarioLogado1_ddlProduto'))
    combox.click()
    time.sleep(2)

    select=Select(combox)
    all_options=[l.get_attribute('value') for l in select.options]

    select.select_by_value(all_options[-1])
    time.sleep(1)

    links=['https://painel.targetmob.com.br/frmDefaultSite.aspx?menuExterno=1&IDTela=107','https://edi.paineltarget.inf.br:8189/TargetSellOutWebPage/ConsultaGeracoes/FrmConsultaGeracoes.aspx?TIPOTELA=0']
    
    for l in links:
    
        driver.get(l)
        time.sleep(1)

        pass
    time.sleep(3)

    lista=['ddlEmpresa','ddlSellOut','txtDataGeracaoInicioFiltro','txtDataGeracaoFinalFiltro','btnBuscar']

    for i,id in enumerate(lista):

        if i in[0,1]:

            combox=WebDriverWait(driver=driver,timeout=espera).until(lambda d: d.find_element(By.ID,id))
            combox.click()
            select=Select(combox)
            all_options=[l.get_attribute('value') for l in select.options]

            pass

        if i==0:

            select.select_by_value(all_options[-1])

            pass

        elif i==1:

            select.select_by_value(all_options[1])

            pass

        elif i in [2,3]:

            dt_atual=datetime.strftime(datetime.now().date(),'%d/%m/%Y')

            #dt_atual='01/05/2023'

            campo=WebDriverWait(driver=driver,timeout=espera).until(lambda d: d.find_element(By.ID,id))
            campo.send_keys(dt_atual)
   
            pass

        else:

            botao=WebDriverWait(driver=driver,timeout=espera).until(lambda d: d.find_element(By.ID,id))
            botao.click()

            pass

        time.sleep(1)

        pass

    #//*[@id="gdvList"]/tbody/tr[2]/td[10]/a/span,//*[@id="gdvList"]/tbody/tr[3]/td[10]/a/span,//*[@id="gdvList"]/tbody/tr[6]/td[10]/a/span
    #//*[@id="gdvList"]/tbody/tr[2]/td[10]/a

    page=BeautifulSoup(driver.page_source,'html.parser')
    element=page.find('table',id='gdvList').find_all('tr',class_='rowGrid')    

    for i in range(2,len(element)+2):

        os.system('cls')

        print(f'Download {i-1} de {len(element)}')
        
        id=element[i-2].find('span').get('id')

        xpath=f'//*[@id="gdvList"]/tbody/tr[{i}]/td[10]/a'

        download=WebDriverWait(driver=driver,timeout=espera).until(lambda d: d.find_element(By.ID,id))
        click=WebDriverWait(driver=driver,timeout=espera).until(lambda d: d.find_element(By.XPATH,xpath))
        action=ActionChains(driver)
        action.move_to_element(download).click(click)
        action.perform()
        #img=gui.locateCenterOnScreen('download.png')
        #gui.click(img.x,img.y)
        time.sleep(10)

        try:    

            alert = Alert(driver)

            print(alert.text)

            alert.accept()

            pass

        except:

            continue

        #break

        pass

    
    driver.close()

    Main()

    pass

if __name__=='__main__':

    Web()

    pass