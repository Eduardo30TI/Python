from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
import requests
import getpass

link_base='https://www.entrei.net'


def Main():

      
    tags=['lista-estados','lista-resultados locais','lista-resultados lista-categorias']

    link=''

    for i,tag in enumerate(tags):

        os.system('cls')

        link_temp=link_base if i==0 else link

        service=Service(ChromeDriverManager().install())

        opcao=ChromeOptions()
        opcao.add_argument('--headless')

        driver=webdriver.Chrome(service=service,options=opcao)

        driver.get(link_temp)

        count=len(str(tag).split(' '))

        class_tag=tag.replace(' ','.')

        while True:

            contagem=len(driver.find_elements(By.ID,tag)) if count==1 else len(driver.find_elements(By.CLASS_NAME,class_tag))
            time.sleep(1)

            if contagem>0:

                break

            pass

        page_source=driver.page_source

        page=BeautifulSoup(page_source,'html.parser')

        lista=page.find_all('ul',id=tag) if count==1 else page.find_all('ul',class_=tag)

        temp_dict=dict()

        for dados in lista:
            
            for d in dados.find_all('li'):

                uf=d.find('a').get('title')

                href=d.find('a').get('href')

                temp_dict[uf]=href

                pass

            pass

        driver.close()

        while True:

            menu=dict()

            for codigo,dados in enumerate(temp_dict.keys()):

                print(f'{codigo+1}) {dados}')

                menu[codigo+1]=dados

                pass

            while True:

                resp=input('Escolha uma das opções acima: ')

                if resp.isnumeric():

                    resp=int(resp)

                    if resp in menu.keys():

                        break

                    pass

                pass


            link=f'{link_base}{temp_dict[menu[resp]]}'

            break

            pass

        #break

        pass
    
    #Relação de clientes
    os.system('cls')

    service=Service(ChromeDriverManager().install())

    opcao=ChromeOptions()
    opcao.add_argument('--headless')

    driver=webdriver.Chrome(service=service,options=opcao)

    driver.get(link)

    while True:

        contagem=len(driver.find_elements(By.ID,'item-busca'))
        time.sleep(1)

        if contagem>0:

            break

        pass

    page_source=driver.page_source

    page=BeautifulSoup(page_source,'html.parser')

    paginas=page.find_all('div',class_='alert alert-default mb10')

    paginas=[l.get_text() for l in paginas]

    paginas=str(paginas[-1]).split('(')

    paginas=str(paginas[-1]).replace(')','').split()

    paginas=int(paginas[-1])

    clientes=[]

    for i in range(1,paginas+1):

        link_temp=f'{link}/pagina-{i}'
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(link_temp)

        while True:

            contagem=len(driver.find_elements(By.CLASS_NAME,'lista-resultados.empresas'))
            time.sleep(1)

            if contagem>0:

                break

            pass

        page_source=driver.page_source
        
        page=BeautifulSoup(page_source,'html.parser')

        lista=page.find_all('ul',class_='lista-resultados empresas')

        for dados in lista:

            os.system('cls')

            print('Aguarde estamos fazendo a varredura...')

            for d in dados.find_all('li'):

                href=d.find('a').get('href')

                link_cli=f'{link_base}{href}'

                if link_cli in clientes:

                    continue

                clientes.append(link_cli)

                pass

            pass

        pass

    df=pd.DataFrame(columns=['Empresa','Segmento','Logradouro','CEP','Bairro','Ciadade','UF'])

    maximo=len(clientes)

    for id,c in enumerate(clientes):

        os.system('cls')
        print(f'Listando o cliente {id+1} de {maximo}. Por favor aguarde...')

        driver.execute_script(f"window.open('{c}');")
        driver.switch_to.window(driver.window_handles[-1])

        while True:

            contagem=len(driver.find_elements(By.ID,'area-header-empresa'))
            time.sleep(1)

            if contagem>0:

                break

            pass

        page_source=driver.page_source

        page=BeautifulSoup(page_source,'html.parser')

        nome=[l.find('span').get_text() for l in page.find_all('h1',class_='titulo titulo-default fn org')]

        nome=str(nome[-1]).strip()

        enderecos=page.find_all('div',class_='m-3 endereco adr')

        for end in enderecos:

            try:

                cep=end.find('a',class_='info-description').get('title')
                cep=str(cep).split()[-1]

                cep_format=cep.replace('-','')

                link_cep=f'https://viacep.com.br/ws/{cep_format}/json/'

                temp_dict=CEP(link_cep)

                logradouro=end.find('span',class_='street-Address').get_text()
                logradouro=str(logradouro).strip().upper()

                bairro=str(temp_dict['bairro']).upper()
                
                cidade=str(temp_dict['localidade']).upper()

                uf=str(temp_dict['uf']).upper()

                df.loc[len(df)]=[nome,menu[resp],logradouro,cep,bairro,cidade,uf]

                pass

            except:

                continue

            pass

        #break

        pass

    temp_path=os.getcwd()

    usuario=getpass.getuser()

    count=temp_path.find(usuario)

    temp_path=temp_path[:count]
    
    temp_path=os.path.join(temp_path,usuario,'Downloads','Leads Entrei.Net')

    if not os.path.exists(temp_path):

        os.makedirs(temp_path)

        pass

    path_base=os.path.join(temp_path,f'{menu[resp]}_{cidade}.xlsx')

    df.to_excel(path_base,index=False,encoding='UTF-8')

    pass

def CEP(link):

    content=requests.get(link)

    return content.json()

    pass

if __name__=='__main__':
    
    Main()

    pass