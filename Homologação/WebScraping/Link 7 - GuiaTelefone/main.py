from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from Interface import GUI
from Acentos import Acentuacao
import time
import os
import pandas as pd
from glob import glob
import getpass

link_base='https://www.guiatelefone.com'

temp_dict=dict()

gui=GUI()

def Main():

    temp_path=os.path.join(os.getcwd(),'Estados','*.csv')

    temp_cliente=[]

    arquivos=glob(temp_path)

    temp_df=pd.DataFrame()

    for arq in arquivos:

        df=pd.read_csv(arq,encoding='UTF-8')

        temp_df=pd.concat([temp_df,df],axis=0,ignore_index=True)

        pass

    df=temp_df

    global temp_dict

    temp_dict={'UF':'','Cidade':''}

    info=[l for l in temp_dict.keys()]

    resp=''

    for i,c in enumerate(info):

        dados=df[c].unique().tolist() if i==0 else df.loc[df[info[i-1]]==resp,c].unique().tolist()

        dados.sort()

        resp=gui.Menu(c,dados)

        temp_dict[c]=Acentuacao.RemoverAcento(str(resp).lower())

        pass

    pesquisa=(f'{str(temp_dict["Cidade"]).title()}, {str(temp_dict["UF"]).upper()}')

    while True:

        campo=input('Informe o segmento que deseja buscar: ')

        if campo!='':

            break

        pass

    temp_dict['Segmento']=campo.title()

    service=Service(ChromeDriverManager().install())
    opcao=ChromeOptions()
    opcao.add_argument('--headless')

    driver=webdriver.Chrome(service=service,options=opcao)
    driver.get(link_base)

    while True:

        contagem=len(driver.find_elements(By.ID,'what'))
        time.sleep(1)

        if contagem>0:

            break

        pass

    campo=driver.find_element(By.ID,'what')
    campo.send_keys(temp_dict['Segmento'])

    while True:

        contagem=len(driver.find_elements(By.ID,'where'))
        time.sleep(1)

        if contagem>0:

            break

        pass

    campo=driver.find_element(By.ID,'where')
    campo.send_keys(pesquisa)
    campo.send_keys(Keys.ENTER)

    while True:

        contagem=len(driver.find_elements(By.XPATH,'/html/body/main/section/div/div[3]/div[1]/nav'))
        time.sleep(1)

        if contagem>0:

            break

        pass
    
    loop=0

    while True:

        gui.Limpar()

        loop+=1

        print(f'Mapeando a página {loop}. Aguarde...')

        driver.switch_to.window(driver.window_handles[-1])
        page=BeautifulSoup(driver.page_source,'html.parser')

        nav=page.find_all('nav')

        elementos=nav[-1].find_all('a')

        artigos=page.find_all('article')

        label_prox=str(elementos[-1].get_text()).strip()

        href_prox=elementos[-1].get('href')

        for art in artigos:

            href=art.find('a').get('href')

            href=f'{link_base}{href}'

            if href in temp_cliente:

                continue

            temp_cliente.append(href)
                
            pass

        if label_prox=='Próximo':

            link=f'{link_base}{href_prox}'

            driver.get(link)

            pass

        else:

            break

        pass
    
    Extrair(temp_cliente)

    pass

def Extrair(links):

    df=pd.DataFrame(columns=['Empresa','Categoria','CEP','Logradouro','Cidade','Estado','Seq','Contato'])

    service=Service(ChromeDriverManager().install())
    opcao=ChromeOptions()
    opcao.add_argument('--headless')

    driver=webdriver.Chrome(service=service,options=opcao)
    
    df=pd.DataFrame(columns=['Empresa','Categoria','Logradouro','Cidade','UF','Contatos','Telefone'])

    temp=[]

    for id,link in enumerate(links):

        gui.Limpar()

        print(f'Aguarde estamos consolidado as informações de {id+1} até {len(links)}')
        
        driver.get(link)
        driver.switch_to.window(driver.window_handles[-1])

        while True:

            contagem=len(driver.find_elements(By.XPATH,'/html/body/main/section/div/div[2]/h1'))
            time.sleep(1)

            if contagem>0:

                break

            pass

        page=BeautifulSoup(driver.page_source,'html.parser')

        try:

            empresa=page.select_one('h1.text-2xl').get_text().strip().upper()

            categoria=page.select_one('a.text-sm').get_text().strip().upper()

            logradouro=page.select_one('p.font-medium').get_text().strip().upper()

            cidade=str(temp_dict['Cidade']).upper()

            uf=str(temp_dict['UF']).upper()

            telefones=[l.get_text().strip() for l in page.select('div.mb-6 >ul>li>span>a')]

            for j,tel in enumerate(telefones):

                j+=1

                contato=f'Contato {j}'

                if empresa in temp:

                    continue

                temp.append(empresa)

                df.loc[len(df)]=[empresa,categoria,logradouro,cidade,uf,contato,tel]

                pass

            pass

        except:

            continue

        #break

        pass

    temp_path=os.getcwd()

    usuario=getpass.getuser()

    count=temp_path.find(usuario)

    temp_path=temp_path[:count]
    
    temp_path=os.path.join(temp_path,usuario,'Downloads','Leads GuiaTelefone')

    if not os.path.exists(temp_path):

        os.makedirs(temp_path)

        pass
    
    arquivo=f'{temp_dict["Segmento"]}_{temp_dict["Cidade"]}_{temp_dict["UF"]}'

    arquivo=f'{arquivo.upper()}.xlsx'

    path_base=os.path.join(temp_path,arquivo)

    df=df.pivot(index=['Empresa','Categoria','Logradouro','Cidade','UF'],columns='Contatos',values='Telefone').reset_index()

    df=df.loc[df['Categoria'].str.contains(str(temp_dict['Segmento']).upper())]

    if len(df)>0:

        df.to_excel(path_base,index=False,encoding='UTF-8')
        
        print('Arquivo gerado com sucesso!')

        pass

    else:

        print('Não foi possível gerar o arquivo!')

        pass

    pass

if __name__=='__main__':

    Main()

    resp=gui.Retorno('Deseja executar novamente?[s/n]: ')

    if resp==True:

        Main()

        pass

    pass