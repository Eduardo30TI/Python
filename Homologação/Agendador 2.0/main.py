from Interface import GUI
from SQL import SQL
from Calendario import Datas

gui=GUI()

sql=SQL('MOINHO.db')

calend=Datas()

arquivos=[]

menu={'Configuração':'Configuracao','Testar Script':'Script','Iniciar':'Start'}

tabelas={

    'Configuracao':"""
    
    CREATE TABLE IF NOT EXISTS configuracao(
    
        CODE SMALLINT NOT NULL PRIMARY KEY,
        PATH TEXT NOT NULL

    )
    
    
    """,

    'Scripts':

    """
    
    CREATE TABLE IF NOT EXISTS scripts(
    
        CODE SMALLINT NOT NULL,
        DIRNAME VARCHAR(250) NOT NULL,
        PATH TEXT NOT NULL

    )
    
    """,

    'Agenda':"""
    
    CREATE TABLE IF NOT EXISTS agenda(
        
        CODE SMALLINT NOT NULL,
        TIME SMALLINT NOT NULL,
        SEQ SMALLINT NOT NULL,
        TIPO VARCHAR(250) NOT NULL,
        DATE VARCHAR(250) NOT NULL

    )
    
    
    """

}

def Main(menu: dict,label: str,retorno=False,texto=''):

    gui.Cls()

    path_base=gui.GetCWD()

    gui.Chdir(path_base)

    sql.CreateTable(querys=tabelas.values())

    usuario=gui.GetUser()

    dt_atual=calend.DataStr(calend.DataAtual())

    gui.Titulo(label,50,0)

    gui.Titulo(usuario,50,0)

    gui.Titulo(dt_atual,50,50)

    res=gui.Menu(menu.keys())

    globals().get(menu[res])()

    if retorno==True:

        resp=gui.Retorno(texto)

        if resp:

            Main(menu,label,retorno,texto)

            pass

        pass

    pass

def Configuracao():

    config={'Configurar Ambiente':'ConfigAmbiente','Mapear':'Mapear','Lista Temporária':'Verificar','Salvar':'Salvar','Agendar Script':'Agendar','Excluir Agenda':'ExcluirAgenda','Resetar Database':'Reset','Reagendar Script':'Reagendar','Consultar Agenda':'Consultar','Voltar':'Voltar'}

    Main(config,'Configuração',True,'Deseja voltar para as configurações?[s/n]: ')

    pass

def Voltar():

    Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

    pass

def ConfigAmbiente():

    try:

        path_base=gui.GetCWD()

        gui.Chdir(path_base)

        querys={

            'Validar':

            """

            SELECT COUNT(CODE) FROM configuracao WHERE CODE=1        
            
            """
        }

        while True:

            caminho=input('Informe o caminho: ')

            res=gui.PathExists(caminho)

            if res==True:
                
                break

            pass

        validar=sql.Codigo(querys['Validar'])

        if validar==0:

            tipo='INSERT'

            querys[tipo]=f"""
            
            INSERT INTO configuracao(CODE,PATH) VALUES({validar+1},'{caminho}')        
            
            """

            pass


        else:

            tipo='UPDATE'

            querys[tipo]=f"""
            
            UPDATE configuracao
            SET PATH='{caminho}'
            WHERE CODE=1
            
            """

            pass


        sql.Salve(querys[tipo])

        print('Caminho base salvo com sucesso!')

        pass

    except KeyboardInterrupt:

        Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

        pass

    pass

def Mapear():

    try:

        path_base=gui.GetCWD()

        gui.Chdir(path_base)    

        querys={

            'Consulta':

            """
            
            SELECT * FROM configuracao
            
            """
        }

        df=sql.GetDados(querys)

        caminho=df['Consulta']['PATH'].unique().tolist()[-1]

        while True:

            tipo=input('Informe o tipo de arquivo: ')

            tipo=f'*{tipo}'

            if tipo!='':

                break

            pass

        global arquivos

        arquivos=gui.MapArq(caminho,tipo)

        print('Arquivos mapeados')

        pass

    except KeyboardInterrupt:

        Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

        pass

    pass

def Verificar():

    try:

        for i,arq in enumerate(arquivos):

            nome=gui.BaseName(gui.PathDir(arq))

            print(f'{i+1}) {nome}')

            pass

        pass

    except KeyboardInterrupt:

        Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

        pass

    pass

