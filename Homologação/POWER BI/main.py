from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Interface import GUI
from SQL import SQL
from Instalador import Pacote
import os
import time
from datetime import datetime

gui=GUI()

sql=SQL('MOINHO.db')

tabelas={

    'Configuração':"""
    
    CREATE TABLE IF NOT EXISTS configuracao(
    
        CODE SMALLINT NOT NULL,
        USER VARCHAR(250) NOT NULL,
        PASSWORD VARCHAR(250) NOT NULL,
        TIME SMALLINT NOT NULL,
        RETORNO SMALLIN NOT NULL

    )    
    
    """,

    'Links':"""
    
    CREATE TABLE IF NOT EXISTS links(
    
        CODE SMALLINT NOT NULL,
        DESCRICAO VARCHAR(250) NOT NULL,
        LINK TEXT NOT NULL

    )
    
    
    """
}

def Main(menu,titulo):

    os.system('cls')

    sql.CriarTabela(tabelas.values())

    res=gui.Menu(titulo,menu)

    globals().get(res)()

    resp=gui.Retorno('Deseja ao menu?[s/n]: ')

    if resp==True:

        Main(lista,titulo)

        pass


    pass

def Configuracao():

    try:

        lista=['Acesso','Link','Instalador','Visualizar','Credenciais','ExcluirLink']

        Main(lista,titulo='Configuração')

        resp=gui.Retorno('Deseja voltar as configurações?[s/n]: ')

        if resp==True:

            Main(lista,titulo='Configuração')

            pass

        pass

    except KeyboardInterrupt:

        lista=['Configuracao','Iniciar']

        Main(lista,titulo='Menu')        

        pass

    pass

def ExcluirLink():

    try:

        querys={

            'Dados':

            """
            SELECT l.CODE,l.DESCRICAO 
            FROM links l            

            """
        }


        df=sql.GetDados(querys['Dados'])

        lista=df['DESCRICAO'].unique().tolist()

        res=gui.Menu('Lista',lista)

        querys['DELETE']=f"""
        
        DELETE FROM links WHERE DESCRICAO='{res}'
        
        """

        resp=gui.Retorno('Deseja remover o link selecionado?[s/n]: ')

        if resp==True:

            sql.Salvar(querys['DELETE'])

            print('Link removido com sucesso!')

            pass

        pass


    except KeyboardInterrupt:

        lista=['Configuracao','Iniciar']

        Main(lista,titulo='Menu')

        pass

    pass

def Credenciais():

    querys={

        'Acesso':

        """
        
        SELECT * FROM configuracao
        
        """
    }

    df=sql.GetDados(querys['Acesso'])
    
    usuario=df['USER'].tolist()[-1]

    senha=df['PASSWORD'].tolist()[-1]

    tempo=df['TIME'].tolist()[-1]

    print(f'Usuário: {usuario}\nSenha: {senha}\nTempo: {tempo}')
    
    pass

def Visualizar():

    querys={

        'Link':

        """
        
        SELECT * FROM links
        
        """
    }

    df=sql.GetDados(querys['Link'])

    lista=df['DESCRICAO'].tolist()

    for i,l in enumerate(lista):

        print(f'{i+1}) {l}')

        pass

    pass

def Acesso():

    temp_dict={'Usuário':'','Senha':'','Tempo':0,'Retorno':0}

    for t in temp_dict.keys():

        val=input(f'Informe {t}: ')

        if t=='Tempo' or t=='Retorno':

            while True:

                if not val.isnumeric():

                    val=input(f'Informe {t}: ')

                    continue

                val=int(val)

                break                

                pass

            pass

        temp_dict[t]=val

        pass

    querys={

        'Validar':

        """
        
        SELECT COUNT(CODE) FROM configuracao WHERE CODE=1
        
        """
    }

    validar=sql.Codigo(querys['Validar'])

    if validar==0:

        tipo='INSERT'

        querys[tipo]=f"""
        
        INSERT INTO configuracao(CODE,USER,PASSWORD,TIME,RETORNO) VALUES({1},'{temp_dict['Usuário']}','{temp_dict['Senha']}',{temp_dict['Tempo']},{temp_dict['Retorno']})        
        
        """

        pass

    else:

        tipo='UPDATE'

        querys[tipo]=f"""
        
        UPDATE configuracao
        SET USER='{temp_dict['Usuário']}',
        PASSWORD='{temp_dict['Senha']}',
        TIME={temp_dict['Tempo']},
        RETORNO={temp_dict['Retorno']}
        WHERE CODE=1
        
        """

        pass

    sql.Salvar(querys[tipo])

    pass

def Instalador():

    Pacote.Instalador()

    pass

