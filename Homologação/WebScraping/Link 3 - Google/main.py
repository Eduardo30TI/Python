from selenium import webdriver
from setuptools import Command
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd
import os
import getpass
import shutil
from glob import glob
from Interface import GUI
from datetime import datetime

gui=GUI()

link='https://www.google.com.br'

def Main(pesquisa):

    service=Service(ChromeDriverManager().install())

    driver=webdriver.Chrome(service=service)

    driver.maximize_window()

    driver.get(link)

    contagem=driver.find_element(By.ID,'gb')
    tempo=0

    while contagem==0:

        contagem=driver.find_element(By.ID,'gb')
        time.sleep(1)

        tempo+=1

        if(tempo>=3):

            driver.close()

            Main(pesquisa)

            break

        pass

    contagem=len(driver.find_elements(By.CLASS_NAME,'gLFyf'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.CLASS_NAME,'gLFyf'))
        time.sleep(1)

        tempo+=1

        if(tempo>=3):

            driver.close()

            Main(pesquisa)

            break        

        pass

    campo=driver.find_element(By.CLASS_NAME,'gLFyf')
    campo.send_keys(pesquisa)
    time.sleep(1)
    campo.send_keys(Keys.ENTER)

    contagem=len(driver.find_elements(By.CLASS_NAME,'ixix9e'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.CLASS_NAME,'ixix9e'))
        time.sleep(1)

        tempo+=1

        if(tempo>=3):

            driver.close()

            Main(pesquisa)

            break

        pass

    contagem=len(driver.find_elements(By.CLASS_NAME,'w7Dbne'))
    tempo=0

    cont=0

    while contagem==0:

        tempo+=1

        contagem=len(driver.find_elements(By.CLASS_NAME,'w7Dbne'))
        time.sleep(1)

        if(tempo>=3):

            driver.close()

            Main(pesquisa)

            break

        pass

    botao=driver.find_element(By.CLASS_NAME,'w7Dbne')
    botao.click()
    time.sleep(1)

    contagem=0

    while contagem==0:

        contagem=len(driver.find_elements(By.ID,'center_col'))
        time.sleep(1)

        pass

    df=pd.DataFrame()

    row_emp=[]

    row_categ=[]

    row_end=[]

    row_tel=[]

    row_avaliacao=[]

    row_comentario=[]

    while True:

        page_content=driver.page_source
        
        site=BeautifulSoup(page_content,'html.parser')

        tags_containers=site.find_all('div',attrs={'jscontroller':'AtSb'})
        
        for tag in tags_containers:

            try:

                id=tag.get('id')

                click=driver.find_element(By.ID,f'{id}')
                click.click()
                time.sleep(1)

                page_content=driver.page_source

                site=BeautifulSoup(page_content,'html.parser')

                categorias=site.find_all('span',attrs={'class':'YhemCb'})

                contagem=len(driver.find_elements(By.CSS_SELECTOR,'span.YhemCb'))
                        
                categoria=str(categorias[-1].get_text()).strip() if contagem>0 else ''

                endereço=site.find('span',attrs={'class':'LrzXr'}).get_text().strip()

                contagem=len(driver.find_elements(By.CSS_SELECTOR,'span.LrzXr.zdqRlf.kno-fv'))

                if(contagem>0):

                    telefone=site.find('span',class_='LrzXr zdqRlf kno-fv').find('span').getText().strip()

                    pass

                else:

                    telefone=''

                    pass

                contagem=len(driver.find_elements(By.CSS_SELECTOR,'span.Aq14fc'))

                if(contagem>0):

                    avaliacao=site.find('span',class_='Aq14fc').get_text().strip()

                    avaliacao=float(avaliacao.replace(',','.'))

                    pass

                else:

                    avaliacao=''

                    pass

                contagem=len(driver.find_elements(By.CSS_SELECTOR,'span.z5jxId'))

                if(contagem>0):

                    comentario=site.find('span',attrs={'class':'z5jxId'}).get_text().strip()

                    comentario=[i for i in comentario.split()]

                    comentario=int(comentario[0])

                    pass

                else:

                    comentario=0

                    pass

                empresa=site.find('div',class_='SPZz6b').find('h2')

                empresa=empresa.find('span').get_text()

                if(empresa.upper() in row_emp):

                    continue

                row_emp.append(empresa.upper())

                row_categ.append(categoria.upper())

                row_end.append(endereço.upper())

                row_tel.append(telefone)

                row_avaliacao.append(avaliacao)

                row_comentario.append(comentario)

                pass

            except Exception as erro:

                continue

                pass
 
            pass

        contagem=len(driver.find_elements(By.ID,'pnnext'))

        if(contagem==0):

            break

        else:

            btn_prox=driver.find_element(By.ID,'pnnext')
            btn_prox.click()

            time.sleep(5)

            pass

        #break

        pass

    temp_dict={

        'Empresa':row_emp,
        'Categoria':row_categ,
        'Endereço':row_end,
        'Telefone':row_tel,
        'Avaliação':row_avaliacao,
        'Comentário':row_comentario
    }

    temp_df=pd.DataFrame(data=temp_dict)

    return temp_df

    pass

