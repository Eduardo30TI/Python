import pyperclip as pc
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
import phonenumbers
import urllib
import pyautogui as gui

contato='11995088584'

caminho=r'C:\Users\eduardo\Downloads\Redução de Base de Cálculo ICMS - Fiscal DFE.pdf'

contato_formatado=phonenumbers.parse(contato,'BR')

contato_formatado=phonenumbers.format_number(contato_formatado,phonenumbers.PhoneNumberFormat.INTERNATIONAL)

driver=webdriver.Chrome(executable_path=r'C:\Users\eduardo\OneDrive - NETFEIRA PONTOCOM LTDA\Python\Testes\Teste03 Whatsapp\chromedriver.exe')

driver.get('https://web.whatsapp.com/')

while len(driver.find_elements_by_id('pane-side'))<=0:

    print('Aguardando...')

    time.sleep(1)

    pass

texto='Boa tarde teste de automação'

texto=urllib.parse.quote(texto)

mensagem=f'https://web.whatsapp.com/send?phone={contato_formatado}&text={texto}'

driver.get(mensagem)

while len(driver.find_elements_by_id('pane-side'))<=0:

    print('Aguardando...')

    time.sleep(1)

    pass

time.sleep(3)

adicionar=driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div/span')
adicionar.click()
time.sleep(3)

adicionar=driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/div/ul/li[4]/button/span')
adicionar.click()
time.sleep(3)

pc.copy(caminho)
pc.paste()

gui.hotkey('ctrl','v')
gui.press('enter')

while len(driver.find_elements_by_class_name('_1w1m1'))<=0:

    time.sleep(1)

    pass

enviar=driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div/span')
enviar.click()
time.sleep(3)

enviar=driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span')
enviar.click()
time.sleep(3)