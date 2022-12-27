from Tempo import DataHora
from Interface import Interface
from Query import GetSQL
import getpass
import pandas as pd
from glob import glob
import os
from datetime import datetime

gui=Interface()

sql=GetSQL('MOINHO.db')

conectando=sql.Conexao()

semana={0:'SEGUNDA',1:'TERÇA',2:'QUARTA',3:'QUINTA',4:'SEXTA',5:'SÁBADO',6:'DOMINGO'}

temp_df=pd.DataFrame(data=[],columns=['Arquivo','Caminho'])

def Main(**kwargs):

    os.system('cls')

    data=DataHora()

    usuario=getpass.getuser()

    data_atual=str(data.TempoAtual())

    gui.Titulo(texto='Menu',espaco=50)

    gui.Titulo(texto=usuario,espaco=50)

    gui.Titulo(texto=data_atual,espaco=50,linha=50)

    retorno=gui.Menu(kwargs=kwargs['kwargs'])

    gui.Titulo(linha=50)

    globals().get(retorno)()

    resp=gui.Retorno('Deseja voltar a tela inicial?[s/n]: ')

    if(resp):

        Main(kwargs=kwargs['kwargs'])

        pass

    pass

def Configuracao():

    os.system('cls')

    data=DataHora()

    usuario=getpass.getuser()

    data_atual=str(data.TempoAtual())

    gui.Titulo(texto='Configuração',espaco=50)

    gui.Titulo(texto=usuario,espaco=50)

    gui.Titulo(texto=data_atual,espaco=50,linha=50)    

    submenu={1:'Mapear',2:'Temporario',3:'Cadastrar',4:'Agendar',5:'Excluir'}

    retorno=gui.Menu(kwargs=submenu)

    gui.Titulo(linha=50)

    globals().get(retorno)()

    pass

def Mapear():

    try:

        caminho=input('Informe o caminho dos arquivos: ')

        for path,dir,arq in os.walk(caminho):

            temp=[]

            for arquivo in arq:

                if(arquivo!='main.py'):

                    continue

                temp_path=os.path.join(path,arquivo)

                arq_name=os.path.basename(path)
                
                temp.append(arq_name)

                temp.append(temp_path)

                temp_df.loc[len(temp_df)]=temp
                
                pass

            pass

        print('Arquivo mapeado com sucesso!')

        pass

    except Exception as erro:

        print(f'Erro: {erro}')

        pass

    pass

def Temporario():

    print(temp_df)

    pass

def Cadastrar():

    try:

        for arq in temp_df['Caminho'].tolist():

            arq_name=str(os.path.basename(arq))

            path_name=str(arq)

            contagem=(len(path_name)-len(arq_name))-1

            path_name=os.path.basename(path_name[:contagem])

            sql.arquivo=arq

            sql.pasta=path_name

            dados=sql.BaseQuery()

            codigo=sql.GetCodigo(query=dados['Código'],connection=conectando)
            
            if(codigo==None):

                codigo=1

                pass

            else:

                codigo+=1

                pass
            
            sql.codigo=codigo

            dados=sql.BaseQuery()

            validar=sql.GetCodigo(query=dados['Validar'],connection=conectando)

            if(validar==0):

                sql.Salvar(query=dados['InserirArquivo'],connection=conectando)

                pass


            else:

                sql.Salvar(query=dados['AlterarArquivo'],connection=conectando)

                pass
            
            pass

        print('Dados salvo com sucesso!')

        pass

    except Exception as erro:

        print(f'Erro: {erro}')

        pass

    pass

