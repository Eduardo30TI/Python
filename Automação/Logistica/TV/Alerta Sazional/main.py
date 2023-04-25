import pandas as pd
from Acesso import Login
from Query import Query
from datetime import datetime,timedelta
import requests

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data_inicio=datetime.now()-timedelta(days=30)

data_atual=datetime.now()

querys={
    
    'Vendas':
    
    """
    
    DECLARE @DTBASE DATETIME, @DTFIM DATETIME, @DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS date),101)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=DATEADD(DAY,-30,@DTFIM)

    SELECT * FROM netfeira.vw_estatistico
    WHERE [Data de Emissão] BETWEEN @DTINICIO AND @DTFIM AND [Tipo de Operação]<>'OUTROS' AND [ID Situação] IN('FA','AB')
    
    """,
    
    'Estoque':
    
    """
    
    SELECT * FROM netfeira.vw_estoque
    WHERE Tipo='CENTRAL'    
    
    """
    
}

def Main(tabelas_df):

    vendas_df=pd.DataFrame()

    vendas_df=tabelas_df['Vendas']

    #vendas_df=vendas_df.loc[(vendas_df['Tipo de Operação']!='OUTROS')&(vendas_df['ID Situação'].isin(['FA','AB']))]

    #vendas_df=vendas_df.loc[vendas_df['Data de Emissão'].between(data_inicio,data_atual)]

    vendas_df=vendas_df[['SKU','Total Venda']].groupby(['SKU'],as_index=False).sum()

    codigos=vendas_df['SKU'].unique().tolist()

    estoque_df=pd.DataFrame()

    estoque_df=tabelas_df['Estoque']

    estoque_df=estoque_df.loc[(~estoque_df['SKU'].isin(codigos))&(estoque_df['Qtde Disponível']>0)]

    Analise(estoque_df)

    pass

def Analise(df):

    links={

        'Consolidado':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/01bb04e9-fb69-4549-a7ae-c801d18c9897/rows?noSignUpCheck=1&key=d3hQ6aWnwJ19WUBPGjl2WU8xFoXGGgeP8wpPyoA%2BcyE1ar6vpz%2By%2BANCAtd%2FScpH%2BL2pINCKvm9m%2BL2aIq5vBQ%3D%3D',
        'Produto':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/04dc9eef-f25a-4677-80c3-22ee81ecf519/rows?key=fmhjQdVJagLvqgBrjy2qepxHkYG7RfcZwga8jdSLUjBSuIVk2Hp6cc5qyZQv4Ht1G2FWI22dxDuEOc5LJp1EeA%3D%3D'

    }

    qtde=df['Qtde Disponível'].sum()

    total=df['Custo Total'].sum()

    mix=len(df['SKU'].unique().tolist())

    peso=df['Peso Disponível'].sum()

    caixa=df['Caixa Disponível'].sum()

    temp_dict=[

        {

        "Qtde Saldo" :float(qtde),
        "Custo Total R$" :float(total),
        "MIX" :float(mix),
        "Peso KG" :float(peso),
        "Caixa" :float(caixa)
        }
    ]

    requests.post(url=links['Consolidado'],json=temp_dict)

    df['SKU']=df['SKU'].astype(str)

    df=df[['SKU','Produto','Qtde Disponível']]

    df.sort_values('Qtde Disponível',ascending=False,inplace=True)

    requests.post(url=links['Produto'],json=df.to_dict('records'))

    pass


if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass