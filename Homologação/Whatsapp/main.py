from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import urllib
import time
from Interface import GUI
from SQL import SQL
from Calendario import Calendario

calend=Calendario()

gui=GUI()

sql=SQL('MOINHO.db')

tabelas={

    'Configuracao':

    """
    
    CREATE TABLE IF NOT EXISTS configuracao (

        CODE SMALLINT NOT NULL,
        PATH TEXT NOT NULL,
        DIR VARCHAR(250) NOT NULL

    )
    
    """,

    'Agenda':

    """

    CREATE TABLE IF NOT EXISTS agenda (

        CODE SMALLINT NOT NULL,
        SEQ SMALLINT NOT NULL,
        TIME SMALLINT NOT NULL,
        DATE VARCHAR(250) NOT NULL,
        TIPO VARCHAR(250) NOT NULL

    )
    
    
    """,

    'Base':

    """
    
    CREATE TABLE IF NOT EXISTS base (

        CODE SMALLINT NOT NULL,
        PATH TEXT NOT NULL

    )
    
    """

}

def Main():

    try:
    
        CriarDir()

        menu=['Configurar','Iniciar']

        gui.Cls()

        res=gui.Menu('Menu',menu)

        globals().get(res)()

        res=gui.Retorno('Deseja voltar para o menu?[s/n]: ')

        if(res):

            Main()

            pass

        pass

    except KeyboardInterrupt:

        Main()

        pass
  
    pass

def Configurar():

    gui.Cls()

    menu=['Mapear','Arquivos','Salvar','Agendar','DeletarAgenda','Resetar','Base','VisualizarConfig','VisualizarAgenda','Reagendar']

    res=gui.Menu('Configuração',menu)

    globals().get(res)()
    
    res=gui.Retorno('Deseja voltar para as configurações?[s/n]: ')

    if(res):

        Configurar()

        pass

    pass

def Iniciar():

    try:

        Whatsapp()

        pass

    except KeyboardInterrupt:

        Main()

        pass

    pass

def Mapear():

    path=path_geral

    global temp

    temp=gui.MapearArq(caminho=path,tipo='main.py')

    pass

def Arquivos():

    for i,path in enumerate(temp):

        i+=1

        print(f'{i}) {path}')

        pass

    pass

def Base():

    querys={

        'Valiar':

        """
        
        SELECT COUNT(CODE) FROM base WHERE CODE=1
        
        """

    }

    while True:

        path=input('Informe o caminho: ')

        if(gui.GetExists(path)):
            
            break

        pass

    validar=sql.Validar(querys['Valiar'])

    if(validar==0):

        info='INSERT'

        querys[info]=f"""
        
        INSERT INTO base (CODE,PATH) VALUES({validar+1},'{path}')
        
        """

        pass

    else:

        info='UPDATE'

        querys[info]=f"""
        
        UPDATE base
        SET PATH='{path}'
        WHERE CODE=1
        
        """

        pass


    sql.Salvar(querys[info])

    CriarDir()

    pass

def VisualizarConfig():

    querys={

        'Dados':

        """
        
        SELECT * FROM base
        
        """
    }

    df=sql.GetDados(kwargs=querys)

    print(df['Dados'])

    pass

def Salvar():

    querys=dict()

    for path in temp:

        dir_name=gui.GetArq(gui.GetDir(path))

        querys['Validar']=f"""
        
        SELECT COUNT(*) FROM configuracao WHERE DIR='{dir_name}'
                
        """

        validar=sql.Validar(querys['Validar'])

        querys['Codigo']="""
        
        SELECT MAX(CODE) FROM configuracao
        
        """

        codigo=sql.Validar(querys['Codigo'])

        codigo=codigo+1 if codigo!=None else 1
        
        if(validar==0):

            info='INSERT'

            querys[info]=f"""
            
            INSERT INTO configuracao (CODE,PATH,DIR) VALUES({codigo},'{path}','{dir_name}')
            
            """

            pass

        else:

            info='UPDATE'

            querys[info]=f"""
            
            UPDATE configuracao
            SET PATH='{path}'
            WHERE DIR='{dir_name}'
            
            """

            pass

        sql.Salvar(querys[info])

        pass

    print('Dados salvo com sucesso!')

    pass

