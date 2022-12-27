from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd

link='https://cnpj.biz/'

def Main(pesquisa):

    servico=Service(ChromeDriverManager().install())

    opcao=Options()
    opcao.add_argument('--headless')

    driver=webdriver.Chrome(service=servico)
    driver.maximize_window()
    driver.get(link)

    contagem=len(driver.find_elements(By.ID,'q'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.ID,'q'))
        time.sleep(1)

        tempo+=1

        if(tempo>=3):

            break        

        pass

    campo=driver.find_element(By.ID,'q')
    campo.send_keys(pesquisa)
    time.sleep(1)
    campo.send_keys(Keys.ENTER)

    temp_df=pd.DataFrame(columns=['Empresa','CNPJ','Cidade','Status','Link'])

    while True:

        time.sleep(1)

        popipe=len(driver.find_elements(By.ID,'pwn'))

        if(popipe>0):

            botao=driver.find_element(By.CSS_SELECTOR,'button.pwn__button--reject')
            botao.click()

            pass     

        try:

            contagem=len(driver.find_elements(By.ID,'q'))
            tempo=0

            while contagem==0:

                contagem=len(driver.find_elements(By.ID,'q'))
                time.sleep(1)

                tempo+=1

                if(tempo>=3):

                    break        

                pass            

            page_content=driver.page_source

            site=BeautifulSoup(page_content,'html.parser')

            lista=site.find('ul',class_='divide-y divide-gray-200').findAll('li')
            
            for i in range(0,len(lista)):

                temp=[]

                empresa=lista[i].find('p',class_='text-lg font-medium text-blue-600 break-all')

                cnpj=lista[i].find('p',class_='flex items-center text-sm text-gray-500')

                cidade=lista[i].find('p',class_='mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6')

                links=lista[i].find('a')

                status=lista[i].find('div',class_='ml-2 flex-shrink-0 flex')
                
                if(empresa!=None):

                    empresa=empresa.get_text().strip().upper()

                    cnpj=cnpj.get_text().strip()

                    cidade=cidade.get_text().strip().upper()

                    status=status.find('p').get_text().strip().upper()

                    links=links.get('href')

                    temp=[empresa,cnpj,cidade,status,links]

                    temp_df.loc[len(temp_df)]=temp

                    pass
                        
                pass

            #rounded-md shadow

            contagem=len(driver.find_elements(By.XPATH,'/html/body/div/main/div[3]/div[1]/div'))
            tempo=0

            while contagem==0:

                contagem=len(driver.find_elements(By.XPATH,'/html/body/div/main/div[3]/div[1]/div'))
                time.sleep(1)

                tempo+=1

                if(tempo>=3):

                    break

                pass

            if(contagem>0):

                botao=driver.find_element(By.XPATH,'/html/body/div/main/div[3]/div[1]/div')
                botao.click()

                pass

            else:

                break
    

            pass

        except Exception as erro:

            continue

        pass

    print(temp_df)

    pass



if __name__=='__main__':


    Main('hamburgueria são paulo - sp')

    pass