def Agendar():

    try:

        gui.Cls()

        path_base=gui.GetCWD()

        gui.Chdir(path_base)

        querys={

            'Scripts':

            """
            
            SELECT * FROM scripts
            
            """
        }

        gui.Titulo('Agenda',50,50)

        df=sql.GetDados(querys)

        lista=df['Scripts']['DIRNAME'].unique().tolist()

        res=gui.Menu(lista)

        codigo=df['Scripts'].loc[df['Scripts']['DIRNAME']==res,'CODE'].unique().tolist()[-1]

        opc=['Mensal','Semanal','Diário','Hora','Minuto','Segundo']

        semanas={'Segunda':1,'Terça':2,'Quarta':3,'Quinta':4,'Sexta':5,'Sábado':6,'Domingo':7}

        res=gui.Menu(opc)

        tipo=res

        if tipo=='Semanal':

            res=gui.Menu(semanas)

            id_week=semanas[res]

            pass

        num=0

        if not tipo in ['Mensal','Semanal']:

            while True:

                num=input('Informe um valor inteiro: ')

                if num.isnumeric():

                    num=int(num)

                    break

                pass

            pass

        resp=gui.Retorno('Deseja escolher uma data?[s/n]: ')

        dt_atual=calend.DataAgendada() if resp==True else calend.DataAgendada(hoje=True)

        if tipo=='Semanal':

            num=id_week

            pass

        num=num if not tipo in ['Hora','Minuto','Segundo'] else calend.Segundo(num,tipo)

        dt_prox=calend.Calcular(data=dt_atual,tipo=tipo,valor=num)

        querys['Validar']=f"""
        
        SELECT COUNT(*) FROM agenda WHERE CODE={codigo}
        
        """

        validar=sql.Codigo(querys['Validar'])

        if validar==0:

            filtro='INSERT'

            querys[filtro]=f"""
            
            INSERT INTO agenda (CODE,TIME,SEQ,TIPO,DATE) VALUES({codigo},{num},{validar+1},'{tipo}','{dt_prox}')
                        
            """

            pass


        else:

            resp=gui.Retorno('Dados já consta no banco de dados deseja inserir uma nova linha?[s/n]: ')

            if resp==True:

                filtro='INSERT'

                querys[filtro]=f"""
                
                INSERT INTO agenda (CODE,TIME,SEQ,TIPO,DATE) VALUES({codigo},{num},{validar+1},'{tipo}','{dt_prox}')
                            
                """

                pass


            else:

                querys['Agenda']="""
                
                SELECT * FROM agenda
                
                """

                df=sql.GetDados(querys)

                sequencias=df['Agenda'].loc[df['Agenda']['CODE']==codigo,'SEQ'].unique().tolist()

                seq=gui.Menu(sequencias)

                filtro='UPDATE'

                querys[filtro]=f"""
                
                UPDATE agenda
                SET TIME={num},
                TIPO='{tipo}',
                DATE='{dt_prox}'
                WHERE CODE={codigo} AND SEQ={seq}
                
                """

                pass

            pass

        sql.Salve(querys[filtro])

        print('Dados salvo com sucesso!')

        pass

    except KeyboardInterrupt:

        Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

        pass

    pass

def Salvar():

    try:

        path_base=gui.GetCWD()

        gui.Chdir(path_base)

        for arq in arquivos:

            dirname=gui.BaseName(gui.PathDir(arq))

            querys={

                'Validar':f"""
                
                SELECT COUNT(*) FROM scripts WHERE DIRNAME='{dirname}'
                
                """,

                'Codigo':"""
                
                SELECT COUNT(*)+1 FROM scripts
                
                """,
                
                'Scripts':"""
                
                SELECT * FROM scripts
                
                """
            }

            validar=sql.Codigo(querys['Validar'])

            codigo=sql.Codigo(querys['Codigo'])

            if validar==0:

                tipo='INSERT'

                querys[tipo]=f"""
                
                INSERT INTO scripts(CODE,DIRNAME,PATH) VALUES({codigo},'{dirname}','{arq}')                
                
                """

                pass


            else:

                df=sql.GetDados(querys)

                codigo=df['Scripts'].loc[df['Scripts']['DIRNAME']==dirname,'CODE'].max()

                tipo='UPDATE'

                querys[tipo]=f"""
                
                UPDATE scripts
                SET DIRNAME='{dirname}',
                PATH='{arq}'
                WHERE CODE={codigo}
                
                """

                pass

            sql.Salve(querys[tipo])

            pass

        print('Salvo com sucesso!')

        pass

    except KeyboardInterrupt:

        Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

        pass
    
    pass

def ExcluirAgenda():

    path_base=gui.GetCWD()

    gui.Chdir(path_base)

    querys={

        'Dados':

        """

        SELECT s.CODE,s.DIRNAME,s.PATH,a.TIME,a.SEQ,a.TIPO,a.DATE
        FROM scripts s
        INNER JOIN agenda a ON s.CODE=a.CODE
        
        """
    }

    df=sql.GetDados(querys)

    temp=df['Dados']['DIRNAME'].unique().tolist()

    res=gui.Menu(temp)
    
    codigo=df['Dados'].loc[df['Dados']['DIRNAME']==res,'CODE'].unique().tolist()[-1]

    temp=df['Dados'].loc[df['Dados']['DIRNAME']==res,'SEQ'].unique().tolist()
    
    seq=gui.Menu(temp)

    querys['DELETE']=f"""
    
    DELETE FROM agenda WHERE CODE={codigo} AND SEQ={seq}
    
    """

    resp=gui.Retorno('Deseja remover a agenda?[s/n]: ')

    if resp==True:

        sql.Salve(querys['DELETE'])

        pass

    print('Agenda exlcuída com sucesso!')

    pass

