import pyautogui as gui
from Interface import Interface
import os
from glob import glob
from SQLite import Query
import getpass
from Tempo import DataHora
from zipfile import ZipFile
import shutil
import time


sql=Query('MOINHO.db')

data=DataHora()

instaladores={'pip':'python.exe -m pip install --upgrade pip','selenium':'pip install selenium','pyautogui':'pip install PyAutoGUI','Openpyxl':'pip install openpyxl','Pandas':'pip install pandas','Matplotlib':'pip install matplotlib','Numpy':'pip install numpy','Jupyter':'pip install jupyter','Shutil':'pip install pytest-shutil','Pyperclip':'pip install pyperclip','DriverManager':'pip install webdriver-manager'}

querys=dict()

tabelas={

    'Configuração':"""
    
    CREATE TABLE IF NOT EXISTS configuracao (

        codigo SMALLINT NOT NULL,
        tempo SMALLINT NOT NULL,
        navegador VARCHAR(250) NOT NULL,
        usuario VARCHAR(250) NOT NULL,
        senha VARCHAR(250) NOT NULL

    )
    
    """,

    'Links':"""
    
    CREATE TABLE IF NOT EXISTS links (

        codigo SMALLINT NOT NULL,
        nome VARCHAR(250) NOT NULL,
        link TEXT NOT NULL

    )    
    
    """

}

def Instalador(**kwargs):

    temp_dict=kwargs['kwargs']

    for programa in temp_dict.values():

        os.system(programa)

        programa=programa.split()

        programa=f'pip install --upgrade {programa[-1]}'

        os.system(programa)     

        pass

    pass

def Main(label,retorno=False,texto='',**kwargs):

    os.system('cls')

    temp_dict=kwargs['kwargs']

    usuario=getpass.getuser()

    data_atual=data.HoraAtual()

    hoje=f'hoje: {data_atual}'

    Interface.Titulo(texto=label,espaco=50)

    Interface.Titulo(texto=usuario,espaco=50)

    Interface.Titulo(texto=hoje,espaco=50,linha=50)

    res=Interface.Menu(temp_dict.values())

    Interface.Titulo(linha=50)

    globals().get(res)()

    if(retorno==True):

        resp=Interface.Retorno(texto=texto)

        if(resp):

            Main(label=label,retorno=retorno,texto=texto,kwargs=temp_dict)

            pass

        pass

    pass

def Configuracao():

    submenu={1:'NavegadorWeb',2:'Links',3:'DeletarLinks'}

    Main(label='Configuração',kwargs=submenu)

    pass

def NavegadorWeb():

    try:

        credenciais={'usuário':'','senha':''}

        for key,value in credenciais.items():

            value=''

            while value=='':

                value=input(f'Informe o {key}: ')

                pass

            credenciais[key]=value

            pass

        querys['Codigo']="""
        
        SELECT MAX(codigo) FROM configuracao
        
        """

        codigo=sql.Code(querys['Codigo'],sql.conectando)

        codigo=(1 if codigo==None else codigo+1)

        tipo_navegador={1:'Chrome',2:'Edge',3:'Firefox'}

        res=Interface.Menu(tipo_navegador.values())

        navegador=res

        resp=''

        while not resp.isnumeric():

            resp=input('Informe o tempo de navegação: ')

            if(resp.isnumeric()):

                resp=int(resp)

                break

                pass

            pass

        tempo=resp

        querys['Validar']="""
        
        SELECT COUNT(codigo) FROM configuracao WHERE navegador='{0}'
        
        """.format(navegador)

        validar=sql.Code(querys['Validar'],sql.conectando)

        #validar e inserção de dados no banco de dados 
        if(validar==0):

            querys['Inserir']="""
            
            INSERT INTO configuracao (codigo,tempo,navegador,usuario,senha) VALUES({0},{1},'{2}','{3}','{4}')
            
            """.format(codigo,tempo,navegador,credenciais['usuário'],credenciais['senha'])
            
            query=querys['Inserir']
            
            pass

        else:

            querys['Alterar']="""
            
            UPDATE configuracao
            SET tempo={0},
            caminho='{1}',
            usuario='{2}',
            senhha='{3}'
            WHERE navegador='{0}'
            
            """.format(tempo,navegador,credenciais['usuário'],credenciais['senha'])

            query=querys['Alterar']

            pass

        sql.Save(query,sql.conectando)

        print('Dados salvo com sucesso!')

        pass

    except Exception as erro:

        print(f'Erro: {erro}')

        pass

    pass

