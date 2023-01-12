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
    
    link = 'https://painel.targetmob.com.br/frmLogin.aspx'
    usuario = 'comercial@demarchibrasil.com.br'
    senha = '654321'

    #abrindo navegador

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get(link)
    time.sleep(2)
    #preenchendo campos de login
    botao = driver.find_element(By.ID,'ctl00_cphPrincipal_uscLogin_ButtonCookie')
    botao.click()
    time.sleep(2)
    campo = driver.find_element(By.ID,'ctl00_cphPrincipal_uscLogin_txtLogin')
    campo.send_keys(usuario)
    campo = driver.find_element(By.ID,'ctl00_cphPrincipal_uscLogin_txtSenha')
    campo.send_keys(senha)
    
    

    botao = driver.find_element(By.CSS_SELECTOR,'input[type="submit"]')
    botao.click()

    time.sleep(5)

    contagem = len(driver.find_elements(By.ID,'select-produto'))

    while contagem == 0:
        
        contagem = len(driver.find_elements(By.ID,'select-produto'))
        time.sleep(1)

        pass
    
    #Fazer Looping

    pesquisa = 'https://www.paineltarget.com.br/gps/v3.4.6/index.html?opc1=Q0xJRU5URV80NTY=&opc2=MTAuMTI4LjAuMzI=&opc3='
    driver.get(pesquisa)

    # criando lista com bs4

    dados = BeautifulSoup(driver.page_source,'html.parser')
    print(dados.find_all('p',class_='cs-product-item__sku'))
    

    pass

if __name__== '__main__':

    main()
    pass