def Reset():

    path_base=gui.GetCWD()

    gui.Chdir(path_base)

    querys={

        'Configuracao':

        """
        
        DELETE FROM configuracao
        
        """,

        'Scripts':

        """
        
        DELETE FROM scripts
        
        """,

        'Agenda':

        """
        
        DELETE FROM agenda
        
        """
    }

    resp=gui.Retorno('Deseja resetar o banco de dados?[s/n]: ')

    if resp==True:

        for query in querys.values():

            sql.Salve(query)

            pass

        pass

    print('Banco de dados resetado com sucesso!')

    pass

def Reagendar():

    try:

        path_base=gui.GetCWD()

        gui.Chdir(path_base)

        querys={

            'Agenda':

            """
            
            SELECT * FROM agenda
            
            """
        }

        df=sql.GetDados(querys)

        for i in range(0,len(df['Agenda'])):
            
            codigo=df['Agenda'].loc[i,'CODE']

            tipo=df['Agenda'].loc[i,'TIPO']

            time=df['Agenda'].loc[i,'TIME']

            seq=df['Agenda'].loc[i,'SEQ']

            dt_atual=df['Agenda'].loc[i,'DATE']

            dt_atual=calend.ConverterData(dt_atual)

            dt_prox=calend.Calcular(dt_atual,tipo,time)

            querys['UPDATE']=f"""
            
            UPDATE agenda
            SET DATE='{dt_prox}'
            WHERE CODE={codigo} AND SEQ={seq}        
            
            """

            dt_hoje=calend.DataAtual()

            if dt_hoje>dt_atual:

                sql.Salve(querys['UPDATE'])

                pass

            pass

        pass

    except Exception as erro:

        print(erro)

        pass

    pass

def Consultar():

    try:

        path_base=gui.GetCWD()

        gui.Chdir(path_base)    

        querys={

            'Dados':

            """

            SELECT s.CODE,s.DIRNAME,s.PATH,a.TIME,a.SEQ,a.TIPO,a.DATE
            FROM scripts s
            INNER JOIN agenda a ON s.CODE=a.CODE
            
            """
        }


        df=sql.GetDados(querys)

        temp=df['Dados']['DIRNAME'].unique().tolist()
        
        res=gui.Menu(temp)

        print(df['Dados'].loc[df['Dados']['DIRNAME']==res])

        pass

    except KeyboardInterrupt:

        Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

        pass  

    pass

def Start():

    try:

        while True:

            path_base=gui.GetCWD()

            gui.Chdir(path_base)

            querys={

                'Dados':

                """

                SELECT s.CODE,s.DIRNAME,s.PATH,a.TIME,a.SEQ,a.TIPO,a.DATE
                FROM scripts s
                INNER JOIN agenda a ON s.CODE=a.CODE
                
                """
            }

            df=sql.GetDados(querys)

            for i in range(0,len(df['Dados'])):

                path_arq=df['Dados'].loc[i,'PATH']

                time=df['Dados'].loc[i,'TIME']

                seq=df['Dados'].loc[i,'SEQ']

                tipo=df['Dados'].loc[i,'TIPO']

                dt_atual=df['Dados'].loc[i,'DATE']

                codigo=df['Dados'].loc[i,'CODE']

                dt_atual=calend.ConverterData(dt_atual)

                dt_hoje=calend.DataAtual()

                if dt_atual>dt_hoje:

                    continue

                dt_prox=calend.Calcular(dt_atual,tipo,time)

                querys['UPDATE']=f"""
                
                UPDATE agenda
                SET DATE='{dt_prox}'
                WHERE CODE={codigo} AND SEQ={seq}         
                
                """

                nome_arq=gui.BaseName(gui.PathDir(path_arq))

                gui.Cls()

                print(f'Executando o arquivo: {nome_arq}. Aguarde...')

                gui.ExecuteScript(path_arq,path_base)

                sql.Salve(querys['UPDATE'])

                pass           

            pass

        pass

    except KeyboardInterrupt:

        Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

        pass

    pass

def Script():

    try:

        path_base=gui.GetCWD()

        gui.Chdir(path_base)

        while True:

            caminho=input('Informe o caminho: ')

            if caminho!='':

                break

            pass
        
        res=gui.PathExists(caminho)

        if res==True:

            while True:

                tipo=input('Informe o tipo de arquivo que deseja: ')

                if tipo!='':

                    break

                pass

            tipo=f'*{tipo}'

            arquivos=gui.Arquivos(caminho,tipo)

            gui.ExecuteScript(arquivos[-1],path_base)
            
            pass

        else:

            Script()

            pass

        pass


    except KeyboardInterrupt:

        #Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

        print('Erro')

        pass

    pass

if __name__=='__main__':
    
    Main(menu,'Menu',True,'Deseja voltar para o menu?[s/n]: ')

    pass