from Acesso import Login
from Query import Query
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

def Main():

    link='https://app.lojaintegrada.com.br/painel/login'

    usuario='eduardo.marfim@demarchibrasil.com.br'
    senha='Net@2022'

    service=Service(ChromeDriverManager().install())

    driver=webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get(link)

    contagem=len(driver.find_elements(By.ID,'hs-eu-cookie-confirmation-inner'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.ID,'hs-eu-cookie-confirmation-inner'))
        time.sleep(1)

        pass

    botao=driver.find_element(By.ID,'hs-eu-confirmation-button')
    botao.click()

    contagem=len(driver.find_elements(By.ID,'email'))

    while contagem==0:

        contagem=len(driver.find_elements(By.ID,'email'))
        time.sleep(1)

        pass


    campo=driver.find_element(By.ID,'email')
    campo.send_keys(usuario)
    time.sleep(1)
    
    campo=driver.find_element(By.ID,'password')
    campo.send_keys(senha)

    botao=driver.find_element(By.ID,'loginButton')
    botao.click()

    while True:


        pass

    pass


if __name__=='__main__':

    Main()

    pass