def CriarDiretorio():

    usuario=getpass.getuser()

    path_base=str(os.getcwd())

    cont=path_base.find('Users')

    path_base=path_base[:cont]

    path_base=os.path.join(path_base,'Users',usuario,'Downloads')

    temp_path=os.path.join(path_base,'LeadsGoogle')

    if(not os.path.exists(temp_path)):
        
        os.mkdir(temp_path)

        pass

    return temp_path

    pass

def Menu():
    
    temp_path=os.path.join(os.getcwd(),'Estados','*.csv')

    arquivos=glob(temp_path)

    lista_df=pd.DataFrame()

    for arq in arquivos:
        
        temp_df=pd.read_csv(arq)

        lista_df=pd.concat([lista_df,temp_df],axis=0,ignore_index=True)

        pass

    temp_dict={

        'UF':'',
        'Cidade':''
    }
        
    for i,key in enumerate(temp_dict.keys()):

        listagem=[]

        gui.Limpar()
        
        if(i==0):

            listagem=lista_df['UF'].unique().tolist()

            pass

        else:

            listagem=lista_df['Cidade'].loc[lista_df['UF']==res].unique().tolist()

            listagem.sort()

            pass
        
        res=gui.Menu(key,listagem)

        temp_dict[key]=res

        pass

    print(f'Cidade escolhida: {res}')

    temp=[]

    segmento=''

    while segmento=='':

        segmento=input('Informe um segmento: ').upper()

        pass

    resp=gui.Retorno('Deseja escolhar um bairro?[s/n]: ')

    st_bairro=False
    
    if(resp):

        bairros=[]

        while True:

            bairro=''

            while bairro=='':

                bairro=input('Informe o bairro: ').upper()
                
                pass

            conteudo=(f'{segmento} {bairro} {temp_dict["UF"]}')

            temp.append(conteudo)

            resp=gui.Retorno('Deseja inserir mais um bairro na pesquisa?[s/n]: ')

            bairros.append(bairro)

            if(not resp):

                st_bairro=True

                break

            pass

        pass

    else:

        conteudo=(f'{segmento} {temp_dict["Cidade"]} {temp_dict["UF"]}')

        temp.append(conteudo)

        pass
    
    df=pd.DataFrame()

    opc=['pousada','motel','hotel','chale']

    for i,t in enumerate(temp):

        if(segmento.lower() in opc):

            try:

                temp_df=Hotel(pesquisa=t,segmento=segmento)

                pass

            except:

                temp_df=Hotel(pesquisa=t,segmento=segmento)

                pass

            pass

        else:
        
            temp_df=Main(pesquisa=t)

            pass

        if(len(df)>0):

            empresas=df['Empresa'].unique().tolist()

            temp_df=temp_df.loc[~temp_df['Empresa'].isin(empresas)&(temp_df['Endereço'].str.contains(bairros[i]))]

            pass

        df=pd.concat([df,temp_df],axis=0,ignore_index=True)
 
        pass

    if(len(df)>0):

        ano=datetime.now().year

        mes=datetime.now().month

        dia=datetime.now().day

        arq=(f'{segmento}_{temp_dict["Cidade"]}_{temp_dict["UF"]}_{ano}_{mes}_{dia}')

        if(st_bairro):

            df=df.loc[(df['Categoria'].str.contains(segmento))]

            pass

        else:

            df=df.loc[(df['Categoria'].str.contains(segmento))&(df['Endereço'].str.contains(temp_dict['Cidade']))]

            pass

        df.sort_values('Avaliação',ascending=False,ignore_index=True,inplace=True)

        df['CEP']=df['Endereço'].apply(CEP)

        df.to_excel(f'{arq}.xlsx',index=False,encoding='UTF-8')

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        path_orig=glob(temp_path) 

        path_dest=CriarDiretorio()

        path_dest=os.path.join(path_dest,os.path.basename(path_orig[-1]))

        shutil.move(path_orig[-1],path_dest)

        print('Arquivo gerado com sucesso!')

        pass

    resp=gui.Retorno('Deseja executar novamente?[s/n]: ')

    if(resp):

        Menu()

        pass

    pass

