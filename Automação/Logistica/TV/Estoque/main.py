from http.cookiejar import FileCookieJar
from Acesso import Login
from Query import Query
import pandas as pd
import requests

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Estoque':

    """
    
    SELECT * FROM netfeira.vw_estoque
    
    """,

    'Vendas':

    """
    
    DECLARE @DTBASE DATETIME,@DTFIM DATETIME, @DTINICIO DATETIME,@DIAS SMALLINT

    SET @DIAS=30

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=DATEADD(DAY,-1,@DTBASE)

    SET @DTINICIO=DATEADD(DAY,@DIAS*-1,@DTFIM)

    SELECT * FROM netfeira.vw_targetestatico
    WHERE [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM AND [Tipo de Operação]<>'OUTROS'

    
    """
}

def Main(tabelas_df):

    urls={
    
        'Consolidado':

        'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/888cbe82-5a75-4482-bd80-ffc00429e181/rows?key=iusDuMKo%2F5akxnCUS7rGhgzSuZByUuLor2Kgz8BzTUibq0uiLvtdE5AQdJTrMy8BYJ%2F9Gyhud4srTu8DEX8DQQ%3D%3D',

        'ProdA':

        'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/62da6985-3f0e-4a16-bd16-3d59ee7ec5f7/rows?key=AMWB%2FemZhWlYh6Fge%2F6dIv4ruU1DCK7TFQRJSTctt8eRwv0j4XWSenywXzdBCABO3vQc40Bvs%2BwvdNQWL95BCw%3D%3D',

        'ProdB':
        
        'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/2ed20a33-de16-4844-9a4c-39856127e0cd/rows?key=93zilN0xNPOy5h92EerosWept6VHmpWpaAEaQmJn1hzauRNjANJVw29bI9jb9vNZ%2BxdbeYYZYFPAHP7%2BckZtgw%3D%3D'
    
    }

    vendas_df=pd.DataFrame()

    vendas_df=tabelas_df['Vendas'][['SKU','Qtde']].groupby(['SKU'],as_index=False).sum()

    vendas_df.sort_values('Qtde',ascending=False,ignore_index=True,inplace=True)

    qtde=vendas_df['Qtde'].sum()

    vendas_df['Qtde Empresa']=qtde

    vendas_df=vendas_df.loc[vendas_df['Qtde']>0]

    res=0

    valores=[]

    for indice,linha in vendas_df.iterrows():
        
        res+=linha['Qtde'].sum()
        
        valores.append(res)
        
        pass

    vendas_df['Qtde Acumulado']=valores

    vendas_df['Perc']=vendas_df.apply(lambda info: round(info['Qtde Acumulado']/info['Qtde Empresa'],4)*100,axis=1)

    vendas_df['Classificação']=vendas_df['Perc'].apply(Classificao)

    estoque_df=pd.DataFrame()

    estoque_df=tabelas_df['Estoque'].merge(vendas_df,on='SKU',how='left')[['Local', 'Tipo', 'SKU', 'Cód. Fabricante', 'Produto', 'Fabricante',
        'Departamento', 'Seção', 'Categoria', 'Linha', 'Fator CX', 'Unid. CMP',
        'Qtde Disponível', 'Caixa Disponível', 'Peso Disponível', 'Qtde CMP','Classificação','Perc']]

    local_df=pd.DataFrame()

    local_df=estoque_df[['Local','Qtde Disponível']].groupby(['Local'],as_index=False).sum()

    local_df=local_df.loc[local_df['Qtde Disponível']>0]

    locais=local_df['Local'].tolist()
    
    estoque_df=estoque_df.loc[estoque_df['Local'].isin(locais)]

    estoque_df=estoque_df[['SKU', 'Cód. Fabricante', 'Produto', 'Fabricante',
        'Departamento', 'Seção', 'Categoria', 'Linha','Classificação','Perc','Qtde Disponível']].groupby(['SKU', 'Cód. Fabricante', 'Produto', 'Fabricante',
        'Departamento', 'Seção', 'Categoria', 'Linha','Classificação','Perc'],as_index=False).sum()

    qtde_prod=len(estoque_df['SKU'].unique().tolist())

    prod_disp=len(estoque_df['SKU'].loc[estoque_df['Qtde Disponível']<=0].unique().tolist())

    prod_ativo=len(estoque_df['SKU'].loc[estoque_df['Qtde Disponível']>0].unique().tolist())

    perc=round(prod_ativo/qtde_prod,4)*100

    minimo=0

    maximo=100

    qtde_pendente=tabelas_df['Estoque']['Qtde Pendente'].loc[tabelas_df['Estoque']['Local'].isin(locais)].sum()

    qtde_saldo=estoque_df['Qtde Disponível'].sum()

    classificacao_df=pd.DataFrame()

    classificacao_df=estoque_df[['Classificação','SKU']].groupby(['Classificação'],as_index=False).count()

    classificacao_df['Contagem']=qtde_prod

    classificacao_df['Perc']=classificacao_df.apply(lambda info: round(info['SKU']/info['Contagem'],4)*100,axis=1)

    class_a=classificacao_df['SKU'].loc[classificacao_df['Classificação']=='A'].max()

    class_b=classificacao_df['SKU'].loc[classificacao_df['Classificação']=='B'].max()

    class_c=classificacao_df['SKU'].loc[classificacao_df['Classificação']=='C'].max()

    perc_a=classificacao_df['Perc'].loc[classificacao_df['Classificação']=='A'].max()

    perc_b=classificacao_df['Perc'].loc[classificacao_df['Classificação']=='B'].max()

    perc_c=classificacao_df['Perc'].loc[classificacao_df['Classificação']=='C'].max()

    prod_a=len(estoque_df['SKU'].loc[(estoque_df['Classificação']=='A')&(estoque_df['Qtde Disponível']<=0)].unique().tolist())

    prod_b=len(estoque_df['SKU'].loc[(estoque_df['Classificação']=='B')&(estoque_df['Qtde Disponível']<=0)].unique().tolist())

    prod_c=len(estoque_df['SKU'].loc[(estoque_df['Classificação']=='C')&(estoque_df['Qtde Disponível']<=0)].unique().tolist())

    temp_dict={

        "Produtos" :float(qtde_prod),
        "Saldo" :float(qtde_saldo),
        "Mínimo" :float(minimo),
        "Máximo" :float(maximo),
        "Classificação A" :float(class_a),
        "Classificação B" :float(class_b),
        "Classificação C" :float(class_c),
        "Perc A" :float(perc_a),
        "Perc B" :float(perc_b),
        "Perc C" :float(perc_c),
        'Qtde Pendente':float(qtde_pendente),
        'Produto Indisponível':float(prod_disp),
        'Perc Disponível':float(perc),
        'Produto Disponível':float(prod_ativo),
        'Indisponível A':float(prod_a),
        'Indisponível B':float(prod_b),
        'Indisponível C':float(prod_c)


    }
    
    requests.post(url=urls['Consolidado'],json=temp_dict)

    df=estoque_df[['SKU','Produto','Perc']].loc[(estoque_df['Classificação']=='A')&(estoque_df['Qtde Disponível']<=0)]

    df.sort_values('Perc',ascending=False,ignore_index=True,inplace=True)

    requests.post(url=urls['ProdA'],json=df.to_dict('records'))

    df=estoque_df[['SKU','Produto','Perc']].loc[(estoque_df['Classificação']=='B')&(estoque_df['Qtde Disponível']<=0)]

    df.sort_values('Perc',ascending=False,ignore_index=True,inplace=True)

    requests.post(url=urls['ProdB'],json=df.to_dict('records'))

    pass


def Classificao(perc):
    
    if(perc<=80):
        
        retorno='A'
        
        pass
    
    elif(perc<=95):
        
        retorno='B'
        
        pass
    
    else:
        
        retorno='C'
        
        pass
    
    return retorno
    
    pass



if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass