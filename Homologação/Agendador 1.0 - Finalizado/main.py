from Interface import GUI
from SQL import SQL
from datetime import datetime,timedelta
from Calendario import Calendario
import os
from Instalador import Pacote

sql=SQL('TARGET.db')

calend=Calendario()

gui=GUI()

tabelas={

    'Configuração':
    
    """
    
    CREATE TABLE IF NOT EXISTS configuracao(

        CODE SMALLINT NOT NULL,
        PATH TEXT NOT NULL,
        DIRNAME TEXT NOT NULL

    )
    
    """,

    'Agenda':
    
    """
    
    CREATE TABLE IF NOT EXISTS agenda(

        CODE SMALLINT NOT NULL,
        TIPO VARCHAR(250) NOT NULL,
        TIME SMALLINT NOT NULL,
        DATE VARCHAR(250) NOT NULL,
        SEQ SMALLINT NOT NULL

    )
    
    """

}

def Main():

    gui.Limpar()

    menu=['Configuracao','TestarScript','Iniciar']

    func=gui.Menu('Menu',menu)

    globals().get(func)()

    resp=gui.Retorno('Deseja voltar para o menu principal?[s/n]: ')

    if(resp):

        Main()

        pass

    pass

def Configuracao():

    try:

        gui.Limpar()

        menu=['Mapear','Lista','Salvar','Agendar','ExcluirAgenda','Excluir','ResetarBase','Consulta','Reagendar','Instalar']

        func=gui.Menu('Configuração',menu)

        globals().get(func)()

        resp=gui.Retorno('Deseja voltar para o menu de configuração?[s/n]: ')

        if(resp):

            Configuracao()

            pass

        pass

    except KeyboardInterrupt:

        Main()

        pass

    pass

def Mapear():

    caminho=''

    global list_arq

    while caminho=='':

        caminho=input('Informe o caminho do arquivo para mapear: ')

        pass

    list_arq=gui.Mapear(caminho,'main.py')
    
    pass

def Lista():

    for l in list_arq:

        print(l)

        pass

    pass

def Salvar():

    for arq in list_arq:

        temp_path=gui.GetDir(arq)

        dir_name=gui.GetArquivo(temp_path)

        querys={

            'Codigo':

            """
            
            SELECT MAX(CODE) FROM configuracao
            
            """
        }

        codigo=sql.Codigo(querys['Codigo'])

        codigo=1 if codigo==None else codigo+1

        querys['Validar']="""
        
        SELECT COUNT(CODE) FROM configuracao WHERE PATH='{0}'
        
        """.format(arq)

        validar=sql.Codigo(querys['Validar'])

        if(validar==0):

            querys['Inserir']="""
            
            INSERT INTO configuracao (CODE,DIRNAME,PATH) VALUES({0},'{1}','{2}')
            
            """.format(codigo,dir_name,arq)

            sql.Salvar(querys['Inserir'])

            pass


        else:

            querys['Alterar']="""
            
            UPDATE configuracao
            SET PATH='{1}'
            WHERE DIRNAME='{0}'
            
            """.format(dir_name,arq)

            sql.Salvar(querys['Alterar'])

            pass

        pass

    print('Dados salvo com sucesso!')

    pass

def Agendar():

    gui.Limpar()

    querys={

        'Configuracao':

        """
        
        SELECT * FROM configuracao
        
        """

    }

    df=sql.GetDados(query=querys['Configuracao'])

    menu=df['DIRNAME'].unique().tolist()

    arq=gui.Menu('Arquivos',menu)

    codigo=df['CODE'].loc[df['DIRNAME']==arq].max()
    
    tipo=['Diario','Semanal','Mensal']

    res=gui.Menu('Agenda',tipo)

    temp_dict=globals().get(res)()

    querys['Validar']=f"""
    
    SELECT COUNT(CODE) FROM agenda WHERE CODE={codigo}
    
    """

    validar=sql.Codigo(querys['Validar'])

    temp_path=df['PATH'].loc[df['DIRNAME']==arq].max()

    if(validar==0):

        querys['Inserir']=f"""
        
        INSERT INTO agenda (CODE,TIPO,TIME,DATE,SEQ) VALUES({codigo},'{temp_dict['Tipo']}',{temp_dict['Segundo']},'{temp_dict['Data']}',{validar+1}) 
        
        """

        script='Inserir'

        pass

    else:

        if(validar>=1):

            resp=gui.Retorno('Dados já consta no banco de dados deseja inserir um novo registro?[s/n]: ')

            if(resp):

                querys['Inserir']=f"""
                
                INSERT INTO agenda (CODE,TIPO,TIME,DATE,SEQ) VALUES({codigo},'{temp_dict['Tipo']}',{temp_dict['Segundo']},'{temp_dict['Data']}',{validar+1})   
                
                """

                script='Inserir'

                pass

            else:
            
                querys['Alterar']=f"""
                
                UPDATE agenda
                SET TIME={temp_dict['Segundo']},
                DATE='{temp_dict['Data']}'
                WHERE CODE={codigo} AND SEQ={validar}
                
                """

                script='Alterar'

                pass

            pass

        pass

    sql.Salvar(querys[script])
        
    resp=gui.Retorno('Deseja inserir mais uma agenda?[s/n]: ')

    if(resp):

        Agendar()

        pass

    pass

