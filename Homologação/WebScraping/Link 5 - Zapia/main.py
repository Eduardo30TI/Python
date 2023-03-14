from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import pandas as pd
from glob import glob
import os
import pyautogui as gui

link_base='https://www.zapia.digital'

def Main():

    os.system('cls')

    path_base=os.path.join(os.getcwd(),'Estados','*.csv')

    arquivos=glob(path_base)

    df=pd.DataFrame()

    for arq in arquivos:

        temp_df=pd.read_csv(arq)

        df=pd.concat([df,temp_df],axis=0,ignore_index=True)

        pass

    colunas=['UF','Cidade']

    res=''

    dados=dict()
    
    for i in range(0,2):
        
        lista=df[colunas[i]].unique().tolist() if i==0 else df.loc[df[colunas[i-1]]==temp_dict[res],colunas[i]].unique().tolist()

        lista.sort()

        temp_dict=dict()

        for j,k in enumerate(lista):

            j+=1

            k=k if i==0 else str(k).title()

            print(f'{j}) {k}')

            temp_dict[j]=k
            
            pass

        while True:

            res=input('Escolha uma das opções acima: ')

            if res.isnumeric():

                res=int(res)

                if res in temp_dict.keys():

                    break

                pass

            pass

        dados[colunas[i]]=temp_dict[res]

        #break

        pass

    resp=''

    while resp=='':

        resp=input('Informe o segmento: ')

        pass

    uf=str(dados['UF']).lower()

    cidade=str(dados['Cidade']).lower()

    pesquisa=f'{cidade} {uf}'

    pesquisa=pesquisa.replace(' ','%20')

    link=f'{link_base}/busca/{pesquisa}/{resp}'

    service=Service(ChromeDriverManager().install())

    opcao=Options()
    opcao.add_argument('--start-fullscreen')

    driver=webdriver.Chrome(service=service,options=opcao)
    driver.get(link)

    while True:

        contagem=len(driver.find_elements(By.ID,'__next'))
        time.sleep(1)

        if contagem>0:

            break

        pass
    
    while True:

        contagem=len(driver.find_elements(By.XPATH,'//*[@id="__next"]/div[3]/div/div[1]/div[2]/button[2]/span'))
        time.sleep(1)

        if contagem>0:

            break

        pass

    botao=driver.find_element(By.CLASS_NAME,'sc-459cfe78-0 hDVNxD')
    print(botao)

    while True:

        pass

    pass


if __name__=='__main__':

    Main()

    pass