def Link():
    
    temp_dict=dict()
    
    querys={

        'Dados':
        
        """
    
        SELECT * FROM links
        
        """
    }

    df=sql.GetDados(querys['Dados'])

    while True:

        while True:

            nome=input('Informe o nome do link: ')

            link=input('Informe o link do BI: ')
            
            if not nome in temp_dict.keys() or not nome in df['DESCRICAO'].unique().tolist():

                break

            pass

        temp_dict[nome]=link
        
        resp=gui.Retorno('Deseja inserir mais um link?[s/n]: ')

        if resp==False:

            break

        pass

    for key,value in temp_dict.items():

        temp=f'{value}?chromeless=1'

        querys['Validar']=f"""
        
        SELECT COUNT(CODE) FROM links WHERE LINK='{temp}'
        
        """

        validar=sql.Codigo(querys['Validar'])

        if validar==0:

            tipo='INSERT'

            querys[tipo]=f"""
            
            INSERT INTO links (CODE,DESCRICAO,LINK) VALUES({validar+1},'{key}','{temp}')
            
            """

            pass


        else:

            tipo='UPDATE'

            querys[tipo]=f"""
            
            UPDATE links
            SET DESCRICAO='{key}',
            LINK='{temp}'
            WHERE LINK='{temp}'
            
            """

            pass

        sql.Salvar(querys[tipo])

        pass

    pass

def Iniciar():

    try:

        querys={

            'Link':

            """
            
            SELECT * FROM links
            
            """,

            'Acesso':

            """
            
            SELECT * FROM configuracao
            
            """
        }

        df=sql.GetDados(querys['Acesso'])

        usuario=df['USER'].tolist()[-1]

        senha=df['PASSWORD'].tolist()[-1]

        loop=df['TIME'].tolist()[-1]

        retorno=df['RETORNO'].tolist()[-1]

        link_base='https://login.microsoftonline.com/'
        
        service=Service(ChromeDriverManager().install())
        opcao=Options()
        opcao.add_argument('--start-fullscreen')

        driver=webdriver.Chrome(service=service,options=opcao)
        driver.get(link_base)
     

        for i,id in enumerate(['i0116','i0118','KmsiCheckboxField']):

            driver.window_handles[-1]

            #i0116
            contagem=len(driver.find_elements(By.ID,id))
            tempo=0

            while contagem==0:

                contagem=len(driver.find_elements(By.ID,id))
                time.sleep(1)

                tempo+=1

                if tempo>=5:

                    break

                pass

            campo=driver.find_element(By.ID,id)
            acesso=usuario if i==0 else senha

            if i!=2:
                campo.send_keys(acesso)

                pass

            else:

                campo.click()

                pass

            #idSIButton9
            contagem=len(driver.find_elements(By.ID,'idSIButton9'))
            tempo=0

            while contagem==0:

                contagem=len(driver.find_elements(By.ID,'idSIButton9'))
                time.sleep(1)

                tempo+=1

                if tempo>=5:

                    break

                pass

            botao=driver.find_element(By.ID,'idSIButton9')
            botao.click()

            time.sleep(3)

            pass

        df=sql.GetDados(querys['Link'])

        for i,link in enumerate(df['LINK'].unique().tolist()):

            driver.window_handles[-1]
            
            if i==0:

                driver.get(link)

                pass

            else:

                driver.execute_script(f"window.open('{link}');")
                driver.switch_to.window(driver.window_handles[-1])

                pass
            
            #//*[@id="pbiThemed0"]/full-screen-controls/div/span[2]/button[1]
            contagem=len(driver.find_elements(By.XPATH,'//*[@id="pbiThemed0"]/full-screen-controls/div/span[2]/button[1]'))
            tempo=0

            while contagem==0:

                contagem=len(driver.find_elements(By.XPATH,'//*[@id="pbiThemed0"]/full-screen-controls/div/span[2]/button[1]'))
                time.sleep(1)

                pass

            botao=driver.find_element(By.XPATH,'//*[@id="pbiThemed0"]/full-screen-controls/div/span[2]/button[1]')
            botao.click()

            time.sleep(2)
            
            pass

        driver.switch_to.window(driver.window_handles[0])
        
        while True:

            if datetime.now().hour<retorno:

                tabs=driver.window_handles

                for tab in tabs:

                    driver.switch_to.window(tab)
                    driver.refresh()

                    contagem=len(driver.find_elements(By.XPATH,'//*[@id="pbiThemed0"]/full-screen-controls/div/span[2]/button[1]'))

                    while contagem==0:

                        contagem=len(driver.find_elements(By.XPATH,'//*[@id="pbiThemed0"]/full-screen-controls/div/span[2]/button[1]'))
                        time.sleep(1)

                        pass

                    botao=driver.find_element(By.XPATH,'//*[@id="pbiThemed0"]/full-screen-controls/div/span[2]/button[1]')
                    botao.click()

                    time.sleep(loop)

                    pass          

                continue

            tabs=driver.window_handles

            for tab in tabs:

                driver.switch_to.window(tab)
                time.sleep(loop)

                pass

            pass

        pass

    except KeyboardInterrupt:

        lista=['Configuracao','Iniciar']

        Main(lista,titulo='Menu')      

        pass

    pass


if __name__=='__main__':

    lista=['Configuracao','Iniciar']

    Main(lista,titulo='Menu')

    pass