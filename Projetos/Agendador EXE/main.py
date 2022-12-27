from SQLITE import SQLConexao
from Tempo import DataHora
from Interface import Interface
import os
import getpass
from datetime import datetime


sql=SQLConexao('MOINHO.db')

temp_lista=[]

conectando=sql.Conexao()

tabela={

    'arquivos':"""
    
    
    CREATE TABLE IF NOT EXISTS arquivos (

        codigo SMALLINT NOT NULL,
        caminho TEXT NOT NULL

    )
    
    """,

    'configuracao':"""
    
    CREATE TABLE IF NOT EXISTS configuracao(

        codigo SMALLINT NOT NULL,
        tipo VARCHAR(250) NOT NULL,
        dt_hora VARCHAR(250) NOT NULL,
        semana VARCHAR(250) NULL,
        tempo SMALLINT NOT NULL,
        prox_data VARCHAR(250) NOT NULL

    )
    
    """


}

def CriarTabela():

    for tab in tabela.values():

        sql.Salvar(query=tab,conectando=conectando)

        pass

    pass

def Main():

    os.system('cls')

    usuario=getpass.getuser()

    temp=['Configuracao','TestarArquivo','Iniciar']

    Interface.Titulo(texto='Menu',espaco=50)

    Interface.Titulo(texto=usuario,espaco=50,linha=50)

    indice=Interface.Menu(temp)

    Interface.Titulo(linha=50)

    globals().get(indice)()

    resp=Interface.Retorno('Deseja voltar ao menu principal?[s/n]: ')

    if(resp):

        Main()

        pass

    pass

def Configuracao():

    os.system('cls')

    usuario=getpass.getuser()

    temp=['Mapear','SalvarArquivo','Atualizacao','ExcluirArquivo','Sair']

    Interface.Titulo(texto='Configuração',espaco=50)

    Interface.Titulo(texto=usuario,espaco=50,linha=50)

    indice=Interface.Menu(temp)

    Interface.Titulo(linha=50)

    globals().get(indice)()

    resp=Interface.Retorno('Deseja voltar as configurações?[s/n]: ')

    if(resp):

        Configuracao()

        pass    

    pass

def Sair():

    Main()

    pass

def Mapear():

    try:

        caminho=input('Informe o caminho onde está o arquivo: ')

        for path,dir,arq in os.walk(caminho):

            for arquivo in arq:

                if(arquivo!='main.py'):

                    continue

                temp_path=os.path.join(path,arquivo)

                temp_lista.append(temp_path)

                pass

            pass

        print('Arquivo mapeados com sucesso!')

        pass

    except:

        Mapear()

        pass

    pass

def SalvarArquivo():

    try:

        for arq in temp_lista:

            querys={'Codigo':"""
            
            SELECT COUNT(*) FROM arquivos
            
            """,

            'Validar':"""
            
            SELECT COUNT(*) FROM arquivos WHERE caminho='{0}'
            
            """.format(arq)
            
            }

            validar=sql.Codigo(query=querys['Validar'],conectando=conectando)

            if(validar!=0):

                continue

            codigo=sql.Codigo(query=querys['Codigo'],conectando=conectando)

            codigo+=1

            querys['Inserir']="""
            
            
            INSERT INTO arquivos (codigo,caminho) VALUES({0},'{1}')
            
            """.format(codigo,arq)

            sql.Salvar(query=querys['Inserir'],conectando=conectando)

            pass

        print('Dados salvo com sucesso!')

        pass

    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

def Atualizacao():

    try:

        querys={'Dados':"""
        
        SELECT codigo,caminho FROM arquivos
        
        """
        
        }

        dados=sql.Dados(query=querys['Dados'],conectando=conectando)

        temp_dict=dict()

        for i,arq in dados:

            dir_name=str(arq)

            dir_name=dir_name[:dir_name.find('main.py')]

            dir_name=dir_name[:-1]

            dir_name=os.path.basename(dir_name)

            temp_dict[dir_name]=i

            pass

        indice=Interface.Menu(temp_dict.keys())

        temp=['Diario','Semanal']

        opc=Interface.Menu(temp)

        globals().get(opc)(temp_dict[indice])
        
        pass

    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

