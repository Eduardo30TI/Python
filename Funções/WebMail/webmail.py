from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pyperclip
import pyautogui as gui
from bs4 import BeautifulSoup

link='http://mail.demarchibrasil.com.br/Login.aspx'

usuario='bot.ti@demarchibrasil.com.br'

senha='Net@2022'

class WebMail:

    def Enviar(**kwargs):

        service=Service(ChromeDriverManager().install())

        driver=webdriver.Chrome(service=service)
        driver.maximize_window()
        driver.get(link)

        contagem=len(driver.find_elements(By.ID,'btnLogin'))
        tempo=0

        while contagem==0:

            contagem=len(driver.find_elements(By.ID,'btnLogin'))
            time.sleep(1)

            tempo+=1

            if(tempo>=3):

                break

            pass

        login=driver.find_element(By.ID,'ctl00_MPH_txtUserName')
        login.send_keys(usuario)
        time.sleep(1)

        password=driver.find_element(By.ID,'ctl00_MPH_txtPassword')
        password.send_keys(senha)
        time.sleep(1)

        button=driver.find_element(By.ID,'btnLogin')
        button.click()
        time.sleep(1)
        driver.window_handles[-1]

        contagem=len(driver.find_elements(By.ID,'fl-1866812783'))
        tempo=0

        while contagem==0:

            contagem=len(driver.find_elements(By.ID,'fl-1866812783'))
            time.sleep(1)

            tempo+=1

            if(tempo>=3):

                break

            pass

        click=driver.find_element(By.ID,'fl-1866812783')
        click.click()
        time.sleep(1)

        driver.execute_script('window.open("");')
        driver.switch_to.window(driver.window_handles[-1])

        driver.get('http://mail.demarchibrasil.com.br/Main/frmCompose.aspx?popup=true')
        
        contagem=len(driver.find_elements(By.ID,'ctl00_MPH_txtTo'))
        tempo=0

        while contagem==0:

            contagem=len(driver.find_elements(By.ID,'ctl00_MPH_txtTo'))
            time.sleep(1)

            tempo+=1

            if(tempo>=3):

                break

            pass
        
        #ctl00_MPH_txtTo
        to=driver.find_element(By.ID,'ctl00_MPH_txtTo')
        to.send_keys(';'.join([str(l).lower() for l in kwargs['kwargs']['To']]))

        #ctl00_MPH_txtCC
        cc=driver.find_element(By.ID,'ctl00_MPH_txtCC')
        cc.send_keys(';'.join([str(l).lower() for l in kwargs['kwargs']['CC']]))

        #ctl00_MPH_txtSubject

        assunto=driver.find_element(By.ID,'ctl00_MPH_txtSubject')
        assunto.click()
        assunto.send_keys(str(kwargs['kwargs']['Assunto']).strip())
        assunto.send_keys(Keys.TAB)
        time.sleep(1)

        mensagem=str(kwargs['kwargs']['Mensagem']).strip()

        pyperclip.copy(mensagem)

        gui.hotkey('ctrl','v')
        time.sleep(1)

        for l in kwargs['kwargs']['Anexo']:

            anexo=driver.find_element(By.CSS_SELECTOR,'input[type="file"]')
            anexo.send_keys(l)

            contagem=len(driver.find_elements(By.CLASS_NAME,'plupload_file_status'))
            tempo=0

            while contagem==0:

                contagem=len(driver.find_elements(By.CLASS_NAME,'plupload_file_status'))
                time.sleep(1)

                tempo+=1

                if tempo>=5:

                    break

                pass

            if contagem>0:            

                while True:

                    page_parse=driver.page_source

                    content=BeautifulSoup(page_parse,'html.parser')

                    loading=content.find('div',class_='plupload_file_status').text

                    if loading=='100%':

                        break

                    pass

                pass
            
            pass

        time.sleep(1)
        
        send=driver.find_element(By.ID,'ctl00_BPH_btnSend2')
        send.click()
        time.sleep(1)

        print('E-mail enviado com sucesso!')

        pass

    pass