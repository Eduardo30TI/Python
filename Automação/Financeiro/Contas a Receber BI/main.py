from h11 import Data
from Acesso import Login
from Query import Query
from Tempo import DataHora
import pandas as pd
import requests

data=DataHora()

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Receber':

    """
    
    SELECT * FROM netfeira.vw_contareceber
    
    """,
    
    'Segmento':
    
    """
    
    SELECT * FROM netfeira.vw_segmento
    
    """

}


def Main(tabelas_df):

    data_atual=data.HoraAtual()

    ano=data_atual.year

    mes=data_atual.month

    titulos_df=pd.DataFrame()

    titulos_df=tabelas_df['Receber'].merge(tabelas_df['Segmento'],on='ID Segmento',how='inner')[['Data de Emissão', 'Data de Vencimento', 'Data de Pagamento', 'Título',
        'Serie', 'Tipo de Pagamento', 'ID Cliente','CNPJ', 'Razão Social',
        'Nome Fantasia', 'Matriz', 'Segmento','Canal', 'Situação', 'Valor',
        'Desconto R$', 'Multa R$', 'Juros R$', 'Abatimento R$', 'Taxa R$',
        'Valor Líquido', 'Pago R$','Status do Título', 'Dias', 'Alerta']]

    titulos_df['Saldo R$']=titulos_df.apply(lambda info: info['Valor Líquido']-info['Pago R$'],axis=1)
    
    tit_venc=len(titulos_df['Título'].loc[(titulos_df['Situação'].str.contains('PARC|ABERTO'))&(titulos_df['Status do Título']=='VENCIDO')&(titulos_df['Data de Vencimento'].dt.year==ano)&(titulos_df['Data de Vencimento'].dt.month==mes)].unique().tolist())

    tot_venc=titulos_df['Saldo R$'].loc[(titulos_df['Situação'].str.contains('PARC|ABERTO'))&(titulos_df['Status do Título']=='VENCIDO')&(titulos_df['Data de Vencimento'].dt.year==ano)&(titulos_df['Data de Vencimento'].dt.month==mes)].sum()

    tit_pagto=len(titulos_df['Título'].loc[(titulos_df['Situação']=='LIQUIDADO')&(titulos_df['Data de Pagamento'].dt.year==ano)&(titulos_df['Data de Pagamento'].dt.month==mes)].unique().tolist())

    tot_pagto=round(titulos_df['Pago R$'].loc[(titulos_df['Situação']=='LIQUIDADO')&(titulos_df['Data de Pagamento'].dt.year==ano)&(titulos_df['Data de Pagamento'].dt.month==mes)].sum(),2)

    tit_as=len(titulos_df['Título'].loc[(titulos_df['Situação'].str.contains('PARC|ABERTO'))&(titulos_df['Status do Título']=='VENCIDO')&(titulos_df['Data de Vencimento'].dt.year==ano)&(titulos_df['Data de Vencimento'].dt.month==mes)&(titulos_df['Canal']=='AS')].unique().tolist())

    tot_as=round(titulos_df['Saldo R$'].loc[(titulos_df['Situação'].str.contains('PARC|ABERTO'))&(titulos_df['Status do Título']=='VENCIDO')&(titulos_df['Data de Vencimento'].dt.year==ano)&(titulos_df['Data de Vencimento'].dt.month==mes)&(titulos_df['Canal']=='AS')].sum(),2)

    perc_as=round(tit_as/tit_venc,4)*100

    tit_fs=len(titulos_df['Título'].loc[(titulos_df['Situação'].str.contains('PARC|ABERTO'))&(titulos_df['Status do Título']=='VENCIDO')&(titulos_df['Data de Vencimento'].dt.year==ano)&(titulos_df['Data de Vencimento'].dt.month==mes)&(titulos_df['Canal']=='FS')].unique().tolist())

    tot_fs=round(titulos_df['Saldo R$'].loc[(titulos_df['Situação'].str.contains('PARC|ABERTO'))&(titulos_df['Status do Título']=='VENCIDO')&(titulos_df['Data de Vencimento'].dt.year==ano)&(titulos_df['Data de Vencimento'].dt.month==mes)&(titulos_df['Canal']=='FS')].sum(),2)

    perc_fs=round(tit_fs/tit_venc,4)*100

    temp_df=pd.DataFrame()

    temp_df=titulos_df.loc[(titulos_df['Status do Título'].isin(['A VENCER','VENCIDO']))&(titulos_df['Data de Vencimento'].dt.year==ano)&(titulos_df['Data de Vencimento'].dt.month==mes)]

    matriz_df=pd.DataFrame()

    matriz_df=temp_df[['Matriz','Saldo R$']].loc[(~temp_df['Matriz'].isnull())&(temp_df['Status do Título']=='VENCIDO')].groupby(['Matriz'],as_index=False).agg({'Saldo R$':'sum'})

    matriz_df.sort_values('Saldo R$',ascending=False,ignore_index=True,inplace=True)

    consolidado_dict={
        
        "Título Vencido" :float(tit_venc),
        "Vencido R$" :float(tot_venc),
        "Títulos Pagos" :float(tit_pagto),
        "Pagos R$" :float(tot_pagto),
        "Canal AS" :float(tit_as),
        "Canal AS R$" :float(tot_as),
        "Canal FS" :float(tit_fs),
        "Canal FS R$" :float(tot_fs),
        "Mínimo" :float(0),
        "Máximo" :float(100),
        "Rep AS %":float(perc_as),
        "Rep FS %":float(perc_fs)

        }

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/f6b98e7a-6f19-4702-b203-ff9d7816b330/rows?noSignUpCheck=1&key=NIF5FUDQsFZKqaeHQ3M91O4EXSl4fXrZ8CjlVgXYZ5V30tWX21tKywp4l%2FiwkFU3KMsxnZc%2FCmJ3xIuS7A0rSg%3D%3D',json=consolidado_dict)

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/2b463fee-2bbc-47e6-ac21-e51b52f409b2/rows?key=R8s3kng0ceMyhRNcya8cELr6CpUTHoJ%2BS8R6dZH0oi0ea5aH%2Fu2BdYGHB54%2BMOp2QLMSF3gWsuatUOyYFkBTdg%3D%3D',json=matriz_df.to_dict('records'))

    matriz_df=pd.DataFrame()

    matriz_df=temp_df[['Matriz','Saldo R$']].loc[(~temp_df['Matriz'].isnull())&(temp_df['Status do Título']=='A VENCER')].groupby(['Matriz'],as_index=False).agg({'Saldo R$':'sum'})

    matriz_df.sort_values('Saldo R$',ascending=False,ignore_index=True,inplace=True)

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/1bcac7f3-63fd-4849-9b1f-7c582f8997ea/rows?key=JtS72yhwtn5VXmp0gdAyHWC42RuxBw%2F6ra8cv3lMa0iGfOuAfx0mcuyF9KuA6R42cfgomyLDJ%2FkG3wsmlQy8mA%3D%3D',json=matriz_df.to_dict('records'))

    cliente_df=pd.DataFrame()

    cliente_df=temp_df[['Nome Fantasia','Saldo R$']].loc[(temp_df['Status do Título']=='VENCIDO')].groupby(['Nome Fantasia'],as_index=False).agg({'Saldo R$':'sum'})

    cliente_df.sort_values('Saldo R$',ascending=False,ignore_index=True,inplace=True)

    total=cliente_df['Saldo R$'].sum()

    cliente_df['Total Geral']=total

    res=0

    valores=[]

    for indice,linha in cliente_df.iterrows():
        
        res=cliente_df['Saldo R$'].iloc[:indice+1].sum()
        
        valores.append(res)
        
        pass

    cliente_df['Acumulado']=valores

    cliente_df['Perc %']=cliente_df.apply(lambda info: round(info['Acumulado']/info['Total Geral'],4)*100,axis=1)

    cliente_df['Classificação']=cliente_df['Perc %'].apply(Classificacao)

    cliente_df=cliente_df[['Nome Fantasia','Saldo R$']].loc[cliente_df['Classificação']!='C']

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/3be589c6-6914-4fd4-ab60-c5c33971ff37/rows?key=YKNUT0aPINZDx%2B9fs9IAAf%2BEsE12UndHuiU0QgfFcZOafxg15RR5PeVHlpnCQ0y2G8KlemXEDt%2FLNvA65Pst7Q%3D%3D',json=cliente_df.to_dict('records'))

    print(cliente_df)

    pass

def Classificacao(valor):
    
    if(valor<=80):
        
        tipo='A'
        
        pass
    
    elif(valor<=95):
        
        tipo='B'
        
        pass
    
    else:
        
        tipo='C'
        
        pass
    
    return tipo
    
    pass

if __name__=='__main__':

    tabelas_df=sql.CriarTabela(kwargs=querys)

    Main(tabelas_df)

    pass