def Resetar():

    querys={

        'Configuracao':

        """

        DELETE FROM configuracao
        
        """,

        'Agenda':

        """
        
        DELETE FROM agenda
        
        """
    }

    resp=gui.Retorno('Deseja resetar o banco de dados?[s/n]: ')

    if(resp):

        for query in querys.values():

            sql.Salvar(query)

            pass

        print('Banco de dados resetado com sucesso!')

        pass

    pass

def Agendar():

    gui.Cls()

    querys={

        'Dados':

        """
        
        SELECT * FROM configuracao
        
        """
    }

    df=sql.GetDados(kwargs=querys)

    temp=df['Dados']['DIR'].unique().tolist()

    dirname=gui.Menu('Agenda',temp)

    codigo=df['Dados']['CODE'].loc[df['Dados']['DIR']==dirname].max()

    menu=['Mensal','Semanal','Diario']

    res=gui.Menu('Agenda',menu)

    temp_dict=globals().get(res)()
    
    querys['Codigo']=f"""
    
    SELECT COUNT(SEQ) FROM agenda WHERE CODE={codigo} 
    
    """

    seq=sql.Validar(querys['Codigo'])

    tipo=str(res).upper()

    if(seq==0):

        info='INSERT'

        querys[info]=f"""
        
        INSERT INTO agenda (CODE,SEQ,TIME,DATE,TIPO) VALUES({codigo},{seq+1},{temp_dict['Segundo']},'{temp_dict['Data']}','{tipo}')
        
        """

        pass

    else:

        resp=gui.Retorno('Dados já consta cadastrado no banco de dados deseja inserir mais uma linha?[s/n]: ')

        if(resp==True):

            info='INSERT'

            querys[info]=f"""
            
            INSERT INTO agenda (CODE,SEQ,TIME,DATE,TIPO) VALUES({codigo},{seq+1},{temp_dict['Segundo']},'{temp_dict['Data']}','{tipo}')
            
            """

            pass

        else:

            querys['Agenda']="""
            
            SELECT c.CODE,c.DIR,a.TIPO,a.TIME,a.DATE,a.SEQ
            FROM configuracao c
            INNER JOIN agenda a ON c.CODE=a.CODE
            
            """

            df=sql.GetDados(kwargs=querys)

            temp=df['Agenda']['DIR'].unique().tolist()
            
            temp=df['Agenda']['SEQ'].loc[df['Agenda']['DIR']==dirname].unique().tolist()

            seq=temp[-1] if len(temp)<=1 else gui.Menu('Arquivo',temp)      

            info='UPDATE'

            querys[info]=f"""
            
            UPDATE agenda
            SET TIME={temp_dict['Segundo']},
            DATE='{temp_dict['Data']}',
            TIPO='{tipo}'
            WHERE CODE={codigo} AND SEQ={seq}
            
            """

            pass
        

        pass

    sql.Salvar(querys[info])

    print('Dados salvo com sucesso!')

    pass

def Mensal():

    data=calend.DataAgendada()

    dt_prox=calend.DataMensal(data)

    temp_dict={'Data':dt_prox,'Segundo':0}

    return temp_dict

    pass

def Semanal():

    semanas={'SEG':1,'TER':2,'QUA':3,'QUI':4,'SEX':5,'SÁB':6,'DOM':7}

    indice=7

    res=gui.Menu('Semanal',semanas)

    dt_prox=calend.DataAgendada()

    num=semanas[res]-1
    
    dt_prox=calend.ProximaData(data=dt_prox,tipo=True,valor=num)

    segundo=calend.GetSegundo()

    temp_dict={'Data':dt_prox,'Segundo':segundo}

    return temp_dict

    pass

def Diario():

    dt_prox=calend.DataAgendada()

    segundo=calend.GetSegundo()

    dt_prox=calend.ProximaData(data=dt_prox,tipo=True,valor=1)

    temp_dict={'Data':dt_prox,'Segundo':segundo}

    return temp_dict

    pass

def CriarDir():

    try:

        global path_geral

        querys={

            'Base':

            """
            
            SELECT PATH FROM base
            
            """
        }

        path=sql.Validar(query=querys['Base'])

        path_geral=gui.UnirPath(path,'Script Python')
        
        gui.CreateDir(path_geral)

        pass

    except:

        pass

    pass

