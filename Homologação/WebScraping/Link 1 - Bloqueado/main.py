from Interface import GUI
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pyautogui as gui
import time
from bs4 import BeautifulSoup
import pandas as pd

gui=GUI()

link='https://empresasdobrasil.com/pesquisar'

link_base='https://empresasdobrasil.com'


def Main(link):

    service=Service(ChromeDriverManager().install())

    opcao=webdriver.ChromeOptions()

    opcao.add_argument('--headless')

    driver=webdriver.Chrome(service=service,chrome_options=opcao)

    driver.maximize_window()

    driver.get(link)

    page_content=driver.page_source

    site=BeautifulSoup(page_content,'html.parser')

    grupos=site.find_all('h4',attrs={'class':'headline'})

    listagem=site.find_all('ul',attrs={'class':'list-unstyled'})

    row_grupo=[]

    row_conteudo=[]

    row_link=[]

    for i in range(0,len(grupos)):
        
        conteudos=listagem[i].find_all('a',attrs={'class':'linhas'})

        for l in conteudos:

            row_grupo.append(grupos[i].get_text())
            
            row_conteudo.append(l.get_text())

            menu=l.get('href')

            link_lista=(f'{link_base}{menu}')

            row_link.append(link_lista)

            pass

        pass

    temp_dict={

        'Grupo':row_grupo,
        'Subgrupo':row_conteudo,
        'Link': row_link
    }

    df=pd.DataFrame(data=temp_dict)

    return df

    pass

def Menu():

    gui.Limpar()

    df=Main(link)

    temp=df['Grupo'].unique().tolist()

    res=gui.Menu('Menu',temp)

    temp=df['Subgrupo'].loc[df['Grupo']==res].unique().tolist()

    gui.Limpar()

    res=gui.Menu('Opções',temp)

    links=df['Link'].loc[df['Subgrupo']==res].unique().tolist()

    df=Estado(links[-1])

    temp=df['Estado'].unique().tolist()

    gui.Limpar()

    res=gui.Menu('Estado',temp)

    links=df['Link'].loc[df['Estado']==res].unique().tolist()

    Cidade(links[-1])

    pass

def Estado(link):

    service=Service(ChromeDriverManager().install())

    opcao=webdriver.ChromeOptions()

    opcao.add_argument('--headless')

    driver=webdriver.Chrome(service=service)

    driver.maximize_window()

    driver.get(link)

    page_content=driver.page_source

    site=BeautifulSoup(page_content,'html.parser')

    listagem=site.find_all('div',attrs={'class':'col-md-3'})

    for lista in listagem:

        row_lista=[content.text for content in lista.find_all('a')]

        row_link=[content.get('href') for content in lista.find_all('a')]

        pass

    temp=[]
    
    for r in row_link:

        r=(f'{link_base}{r}')

        temp.append(r)

        pass

    temp_dict={

        'Estado':row_lista,
        'Link':temp

    }

    time.sleep(5)

    df=pd.DataFrame(data=temp_dict)

    return df

    pass

def Cidade(link):

    service=Service(ChromeDriverManager().install())

    opcao=webdriver.ChromeOptions()

    opcao.add_argument('--headless')

    driver=webdriver.Chrome(service=service,chrome_options=opcao)

    driver.maximize_window()

    driver.get(link)

    page_content=driver.page_source

    site=BeautifulSoup(page_content,'html.parser')

    listagem=site.find_all('li',attrs={'class':'col-md-3'})

    print(len(listagem))

    pass

if __name__=='__main__':
    
    Menu()
    
    pass