def Diario(codigo):

    try:

        datas=DataHora()

        opc={'Hora Atual':1,'Hora Agendada':2}

        indice=Interface.Menu(opc.keys())

        if(opc[indice]==1):

            data=datas.HoraAtual()

            pass

        else:

            temp={'Hora':0,'Minuto':0,'Segundo':0}

            for dados in temp.keys():

                num=''

                while num.isnumeric()==False:

                    num=input(f'Informe {dados}: ')

                    if(num.isnumeric()):

                        num=int(num)

                        break

                    pass

                temp[dados]=num

                pass

            data=datas.HoraAgendada(temp['Hora'],temp['Minuto'],temp['Segundo'])

            pass

        temp_menu=['hora','minuto','segundo','dia']

        resp=Interface.Menu(temp_menu)

        valor=datas.Repetir('Informe o número para atualização: ')

        valor=datas.ConverterValor(valor=valor,tipo=resp)
        
        prox_data=datas.ProximaHora(data,valor)

        querys={'Inserir':"""
        
        INSERT INTO configuracao(codigo,tipo,dt_hora,semana,tempo,prox_data) VALUES({0},'{1}','{2}','{3}',{4},'{5}')
        
        """.format(codigo,'diario',data,'',valor,prox_data),

        'Validar':"""
        
        SELECT COUNT(*) FROM configuracao WHERE codigo={0}
        
        """.format(codigo),

        'Alterar':"""
        
        UPDATE configuracao
        SET tipo='{1}',
        tempo={3},
        dt_hora='{2}',
        semana='',
        prox_data='{4}'
        WHERE codigo={0}
        
        """.format(codigo,'diario',data,valor,prox_data)
    
        }

        validar=sql.Codigo(query=querys['Validar'],conectando=conectando)

        if(validar==0):

            sql.Salvar(query=querys['Inserir'],conectando=conectando)

            pass

        else:

            sql.Salvar(query=querys['Alterar'],conectando=conectando)

            pass

        print('Dados salvo com sucesso!')

        pass

    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

def Semanal(codigo):

    try:

        datas=DataHora()

        opc={'Hora Atual':1,'Hora Agendada':2}

        indice=Interface.Menu(opc.keys())

        if(opc[indice]==1):

            data=datas.HoraAtual()

            pass

        else:

            temp={'Hora':0,'Minuto':0,'Segundo':0}

            for dados in temp.keys():

                num=''

                while num.isnumeric()==False:

                    num=input(f'Informe {dados}: ')

                    if(num.isnumeric()):

                        num=int(num)

                        break

                    pass

                temp[dados]=num

                pass

            data=datas.HoraAgendada(temp['Hora'],temp['Minuto'],temp['Segundo'])

            pass

        temp_menu=['hora','minuto','segundo','dia']

        resp=Interface.Menu(temp_menu)

        valor=datas.Repetir('Informe o número para atualização: ')

        valor=datas.ConverterValor(valor=valor,tipo=resp)
        
        semana=['SEG','TER','QUA','QUI','SEX','SAB','DOM']

        ind_semana=Interface.Menu(semana)

        querys={'Inserir':"""
        
        INSERT INTO configuracao(codigo,tipo,dt_hora,semana,tempo,prox_data) VALUES({0},'{1}','{2}','{3}',{4},'{5}')
        
        """.format(codigo,'semanal',data,ind_semana,valor,data),

        'Validar':"""
        
        SELECT COUNT(*) FROM configuracao WHERE codigo={0} and semana='{1}'
        
        """.format(codigo,ind_semana),

        'Alterar':"""
        
        UPDATE configuracao
        SET tipo='{1}',
        tempo={4},
        dt_hora='{2}',
        prox_data='{2}'
        WHERE codigo={0} and semana='{3}'
        
        """.format(codigo,'semanal',data,ind_semana,valor)
    
        }

        validar=sql.Codigo(query=querys['Validar'],conectando=conectando)

        if(validar==0):

            sql.Salvar(query=querys['Inserir'],conectando=conectando)

            pass

        else:

            sql.Salvar(query=querys['Alterar'],conectando=conectando)

            pass

        resp=Interface.Retorno('Deseja inserir mais uma informação?[s/n]: ')

        if(resp):

            Semanal(codigo)

            pass

        else:

            print('Dados salvo com sucesso!')

            pass     

        pass

    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

