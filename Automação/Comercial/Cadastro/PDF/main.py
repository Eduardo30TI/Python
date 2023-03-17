import tabula
from PyPDF2 import PdfReader
import warnings
from Acesso import Login
from Query import Query
from Interface import GUI
from pathlib import Path as base_path
import os
import shutil
import pandas as pd
from zipfile import ZipFile

gui=GUI()

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

path_foto='Documentos Empresa'

querys={

    'Produto':

    """

    SELECT p.SKU,p.[Cód. Fabricante],p.Produto,p.EAN,p.Fabricante,p.Seção,p.Linha
    FROM netfeira.vw_produto p
    ORDER BY Produto
    
    """
}

warnings.filterwarnings('ignore')


def Main():

    gui.Cls()

    paths_dict={'Origem':'','Destino':''}

    for c in paths_dict.keys():

        while True:

            caminho=input(f'Informe o caminho de {str(c).lower()}: ')

            if caminho!='' and gui.PathExists(caminho)==True:

                paths_dict[c]=caminho

                break

            pass

        pass
    
    dirs=base_path(paths_dict['Origem'])

    lista=list(dirs.rglob('*.pdf*'))

    PdfDM(lista,paths_dict)

    PdfBIMBO(lista,paths_dict)

    PdfMCCAIN(lista,paths_dict)

    pass

def PdfDM(listas: list,path_dict: dict):

    df=sql.CriarTabela(kwargs=querys)

    col='códigos internos'

    codigos=[]

    dados_dict=dict()

    for i,lista in enumerate(listas):

        try:

            gui.Cls()

            arq=gui.BaseName(lista)

            print(f'Lendo arquivo {i+1} de {len(listas)}. Aguarde...')

            lista_pdf=tabula.read_pdf(lista,pages='all')

            for l in lista_pdf:

                colunas=l.columns.tolist()

                if str(colunas[0]).lower()!=col:

                    continue
                    
                temp_df=l

                col_name=[str(l).lower() for l in temp_df.columns.tolist()]

                temp_df.columns=col_name
                
                temp_df[col]=temp_df[col].apply(ConverterFloat)

                for c in temp_df.loc[temp_df[col].notnull(),col].unique().tolist():

                    if str(c).find('/')>=0:

                        ids=str(c).strip().split('/')

                        for id in ids:

                            if id in codigos:

                                continue

                            codigos.append(id)

                            dados_dict[id]=lista

                            pass

                        pass

                    else:

                        if c in codigos:

                            continue
                        
                        codigos.append(c)

                        dados_dict[c]=lista

                        pass

                    pass

                pass

            pass

        except:
            
            continue

        pass

    for key,value in dados_dict.items():

        gui.Cls()

        print('Estamos copiando os arquivos aguarde...')

        try:
            
            col_leach='Cód. Fabricante'

            fabricante=df['Produto'].loc[df['Produto'][col_leach]==key,'Fabricante'].tolist()[-1]

            secao=df['Produto'].loc[df['Produto'][col_leach]==key,'Seção'].tolist()[-1]

            linha=df['Produto'].loc[df['Produto'][col_leach]==key,'Linha'].tolist()[-1]

            sku=df['Produto'].loc[df['Produto'][col_leach]==key,'SKU'].tolist()[-1]

            temp_path=os.path.join(path_dict['Destino'],path_foto,fabricante,secao,linha,f'{sku}.pdf')

            path_dir=gui.PathDir(temp_path)

            if not os.path.exists(path_dir):

                os.makedirs(path_dir)

                pass

            shutil.copy(value,temp_path)

            pass

        except:

            continue

        pass

    print('Arquivo copiado com sucesso!')

    pass