def Diario():

    opc=['Data Atual','Data Agendada']

    res=gui.Menu('Data',opc)

    if(res==opc[0]):

        data=calend.DataAtual()

        pass

    else:

        data=calend.DataAgenda()

        pass

    segundo=calend.Tempo()

    dt_prox=calend.ProxData(data=data,valor=segundo)

    temp_dict={'Data':dt_prox,'Segundo':segundo,'Tipo':'DIARIO'}

    return temp_dict
    
    pass

def Semanal():

    semanas={

        'SEG':1,
        'TER':2,
        'QUA':3,
        'QUI':4,
        'SEX':5,
        'SÁB':6,
        'DOM':7
    }

    indice=7

    opc=['Data Atual','Data Agendada']

    res=gui.Menu('Data',opc)

    if(res==opc[0]):

        data=calend.DataAtual()

        pass

    else:

        data=calend.DataAgenda()

        pass

    tipo=gui.Menu('Semanal',semanas.keys())
    
    res=(indice-data.isoweekday())+semanas[tipo]

    segundo=calend.Segundos(dias=res,opc='Dia')

    dt_prox=calend.ProxData(data=data,valor=segundo)

    segundo=calend.Segundos(dias=indice,opc='Dia')
    
    temp_dict={'Data':dt_prox,'Segundo':segundo,'Tipo':'SEMANAL'}

    return temp_dict

    pass

def Mensal():

    opc=['Data Atual','Data Agendada']

    res=gui.Menu('Data',opc)

    if(res==opc[0]):

        data=calend.DataAtual()

        pass

    else:

        data=calend.DataAgenda()

        pass

    dt_prox=calend.MesDate(data)

    temp_dict={'Data':dt_prox,'Segundo':0,'Tipo':'MENSAL'}

    return temp_dict

    pass

def Iniciar():

    try:

        path_base=os.getcwd()

        while True:

            gui.Limpar()

            querys={

                    'Dados':

                    """
                    
                    SELECT c.CODE,c.PATH,a.TIPO,a.TIME,a.DATE,a.SEQ
                    FROM configuracao c
                    INNER JOIN agenda a ON c.CODE=a.CODE
                    
                    """

                }

            df=sql.Read(query=querys['Dados']) 
            
            for codigo,path,tipo,tempo,data,seq in df:

                try:

                    arq=gui.GetArquivo(path)

                    command=(f'python {arq}')

                    dt_atual=calend.DataAtual()

                    dt_convert=datetime.strptime(data,'%Y-%m-%d %H:%M:%S')

                    script=0

                    if(tipo=='DIARIO'):

                        if(dt_atual>=dt_convert):

                            gui.ScriptExe(caminho=path,comando=command)

                            dt_prox=calend.ProxData(dt_convert,tempo)

                            script=1
                                                
                            pass

                        pass

                    elif(tipo=='SEMANAL'):

                        if(dt_atual>=dt_convert):

                            gui.ScriptExe(caminho=path,comando=command)

                            dt_prox=calend.ProxData(dt_convert,tempo)

                            script=1
                            
                            pass

                        pass

                    elif(tipo=='MENSAL'):

                        if(dt_atual>=dt_convert):

                            gui.ScriptExe(caminho=path,comando=command)

                            dt_prox=calend.MesDate(dt_convert)

                            script=1
                            
                            pass

                        pass

                    os.chdir(path_base)

                    if(script==1):
                        
                        querys['Alterar']=f"""
                        
                        
                        UPDATE agenda
                        SET DATE='{dt_prox}'
                        WHERE CODE={codigo} AND SEQ={seq}
                        
                        """
                        
                        sql.Salvar(querys['Alterar'])

                        pass

                    pass

                except:

                    continue

                pass

            #break

            pass

        pass

    except KeyboardInterrupt:

        Main()

        pass

    pass

