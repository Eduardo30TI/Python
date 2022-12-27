import os
import sqlite3
import time

lista=['Configuracao','Iniciar']

tabelas=["""

CREATE TABLE IF NOT EXISTS db_caminho(

    codigo INT NOT NULL PRIMARY KEY,
    caminho TEXT NOT NULL,
    tempo INT NOT NULL

)

"""]

class SQLite:
    
    def ConexaoSQL():

        try:

            conecta=sqlite3.connect('MOINHO.db')
            
            return conecta

            pass

        except:

            print('Não foi possível conectar a base de dados!')

            pass

        pass


    def CriarTabela():

        with SQLite.ConexaoSQL() as conectando:

            cursor=conectando.cursor()

            for tab in tabelas:

                cursor.execute(tab)

                pass
            
            conectando.commit()

            print('Tabela criada com sucesso!')
            
            pass

        pass

    def SaveSQL(query):

        conectando=SQLite.ConexaoSQL()

        cursor=conectando.cursor()

        cursor.execute(query)

        conectando.commit()

        print('Dados salvo com sucesso!')

        pass


    def ReadSQL(query):

        conectando=SQLite.ConexaoSQL()

        cursor=conectando.cursor()

        cursor.execute(query)

        dados=cursor.fetchall()

        return dados

        pass

    def GetCodigo(query):

        conectando=SQLite.ConexaoSQL()

        cursor=conectando.cursor()

        cursor.execute(query)

        dados=cursor.fetchone()

        for codigo in dados:

            codigo=codigo

            pass

        return int(codigo)

        pass 
    
    pass

def Mapear(caminho=''):

    if(len(caminho)<=0):

        caminho=input('Informe o caminho aonde está os arquivos: ')
        
        pass
    
    for path,dirs,arq in os.walk(caminho):

        for arquivo in arq:

            if(not arquivo.find('.py')>0):

                continue

            temp_path=os.path.join(path,arquivo)

            ExecutarScript(temp_path)

            pass

        pass

    pass

def Texto(conteudo='',linha=0,espaco=0):

    if(len(conteudo)==0 and linha>0):

        print('-'*linha)

        pass

    elif(len(conteudo)>0 and linha>0):

        print(f'{conteudo:^{espaco}}')

        print('-'*linha)

        pass

    elif(len(conteudo)>0 and linha==0):

        print(f'{conteudo:^{espaco}}')

        pass

    pass

def Menu(*args):

    os.system('cls')

    Texto('Menu Princípal',50,50)

    temp_dict=dict()

    for sub in args:

        for i,conteudo in enumerate(sub):

            i+=1

            conteudo=str(conteudo).title()

            temp_dict[i]=conteudo

            print('{0}) {1}'.format(i,conteudo))

            pass

        pass

    indice=[i for i in temp_dict.keys()]

    num=GetOpcao(indice,texto='Escolha uma das opções acima: ')

    Texto(linha=50)

    globals().get(temp_dict[num])()

    resp=GetResposta('Deseja voltar a tela principal?[s/n]: ')

    if(resp=='s'):

        Menu(lista)

        pass
    

    pass

def GetOpcao(*args,texto):

    for indice in  args:

        resp=''

        while not resp in indice:

            Texto(linha=50)

            resp=input(texto)

            if(resp.isnumeric()):

                resp=int(resp)

                if(resp in indice):

                    break

                pass

            pass
        
        pass

    return resp

    pass

def Configuracao():

    campos=['Caminho','Tempo']

    temp=[]

    query="""
    
    SELECT COUNT(*) FROM db_caminho
    
    """

    codigo=SQLite.GetCodigo(query)

    for conteudo in campos:

        valor=''

        while valor=='':

            valor=input('Informe o {0}: '.format(conteudo))

            if(valor!=''):

                break
            
            pass

        temp.append(valor)

        pass

    id=codigo+1

    querys=["""
    
    INSERT INTO db_caminho (codigo,caminho,tempo) VALUES({0},'{1}',{2})
    
    """.format(id,temp[0],temp[1]),
    """
    UPDATE db_caminho
    SET caminho='{0}',
    tempo={1}
    WHERE codigo=1
        
    """.format(temp[0],temp[1])
    
    ]

    if(codigo==0):

        SQLite.SaveSQL(querys[0])

        pass

    else:

        SQLite.SaveSQL(querys[1])

        pass

    pass

def Iniciar():

    query="""
    
    SELECT caminho,tempo FROM db_caminho WHERE codigo=1
    
    """

    dados=SQLite.ReadSQL(query)
    
    for info in dados:

        caminho,tempo=info

        pass

    contagem=tempo

    while contagem>0:

        os.system('cls')

        Texto('Processo em execução',50,50)

        print('O processo se iniciará em {0}'.format(time.ctime()))

        contagem-=1
        time.sleep(0.5)

        if(contagem<=0):

            Mapear(caminho)

            contagem=tempo
            
            pass

        pass

    pass

def ExecutarScript(caminho):

    arquivo=os.path.basename(caminho)

    temp_path=str(caminho)

    temp_path=temp_path[:temp_path.find(arquivo)]

    temp_path=temp_path[:-1]

    os.chdir(temp_path)

    print('Arquivo {0} sendo executado'.format(arquivo))

    os.system(f'python {arquivo}')

    pass

def GetResposta(texto):

    opcao=['s','n']

    resp=''

    Texto(linha=50)

    while not resp in opcao:

        resp=input(texto).lower()

        if(resp in opcao):
            
            break

        pass

    return resp

    pass

if __name__=='__main__':
    
    SQLite.CriarTabela()
    
    Menu(lista)

    pass