def PdfBIMBO(listas: list,path_dict: dict):

    df=sql.CriarTabela(kwargs=querys)

    codigos=[]

    dados_dict=dict()

    for i,lista in enumerate(listas):

        try:

            gui.Cls()

            arq=gui.BaseName(lista)

            print(f'Lendo arquivo {i+1} de {len(listas)}. Aguarde...')

            lista_pdf=tabula.read_pdf(lista,pages='all')

            #ler pdf
            for l in lista_pdf:

                #extrair dados                          
                for c in l.columns.tolist():

                    linhas=lista_pdf[1].loc[lista_pdf[1][c].notnull(),c].tolist()

                    for j in linhas:

                        if len(j)==13 and str(j).isnumeric()==True:

                            if j in codigos:

                                continue

                            dados_dict[j]=lista

                            codigos.append(j)

                            pass

                        pass

                    pass
                #FIM

                pass

            pass

        except:

            continue


        pass

    for key,value in dados_dict.items():

        gui.Cls()

        print('Estamos copiando os arquivos aguarde...')

        try:

            col_leach='EAN'
        
            fabricante=df['Produto'].loc[df['Produto'][col_leach]==key,'Fabricante'].tolist()[-1]

            secao=df['Produto'].loc[df['Produto'][col_leach]==key,'Seção'].tolist()[-1]

            linha=df['Produto'].loc[df['Produto'][col_leach]==key,'Linha'].tolist()[-1]

            sku=df['Produto'].loc[df['Produto'][col_leach]==key,'SKU'].tolist()[-1]

            temp_path=os.path.join(path_dict['Destino'],path_foto,fabricante,secao,linha,f'{sku}.pdf')

            path_dir=gui.PathDir(temp_path)

            if not os.path.exists(path_dir):

                os.makedirs(path_dir)

                pass

            shutil.copy(value,temp_path)

            pass

        except:

            continue

        pass

    print('Arquivo copiado com sucesso!')

    pass

def PdfMCCAIN(listas: list,path_dict: dict):

    df=sql.CriarTabela(kwargs=querys)

    codigos=[]

    dados_dict=dict()

    for i,lista in enumerate(listas):

        try:

            gui.Cls()

            arq=gui.BaseName(lista)

            print(f'Lendo arquivo {i+1} de {len(listas)}. Aguarde...')

            lista_pdf=PdfReader(lista)
            page=lista_pdf.pages[0]

            text=page.extract_text()

            content=text.split('\n')

            col_leach='pacote'

            val=[l for l in content if str(l).lower().find(col_leach)>=0]

            val=[l for l in val[0].split()]

            val=val[-1]

            if val in codigos:

                continue

            dados_dict[val]=lista

            codigos.append(val)

            pass

        except:

            continue


        pass

    for key,value in dados_dict.items():

        gui.Cls()

        print('Estamos copiando os arquivos aguarde...')

        try:

            col_leach='EAN'
        
            fabricante=df['Produto'].loc[df['Produto'][col_leach]==key,'Fabricante'].tolist()[-1]

            secao=df['Produto'].loc[df['Produto'][col_leach]==key,'Seção'].tolist()[-1]

            linha=df['Produto'].loc[df['Produto'][col_leach]==key,'Linha'].tolist()[-1]

            sku=df['Produto'].loc[df['Produto'][col_leach]==key,'SKU'].tolist()[-1]

            temp_path=os.path.join(path_dict['Destino'],path_foto,fabricante,secao,linha,f'{sku}.pdf')

            path_dir=gui.PathDir(temp_path)

            if not os.path.exists(path_dir):

                os.makedirs(path_dir)

                pass

            shutil.copy(value,temp_path)

            pass

        except:

            continue

        pass

    print('Arquivo copiado com sucesso!')

    pass

def ConverterFloat(val: str):

    val=str(val)

    val=val.strip().split('.')

    return val[0]

    pass

def ExtrairZip(loop=False,caminho=None):

    gui.Cls()

    if loop==False:

        while True:

            caminho=input('Informe o caminho: ')

            if os.path.exists(caminho)==True:

                break

            pass

        pass

    path_base=os.path.join(caminho,'Base')

    if not os.path.exists(path_base):

        os.makedirs(path_base)

        pass

    lista=list(base_path(caminho).rglob('*.zip*'))
        
    for arq in lista:

        arquivo=str(gui.BaseName(arq))

        arquivo=arquivo.split('.')[0]

        temp_path=os.path.join(path_base,arquivo)

        with ZipFile(arq,'r') as read_zipe:

            read_zipe.extractall(temp_path)                

            pass

        pass

    lista=list(base_path(path_base).rglob('*.zip*'))

    if len(lista)>0:

        ExtrairZip(loop=True,caminho=path_base)

        pass

    print('Extração finalizada!')

    pass

if __name__=='__main__':

    Main()

    pass