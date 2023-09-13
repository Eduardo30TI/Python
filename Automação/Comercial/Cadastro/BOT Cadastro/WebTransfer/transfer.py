from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

class Web:

    def __init__(self,arquivo):

        self.link_base='https://wetransfer.com/'

        self.arquivo=arquivo

        pass

    def WebLink(self):

        #service=Service(ChromeDriverManager().install())
        service=Service()
        option=Options()
        option.add_argument('--headless')
        

        driver=webdriver.Chrome(service=service)
        driver.get(self.link_base)

        #aceitar os termos de uso
        while True:

            contagem=len(driver.find_elements(By.XPATH,'//*[@id="__next"]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[4]/button[1]'))

            if contagem>0:

                break

            pass

        botao=driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[4]/button[1]')
        botao.click()
        time.sleep(2)

        while True:

            contagem=len(driver.find_elements(By.CSS_SELECTOR,'button.transfer__button'))

            if contagem>0:

                break

            pass
        
        botao=driver.find_element(By.CSS_SELECTOR,'button.transfer__button')
        botao.click()

        anexo=driver.find_element(By.CSS_SELECTOR,'input[type="file"]')
        anexo.send_keys(self.arquivo)
        
        #/html/body/div[2]/div/div[2]/div/div[2]/button[1]
        botao=driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[3]/div[1]/div[2]/button[1]/svg')
        botao.click()
        time.sleep(2)

        #/html/body/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div[1]/div/div[2]
        botao=driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[3]/div[1]/div[1]/div[1]/div[3]/div[1]/div/div[2]/label')
        botao.click()
        time.sleep(2)

        #transfer__button transfer-link__url
        while True:

            contagem=len(driver.find_elements(By.XPATH,'//*[@id="__next"]/div/div[3]/div[1]/div[2]/button[2]'))

            if contagem>0:

                break

            pass
        botao=driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[3]/div[1]/div[2]/button[2]')
        botao.click()
        time.sleep(2)

        while True:
        
            page=BeautifulSoup(driver.page_source,'html.parser')

            elemento=page.select_one('.transfer-link__url')

            if elemento!=None:

                break

            pass

        return elemento.get('value')

        pass


    pass