def ExcluirAgenda():

    querys={

        'Dados':

        """
        
        SELECT c.CODE,c.PATH,c.DIRNAME,a.TIPO,a.TIME,a.DATE
        FROM configuracao c
        INNER JOIN agenda a ON c.CODE=a.CODE        
                
        """
    }

    df=sql.GetDados(querys['Dados'])

    if(len(df)>0):

        menu=df['DIRNAME'].unique().tolist()

        res=gui.Menu('Arquivos',menu)

        resp=gui.Retorno('Deseja excluir os dados da agenda?[s/n]: ')

        codigo=df['CODE'].loc[df['DIRNAME']==res].max()

        if(resp):

            querys['Delete']=f"""
            
            DELETE FROM agenda WHERE CODE={codigo}
            
            """
            
            sql.Salvar(querys['Delete'])

            pass

        pass

    else:

        pass

    pass

def Excluir():

    querys={

        'Dados':

        """
        
        SELECT c.CODE,c.PATH,c.DIRNAME,a.TIPO,a.TIME,a.DATE
        FROM configuracao c
        INNER JOIN agenda a ON c.CODE=a.CODE        
                
        """
    }

    df=sql.GetDados(querys['Dados'])

    if(len(df)>0):

        menu=df['DIRNAME'].unique().tolist()

        res=gui.Menu('Arquivos',menu)

        resp=gui.Retorno('Deseja excluir os dados da agenda?[s/n]: ')

        codigo=df['CODE'].loc[df['DIRNAME']==res].max()

        if(resp):

            querys['Delete']=f"""
            
            DELETE FROM agenda WHERE CODE={codigo}
            
            """
            
            sql.Salvar(querys['Delete'])

            querys['Delete']=f"""
            
            DELETE FROM configuracao WHERE CODE={codigo}
            
            """
            
            sql.Salvar(querys['Delete'])            

            pass

        pass

    else:

        pass

    pass

def ResetarBase(): 

    querys={

        'Dados':

        """
        
        SELECT c.CODE,c.PATH,c.DIRNAME,a.TIPO,a.TIME,a.DATE
        FROM configuracao c
        INNER JOIN agenda a ON c.CODE=a.CODE        
                
        """
    }

    df=sql.GetDados(querys['Dados'])

    if(len(df)>0):

        resp=gui.Retorno('Deseja excluir os dados da agenda?[s/n]: ')
       
        if(resp):

            querys['Delete']=f"""
            
            DELETE FROM agenda
            
            """
            
            sql.Salvar(querys['Delete'])

            querys['Delete']=f"""
            
            DELETE FROM configuracao
            
            """
            
            sql.Salvar(querys['Delete'])            

            pass

        pass

    else:

        pass

    pass

def TestarScript():

    gui.TestarScript()

    pass

def Consulta():

    querys={

        'Dados':

        """
        
        SELECT c.CODE,c.DIRNAME,a.TIPO,a.TIME,a.DATE,a.SEQ
        FROM configuracao c
        INNER JOIN agenda a ON c.CODE=a.CODE        
                
        """
    }

    df=sql.GetDados(querys['Dados'])

    print(df)

    pass

def Reagendar():

    querys={
            
        'Dados':

        """
                    
        SELECT c.CODE,c.PATH,c.DIRNAME,a.TIPO,a.TIME,a.DATE,a.SEQ
        FROM configuracao c
        INNER JOIN agenda a ON c.CODE=a.CODE   
                
        """
    }

    df=sql.GetDados(querys['Dados'])

    for i in range(0,len(df)):

        tipo=str(df['TIPO'].iloc[i]).upper()

        dt_prox=df['DATE'].iloc[i]

        seq=df['SEQ'].iloc[i]

        codigo=df['CODE'].iloc[i]

        dt_prox=calend.DateStrTime(dt_prox)

        dt_atu=calend.DataAtual()

        segundo=int(df['TIME'].iloc[i])

        if(dt_atu>=dt_prox):

            if(tipo=='DIARIO'):

                dia=(dt_atu.date()-dt_prox.date()).days

                dt_prox=calend.ProximaData(data=dt_prox,tipo=True,valor=dia)

                pass

            elif(tipo=='SEMANAL'):

                dt_prox=calend.ProxData(data=dt_prox,valor=segundo)

                pass

            else:

                dt_prox=calend.MesDate(dt_prox)

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

def Instalar():

    Pacote.Instalador()

    pass

if __name__=='__main__':

    sql.CriarTabela(tabelas.values())

    Main()

    pass