def VisualizarAgenda():

    while True:

        gui.Cls()

        querys={

            'Dados':

            """
            
            SELECT c.CODE,c.DIR,a.TIPO,a.TIME,a.DATE,a.SEQ
            FROM configuracao c
            INNER JOIN agenda a ON c.CODE=a.CODE        
            
            """
        }

        df=sql.GetDados(kwargs=querys)

        temp=df['Dados']['DIR'].unique().tolist()

        res=gui.Menu('Diretório',temp)

        print(df['Dados'].loc[df['Dados']['DIR']==res])

        resp=gui.Retorno('Deseja consultar novamente?[s/n]: ')

        if(not resp):

            break

        pass

    pass

def DeletarAgenda():

    querys={

        'Dados':

        """
        
        SELECT c.CODE,c.PATH,c.DIR,a.TIPO,a.TIME,a.DATE,a.SEQ
        FROM configuracao c
        INNER JOIN agenda a ON c.CODE=a.CODE        
        
        """
    }

    df=sql.GetDados(kwargs=querys)

    temp=df['Dados']['DIR'].unique().tolist()

    dir=gui.Menu('Diretório',temp)

    temp=df['Dados']['SEQ'].loc[df['Dados']['DIR']==dir].unique().tolist()

    seq=gui.Menu('Sequência de execução',temp)

    print(df['Dados'].loc[(df['Dados']['DIR']==dir)&(df['Dados']['SEQ']==seq)])

    codigo=df['Dados']['CODE'].loc[(df['Dados']['DIR']==dir)&(df['Dados']['SEQ']==seq)].tolist()[-1]

    querys['DELETE']=f"""
    
    DELETE FROM agenda
    WHERE CODE={codigo} AND SEQ={seq}
    
    """

    resp=gui.Retorno('Deseja realmente excluir os dados da agenda?[s/n]: ')

    if(resp):

        sql.Salvar(querys['DELETE'])

        print('Dados excluído com sucesso!')

        pass
    
    pass

