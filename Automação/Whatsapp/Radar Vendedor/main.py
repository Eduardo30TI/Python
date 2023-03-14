from selenium import webdriver
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pytesseract import pytesseract
import cv2
import time
from Acesso import Login
from Query import Query
import pandas as pd
import os
import glob
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

link_base='https://painel.targetmob.com.br/'

path_exe=r'C:\Users\eduardo\AppData\Local\Programs\Tesseract-OCR'

usuario='comercial@demarchibrasil.com.br'

senha='654321'

querys={

    'Vendedor':

    """
    
    SELECT LTRIM(RTRIM(v.[ID Vendedor])) AS [ID Vendedor],v.[Nome Resumido],s.Equipe,
	s.Supervisor,s.[DDD Sup],s.[Telefone Sup]
	,s.Gerente,s.[DDD Gerente],s.[Telefone Gerente]
    FROM netfeira.vw_vendedor v
    INNER JOIN netfeira.vw_supervisor s ON v.[ID Equipe]=s.[ID Equipe]
    WHERE Categoria='CLT' AND [Status do Vendedor]='ATIVO'
    
    """

}

def Main():

    link=f'{link_base}frmDefault.aspx'

    df=sql.CriarTabela(kwargs=querys)

    whatsapp=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    opcao=ChromeOptions()
    #opcao.add_argument('--start-fullscreen')
    opcao.add_argument('--headless=new')

    service=Service(ChromeDriverManager().install())
    driver=webdriver.Chrome(service=service,options=opcao)
    driver.maximize_window()
    driver.get(link)

    #usuário

    contagem=len(driver.find_elements(By.XPATH,'ctl00_cphPrincipal_uscLogin_txtLogin'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.XPATH,'ctl00_cphPrincipal_uscLogin_txtLogin'))
        time.sleep(1)
        tempo+=1

        if tempo>=3:

            break

        pass
    
    campo=driver.find_element(By.ID,'ctl00_cphPrincipal_uscLogin_txtLogin')
    time.sleep(3)
    campo.send_keys(usuario)
    
    #habilitar cookies
    contagem=len(driver.find_elements(By.ID,'ctl00_cphPrincipal_uscLogin_ButtonCookie'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.ID,'ctl00_cphPrincipal_uscLogin_ButtonCookie'))
        time.sleep(1)
        tempo+=1

        if tempo>=3:

            break

        pass

    botao=driver.find_element(By.ID,'ctl00_cphPrincipal_uscLogin_ButtonCookie')
    botao.click()

    #ctl00_cphPrincipal_uscLogin_txtSenha

    #senha

    contagem=len(driver.find_elements(By.XPATH,'ctl00_cphPrincipal_uscLogin_txtSenha'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.XPATH,'ctl00_cphPrincipal_uscLogin_txtSenha'))
        time.sleep(1)
        tempo+=1

        if tempo>=3:

            break

        pass
    
    campo=driver.find_element(By.ID,'ctl00_cphPrincipal_uscLogin_txtSenha')
    time.sleep(3)
    campo.send_keys(senha)

    #//*[@id="ctl00_cphPrincipal_uscLogin_btnEntrar"]

    #clicar em entrar
    contagem=len(driver.find_elements(By.XPATH,'//*[@id="ctl00_cphPrincipal_uscLogin_btnEntrar"]'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.XPATH,'//*[@id="ctl00_cphPrincipal_uscLogin_btnEntrar"]'))
        time.sleep(1)
        tempo+=1

        if tempo>=3:

            break

        pass

    botao=driver.find_element(By.XPATH,'//*[@id="ctl00_cphPrincipal_uscLogin_btnEntrar"]')
    botao.click()

    #menu
    contagem=len(driver.find_elements(By.ID,'menu'))
    tempo=0

    while contagem==0:

        contagem=len(driver.find_elements(By.ID,'menu'))
        time.sleep(1)
        tempo+=1

        if tempo>=3:

            break

        pass    

    link='https://www.paineltarget.com.br/gps/v3.4.6/index.html?opc1=Q0xJRU5URV80NTY=&opc2=MTAuMTI4LjAuMzI=&opc3='
    driver.get(link)

    #df['Vendedor']['ID Vendedor'].unique().tolist()
    for i,c in enumerate(df['Vendedor']['ID Vendedor'].unique().tolist()):

        #driver.switch_to.window(driver.window_handles[-1])

        if i>0:

            #//*[@id="RDV__lista-vendedores_filtro"]/div/div/form/div[2]/a/img
            contagem=0

            while contagem==0:

                contagem=len(driver.find_elements(By.XPATH,'//*[@id="RDV__lista-vendedores_filtro"]/div/div/form/div[2]/a/img'))
                time.sleep(1)

                pass

            click=driver.find_element(By.XPATH,'//*[@id="RDV__lista-vendedores_filtro"]/div/div/form/div[2]/a/img')
            click.click()

            pass

        #RDV__tabela
        contagem=0

        while contagem==0:

            contagem=len(driver.find_elements(By.ID,'RDV__tabela'))
            time.sleep(1)

            pass

        #RDV__tabela-vendedores
        contagem=0

        while contagem==0:

            contagem=len(driver.find_elements(By.ID,'RDV__tabela-vendedores'))
            time.sleep(1)

            pass    

        #exampleInput1
        contagem=0

        while contagem==0:

            contagem=len(driver.find_elements(By.ID,'exampleInput1'))
            time.sleep(1)

            pass

        campo=driver.find_element(By.ID,'exampleInput1')
        time.sleep(1)
        campo.send_keys(c)

        #tratar erro

        try:

            #//*[@id="RDV__tabela-vendedores"]/tr[1]/td[2]/div[1]/a
            click=driver.find_element(By.XPATH,'//*[@id="RDV__tabela-vendedores"]/tr[1]/td[2]/div[1]/a')
            click.click()

            #snackbar-container
            contagem=len(driver.find_elements(By.ID,'btn-legendas'))

            while contagem==0:

                contagem=len(driver.find_elements(By.ID,'btn-legendas'))
                time.sleep(1)

                pass
   
            time.sleep(20)
            
            temp_path=os.path.join(os.getcwd(),'Fotos')

            if not os.path.exists(temp_path):

                os.makedirs(temp_path)

                pass
            
            temp_path=os.path.join(temp_path,f'{c}.png')

            driver.save_screenshot(temp_path)

            #box-alerta
            img_alert=driver.find_element(By.CSS_SELECTOR,'section.box-alerta')
            path_img=os.path.join(os.getcwd(),f'Alerta {c}.png')
            img_alert.screenshot(path_img)

            img=cv2.imread(f'Alerta {c}.png')

            pytesseract.tesseract_cmd=path_exe +r'\tesseract.exe'
            texto=pytesseract.image_to_string(img,lang='por')

            texto=str(texto).strip()

            os.remove(path_img)

            #user-info__btn-voltar
            contagem=0

            while contagem==0:

                contagem=len(driver.find_elements(By.ID,'user-info__btn-voltar'))
                time.sleep(1)

                if contagem>0:
                    
                    break

                pass
            
            click=driver.find_element(By.ID,'user-info__btn-voltar')
            click.click()

            col_dd={'DDD Sup':'Telefone Sup','DDD Gerente':'Telefone Gerente'}

            col_nome={'DDD Sup':'Supervisor','DDD Gerente':'Gerente'}

            nome=df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==c,'Nome Resumido'].unique().tolist()[-1]

            nome=f'Vendedor(a): {c} - {nome}\nAlertas:\n\n{texto}'

            print(nome)
            
            os.system('cls')

            print(f'Mapeando Vendedor(a): {nome}')

            for key,value in col_dd.items():
                
                ddd=df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==c,key].unique().tolist()[-1]

                telefone=df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==c,value].unique().tolist()[-1]

                supervisor=df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==c,col_nome[key]].unique().tolist()[-1]
                
                whatsapp.loc[len(whatsapp)]=[supervisor,ddd,telefone,nome,temp_path]

                pass
                        
            pass

        except:

            continue
        
        #break

        pass

    whatsapp.sort_values('Vendedor',ascending=True,ignore_index=True,inplace=True)

    whatsapp.to_excel('whatsapp.xlsx',index=False,encoding='UTF-8')

    pass


if __name__=='__main__':

    data=datetime.now()

    if not data.isoweekday() in [6,7]:

        #snackbar-container

        Main()


        pass

    pass