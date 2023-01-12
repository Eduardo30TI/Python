from Acesso import Login
from Query import Query
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

def main():
    
    link = 'https://cornershopapp.com/pt-br/accounts/login/?next=/stores/'
    usuario = 'renato@demarchibrasil.com.br'
    senha = 'Net@2019'

    #abrindo navegador

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get(link)

    #preenchendo campos de login

    campo = driver.find_element(By.ID,'email')
    campo.send_keys(usuario)
    campo = driver.find_element(By.ID,'password')
    campo.send_keys(senha)

    botao = driver.find_element(By.CSS_SELECTOR,'input[type="submit"]')
    botao.click()

    

    contagem = len(driver.find_elements(By.ID,'root-navigation'))

    while contagem == 0:
        
        contagem = len(driver.find_elements(By.ID,'root-navigation'))
        time.sleep(1)

        pass
    
    #Fazer Looping

    pesquisa = 'https://stores.cornershopapp.com/inventory?search=3'
    driver.get(pesquisa)

    # criando lista com bs4

    dados = BeautifulSoup(driver.page_source,'html.parser')
    print(dados.find_all('p',class_='cs-product-item__sku'))
    

    pass

if __name__== '__main__':

    main()
    pass