def CriarPasta():

    if(not os.path.exists('Webdriver')):

        temp_path=os.path.join(os.getcwd(),'Webdriver')

        os.mkdir(temp_path)        

        pass

    pass

def ExtrairZip(*args):

    for arquivo in args[0]:

        with ZipFile(arquivo,'r') as arq:

            name_arq=os.path.basename(arquivo)

            temp_path=str(arquivo)

            contagem=(len(temp_path)-len(name_arq))-1

            temp_path=temp_path[:contagem]

            arq.extractall(temp_path)

            pass

        os.remove(arquivo)

        pass
    
    pass

def Links():

    try:

        while True:

            querys['Codigo']="""
            
            SELECT MAX(codigo) FROM links
            
            """

            codigo=sql.Code(querys['Codigo'],sql.conectando)

            codigo=(1 if codigo==None else codigo+1)

            caminho=''

            while caminho=='':

                caminho=input('Informe o link do painel: ')
               
                pass

            caminho=(f'{caminho}?chromeless=true')

            nome=''

            while nome=='':

                nome=input('informe o nome do link: ')

                pass

            querys['Validar']="""
            
            SELECT COUNT(*) FROM links WHERE link='{0}'
            
            """.format(caminho)

            validar=sql.Code(querys['Validar'],sql.conectando)

            if(validar==0):

                querys['Inserir']="""
                
                INSERT INTO links(codigo,nome,link) VALUES({0},'{1}','{2}')
                
                """.format(codigo,nome,caminho)

                query=querys['Inserir']

                pass


            else:

                querys['Alterar']="""
                
                UPDATE links
                SET nome='{0}',
                link='{1}'
                WHERE link='{1}'
                
                """.format(nome,caminho)

                query=querys['Alterar']

                pass

            sql.Save(query,sql.conectando)

            print('Dados salvo com sucesso!')

            resp=Interface.Retorno('Deseja inserir mais um link?[s/n]: ')

            if(not resp):

                break

            Interface.Titulo(linha=50)

            pass

        pass

    except Exception as erro:

        print(f'Erro: {erro}')

        pass

    pass

def DeletarLinks():

    try:

        querys['Consulta']="""
        
        SELECT * FROM links
        
        """

        tabelas_df=sql.DataBase(querys=querys)

        lista=tabelas_df['Consulta']['nome'].tolist()

        res=Interface.Menu(lista)

        querys['Delete']="""
        
        DELETE FROM links WHERE nome='{0}'  
        
        """.format(res)

        Interface.Titulo(linha=50)

        resp=Interface.Retorno('Deseja excluir o link do banco de dados?[s/n]: ')
        
        if(res):

            sql.Save(querys['Delete'],sql.conectando)

            print('Deletado com sucesso!')

            pass

        pass

    except Exception as erro:

        print(f'Erro: {erro}')

        pass

    pass

def Iniciar():

    Layout()

    while True:

        data_atual=data.HoraAtual()

        hora=data_atual.hour

        if(hora==6):

            Layout()

            pass

        pass

    pass

def Layout():

    path_base=os.getcwd()

    os.chdir(path_base)

    arq=[l for l in glob('*.py') if l=='layout.py']

    os.system(f'python {arq[-1]}')

    pass


if __name__=='__main__':

    #Instalador(kwargs=instaladores)

    sql.CreateTable(tabelas.values())
    
    submenu={1:'Configuracao',2:'Iniciar'}
    
    Main(kwargs=submenu,label='Menu',retorno=True,texto='Deseja voltar a tela inicial?[s/n]: ')

    pass