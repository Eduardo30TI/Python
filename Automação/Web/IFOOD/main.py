from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

espera=60

def Main():

    link_base='https://portal.ifood.com.br/login'

    login='eduardo.marfim@demarchibrasil.com.br'

    password='Net@2023#23'

    service=Service(ChromeDriverManager().install())
    option=Options()
    
    option.add_argument('--headless')
    
    driver=webdriver.Chrome(service=service)
    driver.get(link_base)
    driver.fullscreen_window()

    acesso={'email':login,'password':password}

    for tag,acess in acesso.items():

        WebDriverWait(driver,timeout=espera).until(lambda d: d.find_element(By.ID,tag))
        campo=driver.find_element(By.ID,tag)
        campo.send_keys(acess)

        WebDriverWait(driver,timeout=espera).until(lambda d: d.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[1]/div/div[3]/div/div[2]/main/form/button'))
        botao=driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[1]/div/div[3]/div/div[2]/main/form/button')
        botao.click()

        pass
    
    WebDriverWait(driver,timeout=espera).until(lambda d: d.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[1]/div/div[3]/div/div[2]/main/div/div/div[2]/button[1]'))
    botao=driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[1]/div/div[3]/div/div[2]/main/div/div/div[2]/button[1]')
    botao.click()


    while True:


        pass


    pass



if __name__=='__main__':

    Main()

    pass