def Agendar():

    try:

        while True:

            data=DataHora()

            dados=sql.BaseQuery()

            base=sql.GetDados(query=dados['ConsultaArquivo'],connection=conectando)

            temp_dict=dict()

            copy_temp=dict()

            for codigo,caminho,pasta in base:

                temp_dict[codigo]=pasta

                copy_temp[pasta]=codigo

                pass
            
            retorno=gui.Menu(kwargs=temp_dict)

            codigo=copy_temp[retorno]

            temp_dict={1:'Diário',2:'Semanal'}

            copy_temp={'Diário':1,'Semanal':2}

            retorno=gui.Menu(kwargs=temp_dict)

            tipo=retorno

            if(copy_temp[retorno]==2):

                retorno=gui.Menu(kwargs=semana)

                weekday_name=retorno

                pass

            else:

                weekday_name=''

                pass
            
            segundo=data.OpcoesTempo()

            temp_dict={0:'Data Atual',1:'Data Agendada'}

            copy_temp={'Data Atual':0,'Data Agendada':1}

            retorno=gui.Menu(kwargs=temp_dict)

            atualizador=copy_temp[retorno]

            if(atualizador==0):

                data_atual=data.TempoAtual()

                pass

            else:

                temp_dict={'hora':0,'minuto':0,'segundo':0}

                for coluna,valor in temp_dict.items():

                    resp=''

                    while not resp.isnumeric():

                        resp=input(f'Informe {coluna} com valor inteiro: ')

                        if(resp.isnumeric()):

                            resp=int(resp)

                            break

                        pass

                    temp_dict[coluna]=resp

                    pass

                data_atual=data.TempoAgendado(hora=temp_dict['hora'],minuto=temp_dict['minuto'],segundo=temp_dict['segundo'])

                pass

            dt_prox=data_atual

            sql.codigo=codigo

            sql.tipo=tipo

            sql.semana=weekday_name

            sql.tempo=segundo

            sql.atualizador=atualizador

            sql.dt_prox=dt_prox

            dados=sql.BaseQuery()

            validar=sql.GetCodigo(query=dados['ValidarConfiguracao'],connection=conectando)

            if(validar==0):

                sql.Salvar(query=dados['InserirConfiguracao'],connection=conectando)

                pass

            else:

                temp_dict={1:'Inserir',2:'Alterar'}

                retorno=gui.Menu(kwargs=temp_dict)

                if(retorno=='Inserir'):

                    sql.Salvar(query=dados['InserirConfiguracao'],connection=conectando)

                    pass


                else:

                    sql.Salvar(query=dados['AlterarConfiguracao'],connection=conectando)

                    pass

                pass

            print('Dados salvo com sucesso!')
                                    
            resp=gui.Retorno('Deseja inserir mais uma agenda?[s/n]: ')
            
            if(not resp):

                break

                pass

            pass

        pass


    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

def Voltar():

    submenu={1:'Configuracao',2:'Iniciar'}
    
    Main(kwargs=submenu)

    pass

def Excluir():

    try:

        dados=sql.BaseQuery()

        tabela=sql.GetDados(query=dados['ConsultaArquivo'],connection=conectando)

        temp_dict=dict()

        copy_temp=dict()

        for codigo,caminho,pasta in tabela:

            temp_dict[codigo]=pasta

            copy_temp[pasta]=codigo

            pass

        retorno=gui.Menu(kwargs=temp_dict)

        sql.codigo=copy_temp[retorno]

        dados=sql.BaseQuery()

        resp=gui.Retorno('Deseja excluir as informações?[s/n]: ')

        if(resp):

            sql.Salvar(query=dados['DeleteArquivo'],connection=conectando)

            sql.Salvar(query=dados['DeleteConfiguracao'],connection=conectando)

            print('Dados excluído com sucesso!')

            pass

        pass

    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

def Iniciar():

    try:

        while True:

            data=DataHora()

            os.system('cls')

            usuario=getpass.getuser()

            dt_now=str(data.TempoAtual())

            gui.Titulo(texto='Menu',espaco=50)

            gui.Titulo(texto=usuario,espaco=50)

            gui.Titulo(texto=dt_now,espaco=50,linha=50)

            dados=sql.BaseQuery()

            tabela=sql.GetDados(dados['Dados'],conectando)

            hoje=data.TempoAtual()

            for codigo,caminho,tipo,weekday,atualizar,tempo,dt_prox in tabela:

                data_retorno=datetime.strptime(dt_prox, '%Y-%m-%d %H:%M:%S')

                if(atualizar==1):

                    date=datetime.strptime(dt_prox, '%Y-%m-%d %H:%M:%S')

                    pass

                else:

                    date=data.TempoAtual()

                    pass
                
                indice=data.DiaSemana(date)
                
                if(weekday!=''):

                    if(semana[indice]==weekday):
 
                        if(hoje>=data_retorno):

                            data_atual=data.ProximoAgenda(tempo=date,segundo=tempo)
                            
                            sql.codigo=codigo

                            sql.dt_prox=data_atual   

                            dados=sql.BaseQuery()                         

                            ExecutarScript(caminho)

                            sql.Salvar(query=dados['AtualizacaoHora'],connection=conectando) 

                            pass

                        pass

                    pass

                else:

                    if(hoje>=data_retorno):

                        data_atual=data.ProximoAgenda(tempo=date,segundo=tempo)
                            
                        sql.codigo=codigo

                        sql.dt_prox=data_atual   

                        dados=sql.BaseQuery()                          

                        ExecutarScript(caminho)
                        
                        sql.Salvar(query=dados['AtualizacaoHora'],connection=conectando)                    

                        pass

                    pass

                pass

            pass

        pass

    except KeyboardInterrupt: # ctrl+c

        submenu={1:'Configuracao',2:'Iniciar'}
        
        Main(kwargs=submenu)

        pass

    pass

def ExecutarScript(caminho):

    arquivo=os.path.basename(caminho)

    path_name=str(caminho)

    contagem=(len(path_name)-len(arquivo))-1

    path_name=path_name[:contagem]

    os.chdir(path_name)

    os.system(f'python {arquivo}')

    pass

if __name__=='__main__':

    sql.CriarTabela()

    submenu={1:'Configuracao',2:'Iniciar'}
    
    Main(kwargs=submenu)

    pass