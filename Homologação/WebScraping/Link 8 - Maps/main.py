from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from glob import glob
import os
import pandas as pd
from Interface import GUI

gui=GUI()


link_base='https://www.google.com.br/maps/'

def Main():

    gui.Limpar()

    temp_path=os.path.join(os.getcwd(),'Estados','*.csv')

    arquivos=glob(temp_path)

    temp_df=pd.DataFrame()

    for arq in arquivos:

        df=pd.read_csv(arq,encoding='UTF-8')

        temp_df=pd.concat([temp_df,df],axis=0,ignore_index=True)

        pass

    df=temp_df

    temp_dict={'UF':'','Cidade':''}

    info=[l for l in temp_dict.keys()]

    resp=''

    for i,c in enumerate(info):

        dados=df[c].unique().tolist() if i==0 else df.loc[df[info[i-1]]==resp,c].unique().tolist()

        dados.sort()

        resp=gui.Menu(c,dados)

        temp_dict[c]=str(resp).lower()

        pass

    while True:

        pesquisa=input('Informe o que deseja pesquisar: ')

        if pesquisa!='':

            break

        pass

    pesquisa=f'{pesquisa} {temp_dict["Cidade"]} {temp_dict["UF"]}'


    service=Service(ChromeDriverManager().install())
    opcao=Options()

    opcao.add_argument('--start-fullscreen')

    driver=webdriver.Chrome(options=opcao,service=service)
    driver.get(link_base)

    #searchboxinput caixa de texto
    while True:

        contagem=len(driver.find_elements(By.ID,'searchboxinput'))

        if contagem>0:

            break

        pass

    campo=driver.find_element(By.ID,'searchboxinput')
    campo.send_keys(pesquisa)
    campo.send_keys(Keys.ENTER)

    #//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]

    while True:

        contagem=len(driver.find_elements(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]'))

        if contagem>0:

            break

        pass
    
    div=driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
    
    while True:
                
        pass

    pass

if __name__=='__main__':

    Main()

    pass