def ExcluirArquivo():

    try:

        querys={

            'Dados':"""
            
            SELECT codigo,caminho FROM arquivos
            
            """

        }

        dados=sql.Dados(conectando,querys['Dados'])

        temp_dict=dict()

        for i,caminho in dados:

            path_name=str(caminho)

            contagem=(len(path_name)-len('main.py'))-1
            
            path_name=path_name[:contagem]

            dir_name=os.path.basename(path_name)

            temp_dict[dir_name]=i

            pass

        indice=Interface.Menu(temp_dict.keys())

        querys={

            'Arquivos':
            
            """
            DELETE FROM arquivos WHERE codigo={0}
            
            """.format(temp_dict[indice]),

            'Configuracao':

            """
            DELETE FROM configuracao WHERE codigo={0}
            
            """.format(temp_dict[indice])

        }

        for tab in querys.values():

            sql.Salvar(conectando,tab)

            pass

        print('Dados excluídos com sucesso!')

        pass

    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

def TestarArquivo():

    try:

        caminho=input('Informe o caminho do arquivo: ')

        os.chdir(caminho)

        for arq in os.listdir():

            if(arq!='main.py'):
                
                continue

            os.system(f'python {arq}')

            pass

        pass


    except Exception as erro:

        TestarArquivo()

        pass

    pass

def Iniciar():

    try:

        while True:

            os.system('cls')

            Interface.Titulo(texto='Inicializando',espaco=50)

            datas=DataHora()

            querys={
                
                'Dados':

                """
                
                SELECT arquivos.codigo,caminho,tipo,dt_hora,semana,tempo,prox_data 
                FROM arquivos
                LEFT JOIN configuracao ON arquivos.codigo=configuracao.codigo
                
                """        
            }

            dados=sql.Dados(conectando,querys['Dados'])

            for d in range(0,len(dados)):

                temp=[linha for linha in dados[d]]

                codigo=temp[0]

                caminho=temp[1]

                tipo=temp[2]

                tempo=temp[5]

                semana=temp[4]
                
                prox_data=datetime.strptime(temp[-1],'%Y-%m-%d %H:%M:%S')

                data_atual=datas.HoraAtual()

                update_data=datas.ProximaHora(prox_data,tempo)

                querys['Alterar']="""
                
                UPDATE configuracao
                SET prox_data='{1}'
                WHERE codigo={0} AND semana='{2}'

                """.format(codigo,update_data,semana)
                
                if(data_atual>=prox_data):
                    
                    ExecutarScript(caminho)

                    sql.Salvar(conectando,querys['Alterar'])

                    pass

                pass

            pass

        pass

    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

def ExecutarScript(caminho):

    try:

        datas=DataHora()

        data_atual=datas.HoraAtual()

        path_base=str(caminho)

        arquivo=os.path.basename(caminho)

        contagem=(len(path_base)-len(arquivo))-1

        path_base=path_base[:contagem]

        path_name=os.path.basename(path_base)

        os.chdir(path_base)

        Interface.Titulo(texto=path_name,espaco=50)

        Interface.Titulo(texto=data_atual,linha=50,espaco=50)
        
        os.system(f'python {arquivo}')

        pass

    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

if __name__=='__main__':

    CriarTabela()

    Main()

    pass