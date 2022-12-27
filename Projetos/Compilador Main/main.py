from SQLITE import SQLConexao
from Interface import Interface
import os
import time
from joblib import Parallel,delayed

conecta=SQLConexao('MOINHO.db')

conectando=conecta.Conexao()

tabela={

'Configuracao':

"""

CREATE TABLE IF NOT EXISTS configuracao(

codigo SMALLINT NOT NULL,
caminho TEXT NOT NULL,
tempo SMALLINT NOT NULL,
paralelo SMALLINT NOT NULL

)

"""


}

def CriarTabela(conectando):

    for tab in tabela.values():

        conecta.Salvar(conectando,tab)

        pass

    pass

def Main():

    dados=['Configuracao','Iniciar']

    Interface.Titulo('Menu',50,50)

    func=Interface.Menu(dados)

    Interface.Titulo(linha=50)

    globals().get(func)()
    
    resp=Interface.Retorno('Deseja executar o programa novamente?[s/n]: ')

    if(resp):

        Main()

        pass
    
    pass

def Configuracao():

    querys={

        1:"""
        
        SELECT COUNT(*) FROM configuracao
        
        """

    }

    codigo=conecta.Codigo(conectando,querys[1])

    dados={'caminho':'','tempo':'','paralelo':''}

    for d in dados.keys():

        resp=''

        while resp=='':

            resp=input(f'Informe o {d}: ')
                
            pass

        dados[d]=resp

        pass

    if(codigo==0):

        codigo+=1

        querys[2]="""
        
        INSERT INTO configuracao (codigo,caminho,tempo,paralelo) VALUES({0},'{1}',{2},{3})
        
        """.format(codigo,dados['caminho'],dados['tempo'],dados['paralelo'])

        conecta.Salvar(conectando,querys[2])
        
        pass

    else:

        querys[3]="""
        
        UPDATE configuracao
        SET caminho='{0}',
        tempo={1},
        paralelo={2}
        WHERE codigo={3}

        """.format(dados['caminho'],dados['tempo'],dados['paralelo'],codigo)

        conecta.Salvar(conectando,querys[3])

        pass

    print('Dados salvo com sucesso!')

    pass

def Iniciar():
    
    querys={

        1:
        """
        
        SELECT caminho,tempo,paralelo FROM configuracao WHERE codigo=1
        
        """

    }

    info=conecta.Dados(conectando,querys[1])

    while True:

        os.system('cls')

        Interface.Titulo('Arquivos sendo executado aguarde...')

        Interface.Titulo(linha=50)

        indice=[linha for linha in info[0]]

        caminho=indice[0]

        tempo=indice[1]

        paralelo=indice[2]

        temp=[]

        for path,dir,arq in os.walk(caminho):

            for arquivo in arq:

                if(not arquivo=='main.py'):

                    continue

                temp_path=os.path.join(path,arquivo)

                temp.append(temp_path)

                pass

            pass

        Parallel(n_jobs=paralelo)(delayed(ExecutarScript)(arq) for arq in temp)

        time.sleep(tempo)

        pass

    pass

def ExecutarScript(arquivo):

    arq_nome=os.path.basename(arquivo)

    path_base=str(arquivo)

    path_base=path_base[:path_base.find(arq_nome)]

    path_base=path_base[:-1]

    os.chdir(path_base)

    os.system(f'py {arq_nome}')

    pass

if __name__=='__main__':
        
    CriarTabela(conectando)

    Main()

    pass