def Whatsapp():

    link='https://web.whatsapp.com/'

    opc=['DIARIO','SEMANAL']
    
    service=Service(ChromeDriverManager().install())
    options=ChromeOptions()

    profile=gui.UnirPath(gui.GetPath(),'profile')
    profile=gui.UnirPath(profile,'wpp')
    options.add_argument(r'user-data-dir={}'.format(profile))

    driver=webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get(link)

    while True:

        path_base=gui.GetPath()

        gui.Chdir(path_base)

        querys={
            
            'Dados':

            """
                
            SELECT c.CODE,c.PATH,c.DIR,a.TIPO,a.TIME,a.DATE,a.SEQ
            FROM configuracao c
            INNER JOIN agenda a ON c.CODE=a.CODE        
            
            """
        }       
        
        contagem=len(driver.find_elements(By.ID,'pane-side'))

        if(contagem<=0):

            continue
            
        df=sql.GetDados(kwargs=querys)

        scripts=df['Dados']['PATH'].tolist()

        #executar os script python
        for i,script in enumerate(scripts):

            dt_atual=calend.DataAtual()

            dt_prox=df['Dados']['DATE'].loc[df['Dados'].index==i].tolist()[-1]

            codigo=df['Dados']['CODE'].loc[df['Dados'].index==i].tolist()[-1]

            seq=df['Dados']['SEQ'].loc[df['Dados'].index==i].tolist()[-1]

            segundos=df['Dados']['TIME'].loc[df['Dados'].index==i].tolist()[-1]

            tipo=str(df['Dados']['TIPO'].loc[df['Dados'].index==i].tolist()[-1]).upper()

            dt_prox=calend.DateStrTime(dt_prox)

            if(dt_atual>=dt_prox):

                dt_prox=calend.ProximaData(dt_prox,False,segundos) if tipo in opc else calend.DataMensal(dt_prox)

                querys['UPDATE']=f"""
                
                UPDATE agenda
                SET DATE='{dt_prox}'
                WHERE CODE={codigo} AND SEQ={seq}
                
                """
                
                gui.ExecutarScript(script)

                gui.Chdir(path_base)

                path_dir=gui.PathDir(script)

                arquivos=gui.Arquivos(path_dir,'whatsapp.xlsx')

                if(len(arquivos)<=0):

                    continue

                excel=sql.Excel(arquivos[-1])

                for i in range(0,len(excel)):

                    try:

                        ddd=excel['DDD'].loc[excel.index==i].tolist()[-1]

                        telefone=excel['Telefone'].loc[excel.index==i].tolist()[-1]

                        mensagem=str(excel['Mensagens'].loc[excel.index==i].tolist()[-1]).strip()

                        paths=excel['Path'].loc[(excel.index==i)&(~excel['Path'].isnull())].tolist()

                        tel_format=f'55{ddd}{telefone}'

                        text_format=urllib.parse.quote(mensagem)

                        link_api=f'{link}send?phone={tel_format}&text={text_format}'

                        driver.get(link_api)

                        contagem=len(driver.find_elements(By.CSS_SELECTOR,'p.selectable-text.copyable-text'))
                        tempo=0

                        while contagem==0:

                            contagem=len(driver.find_elements(By.CSS_SELECTOR,'p.selectable-text.copyable-text'))
                            time.sleep(1)
                            
                            erro=len(driver.find_elements(By.CLASS_NAME,'_3J6wB'))

                            block=len(driver.find_elements(By.XPATH,'//*[@id="main"]/footer/div'))

                            if(erro>0 or block>0):

                                break
                            
                            pass
                        
                        try:

                            if(len(paths)>0):

                                click=driver.find_element(By.CSS_SELECTOR,'span[data-icon="clip"]')
                                click.click()
                                #inserir arquivo
                                anexo=driver.find_element(By.CSS_SELECTOR,'input[type="file"]')
                                time.sleep(2)
                                anexo.send_keys(paths[-1])
                                time.sleep(3)
                                driver.window_handles[-1]                    

                                pass

                            contagem=len(driver.find_elements(By.CSS_SELECTOR,'p.selectable-text.copyable-text'))
                            tempo=0

                            while contagem==0:

                                contagem=len(driver.find_elements(By.CSS_SELECTOR,'p.selectable-text.copyable-text'))
                                time.sleep(1)

                                erro=len(driver.find_elements(By.CLASS_NAME,'_3J6wB'))

                                block=len(driver.find_elements(By.XPATH,'//*[@id="main"]/footer/div'))

                                if(erro>0 or block>0):

                                    break                        

                                pass

                            campo=driver.find_element(By.CSS_SELECTOR,'p.selectable-text.copyable-text')
                            campo.send_keys(Keys.ENTER)

                            time.sleep(3)

                            pass

                        except:

                            continue

                        pass

                    except:

                        continue
                    
                    pass

                #salvar alterações

                sql.Salvar(querys['UPDATE'])                

                pass

            temp_path=gui.PathDir(script)

            gui.RemoverArquivo(temp_path,'.xlsx')        

            pass
        
        pass

    pass

def Reagendar():

    querys={
            
        'Dados':

        """
                    
        SELECT c.CODE,c.PATH,c.DIR,a.TIPO,a.TIME,a.DATE,a.SEQ
        FROM configuracao c
        INNER JOIN agenda a ON c.CODE=a.CODE        
                
        """
    }

    df=sql.GetDados(kwargs=querys)

    for i in range(0,len(df['Dados'])):

        tipo=str(df['Dados']['TIPO'].iloc[i]).upper()

        dt_prox=df['Dados']['DATE'].iloc[i]

        seq=df['Dados']['SEQ'].iloc[i]

        codigo=df['Dados']['CODE'].iloc[i]

        dt_prox=calend.DateStrTime(dt_prox)

        dt_atu=calend.DataAtual()

        segundo=int(df['Dados']['TIME'].iloc[i])

        if(dt_atu>=dt_prox):

            if(tipo=='DIARIO'):

                dia=(dt_atu.date()-dt_prox.date()).days

                dt_prox=calend.ProximaData(data=dt_prox,tipo=True,valor=dia)

                pass

            elif(tipo=='SEMANAL'):

                dt_prox=calend.ProximaData(data=dt_prox,tipo=False,valor=segundo)

                pass

            else:

                dt_prox=calend.DataMensal(dt_prox)

                pass
            
            querys['UPDATE']=f"""
            
            UPDATE agenda
            SET DATE='{dt_prox}'
            WHERE CODE={codigo} AND SEQ={seq}            
            
            """

            sql.Salvar(querys['UPDATE'])

            pass

        pass

    print('Dados reagendados.')

    pass

if __name__=='__main__':

    sql.CriarTabela(kwargs=tabelas)

    Main()

    pass