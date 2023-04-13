from Acesso import Login
from Query import Query
from Email import Email
from RemoverArquivo import Remover
from glob import glob
import os
from datetime import datetime
import win32com.client as win32
import pandas as pd

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Custo':

    """
    
    SELECT c.SKU,c.[Cód. Fabricante],c.Produto,c.Fabricante,c.[Unid. CMP],c.Caixa,c.[Anterior C/ST],c.[Atual C/ST],c.[Dif R$],c.[Perc %],c.[Alerta de Custo],c.[Última Entrada]
	FROM netfeira.vw_custo c
    WHERE [Tipo de Custo]='ULTIMA ENTRADA' AND [Alerta de Custo]<>'OK'
    AND [Última Entrada] BETWEEN DATEADD(DAY,-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)) AND CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)
    ORDER BY SKU
    
    """,

    'Data':

    """
    
    SELECT DATEADD(DAY,-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)) AS [Inicio]
    ,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101) AS [Fim]
    
    """
}

path_name='Compras'

send_path='Sent Items'

assunto_base='Alteração de custo'

def Main():

    df=sql.CriarTabela(kwargs=querys)

    colunas=df['Custo'].columns.tolist()

    path_memoria=os.path.join(os.getcwd(),'Consolidado.csv')

    if os.path.exists(path_memoria)==True:

        dt_min=df['Data']['Inicio'].max()

        dt_max=df['Data']['Fim'].max()

        temp_df=pd.read_csv(path_memoria,encoding='UTF-8')

        temp_df['Última Entrada']=pd.to_datetime(temp_df['Última Entrada'])

        temp_df=temp_df.loc[temp_df['Última Entrada'].between(dt_min,dt_max)]

        df['Custo']['ID']=df['Custo']['SKU'].astype(str) + '' + df['Custo']['Última Entrada'].astype(str)

        temp_df['ID']=temp_df['SKU'].astype(str) + '' + temp_df['Última Entrada'].astype(str)

        codigos=temp_df['ID'].unique().tolist()

        df['Custo']=df['Custo'].loc[~df['Custo']['ID'].isin(codigos)]

        df['Consolidado']=pd.concat([df['Custo'],temp_df],axis=0,ignore_index=True)

        pass

    if len(df['Custo'])>0:
        
        msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

        dt_atual=datetime.strftime(datetime.now().date(),'%d/%m/%Y')

        assunto=f'Alteração de custo {dt_atual}'

        nome=f'Eduardo/Vilton'

        temp_path=os.path.join(os.getcwd(),'Email','*.png')

        img=glob(temp_path)

        mensagem=f"""
            
        <p>{msg};</p>

        <p>{str(nome).title()}</p>

        <p>Segue abaixo produto para efetuar inclusão de custo.</p>

        <img src="{img[-1]}" height=195 with=326/>
        
        """

        email_to=['eduardo.marfim@demarchibrasil.com.br','vilton.paiva@demarchisaopaulo.com.br']

        #email_to=['eduardo.marfim@demarchibrasil.com.br']

        email_cc=['edson.junior@demarchibrasil.com.br','compras@demarchibrasil.com.br','rogerio.felipim@demarchibrasil.com.br','julio@demarchibrasil.com.br']

        #email_cc=[]

        df['Custo'].to_excel('Alteração de Custo.xlsx',index=False)

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        arquivos=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':arquivos}

        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

        Remover.RemoverArquivo('.xlsx')

        #Verificar se as pastas
        outlook=win32.Dispatch('Outlook.Application').GetNameSpace('MAPI')

        #caixa de entrada identificar pasta x
        inbox=outlook.GetDefaultFolder(6)
        paths=inbox.Folders

        lista=[l.Name for l in paths]

        if not path_name in lista:

            inbox.Folders.Add(path_name)

            print('Pasta criada com sucesso')

            pass
        
        #encontrar os emails
        folders=outlook.Folders.Item(1)
        sendbox=folders.Folders[send_path]

        messages=sendbox.items

        path_orig=inbox.Folders[path_name]

        for m in messages:

            if str(m.subject).find(assunto_base)<0:

                continue

            m.move(path_orig)

            pass

        if not os.path.exists(path_memoria):

            df['Custo'].to_csv(path_memoria,index=False,encoding='UTF-8')

            pass

        else:
        
            df['Consolidado'][colunas].to_csv(path_memoria,index=False,encoding='UTF-8')

            pass

        pass

    pass


if __name__=='__main__':

    Main()

    pass