def Hotel(pesquisa,segmento):

    servico=Service(ChromeDriverManager().install())
    driver=webdriver.Chrome(service=servico)
    driver.maximize_window()
    driver.get(link)

    #CH6Bmd

    contagem=len(driver.find_elements(By.XPATH,'/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.XPATH,'/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input'))
        time.sleep(1)

        tempo+=1

        if(tempo>3):

            break

        pass

    campo=driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
    campo.send_keys(pesquisa)
    campo.send_keys(Keys.ENTER)

    contagem=len(driver.find_elements(By.CSS_SELECTOR,'div.CH6Bmd'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.CSS_SELECTOR,'div.CH6Bmd'))
        time.sleep(1)

        tempo+=1

        if(tempo>3):

            break

        pass

    contagem=len(driver.find_elements(By.XPATH,'//*[@id="rso"]/div[1]/div/div/div/div/div/div[3]/div/g-more-link/a/div'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.XPATH,'//*[@id="rso"]/div[1]/div/div/div/div/div/div[3]/div/g-more-link/a/div'))
        time.sleep(1)

        tempo+=1

        if(tempo>3):

            break

        pass

    botao=driver.find_element(By.XPATH,'//*[@id="rso"]/div[1]/div/div/div/div/div/div[3]/div/g-more-link/a/div')
    botao.click()

    contagem=len(driver.find_elements(By.CSS_SELECTOR,'div.l5cSPd'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.CSS_SELECTOR,'div.l5cSPd'))
        time.sleep(1)

        tempo+=1

        if(tempo>3):

            driver.close()

            Hotel(pesquisa)

            break

        pass

    page_content=driver.page_source

    site=BeautifulSoup(page_content,'html.parser')

    elementos=site.find_all('a',class_='PVOOXe')

    temp=[]

    for i in range(0,len(elementos)):
        
        href=elementos[i].get('href')

        href=(f'{link}{href}')

        if(href in temp):

            continue

        temp.append(href)

        pass

    df=pd.DataFrame(columns=['Empresa','Categoria','Endereço','Telefone','Avaliação'])

    for href in temp:

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(href)

        try:

            contagem=len(driver.find_elements(By.XPATH,'//*[@id="featured"]/c-wiz/c-wiz/div[3]/div/div[3]/span'))

            if(contagem==0):

                botao=driver.find_element(By.XPATH,'//*[@id="featured"]/c-wiz/c-wiz/div[3]/div/div[3]/span')
                botao.click()

                pass

            pass 

        except:

            contagem=0

            pass

        page_content=driver.page_source

        site=BeautifulSoup(page_content,'html.parser')

        empresa=site.find('h1',class_='QORQHb r77R5e').get_text().strip().upper()

        info=site.find_all('span',class_='CFH2De')

        if(len(info)>0):

            contagem=len(driver.find_elements(By.XPATH,'//*[@id="overview"]/c-wiz/c-wiz/div/div/div/c-wiz[1]/div/section[1]/c-wiz/div[1]/div[1]/div[2]/span'))
            tempo=0

            while contagem==0:

                contagem=len(driver.find_elements(By.XPATH,'//*[@id="overview"]/c-wiz/c-wiz/div/div/div/c-wiz[1]/div/section[1]/c-wiz/div[1]/div[1]/div[2]/span'))
                time.sleep(1)

                tempo+=1

                if(tempo>=3):

                    break

                pass

            if(contagem>0):

                estrela=site.find('div',class_='fnmyY').findAll('span',class_='CFH2De')

                estrela=[l for l in str(estrela[0]).split() if l.isnumeric()]

                estrela=int(estrela[-1])

                info=site.find('div',class_='K4nuhf').findAll('span',class_='CFH2De')

                telefone=info[-1].get_text().strip()

                endereco=info[0].get_text().strip().upper()

                linhas=[empresa,str(segmento).upper(),endereco,telefone,estrela]

                df.loc[len(df)]=linhas

                pass

            pass
                                
        #break

        pass

    return df
    
    pass

def CEP(endereco):
    
    endereco=endereco.split()
    
    return endereco[-1]
    
    pass

if __name__=='__main__':
    
    try:

        Menu()

        pass

    except KeyboardInterrupt:

        Menu()

        pass
    
    pass