from Query import Query
import os
from glob import glob
import requests
from Tempo import DataHora
import pandas as pd


sql=Query('Netfeira','sqlserver','MOINHO','192.168.0.252')

data=DataHora()

base_contas=['CAIXA-CONSORCIO','DISTRIBUICAO DE LUCRO','FORNECEDORES','RECIFE','SALVADOR','BELEM','CAMBIO','CONSORCIO','LITORAL','NUMERARIO','PARANA']

def Consolidado(tabelas_df):

    url_base='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/7eab6da5-7067-4472-9035-e3231753e881/rows?key=k3VJLCx4WI3R2UWCZDiZxcqtQLj1IoS%2F52s4rsgnNKpwdIsvAYeF%2FQaJ2bPA8k8d%2FXlbo4DlNXSvSIzI3ECRVg%3D%3D'
    
    data_atual=data.HoraAtual()

    titulos_vencidos=len(tabelas_df['Pagar']['Título'].loc[(tabelas_df['Pagar']['Data de Vencimento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Vencimento'].dt.month==data_atual.month)&(tabelas_df['Pagar']['ID Situação'].isin(['AB','PL']))&(tabelas_df['Pagar']['Contas'].isin(['FORNECEDORES']))].unique().tolist())

    valor_vencer=tabelas_df['Pagar']['Título R$'].loc[(tabelas_df['Pagar']['Data de Vencimento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Vencimento'].dt.month==data_atual.month)&(tabelas_df['Pagar']['ID Situação'].isin(['AB','PL']))&(tabelas_df['Pagar']['Contas'].isin(['FORNECEDORES']))].sum()

    faturado=round(tabelas_df['Estatico']['Total Geral'].loc[(tabelas_df['Estatico']['Tipo de Operação']=='VENDAS')&(tabelas_df['Estatico']['Status do Pedido']!='EM ABERTO')&(tabelas_df['Estatico']['Data de Faturamento'].dt.year==data_atual.year)&(tabelas_df['Estatico']['Data de Faturamento'].dt.month==data_atual.month)].sum(),2)

    aberto=round(tabelas_df['Aberto']['Total Geral'].loc[(tabelas_df['Aberto']['Data do Pedido'].dt.year==data_atual.year)&(tabelas_df['Aberto']['Data do Pedido'].dt.month==data_atual.month)&(tabelas_df['Aberto']['Data do Pedido'].dt.day==data_atual.day)&(tabelas_df['Aberto']['Situação']=='AB')].sum())

    total=faturado+aberto

    tabelas_df['Pagar']['Contas']=tabelas_df['Pagar']['Contas'].apply(lambda info: str(info).strip())

    tabelas_df['Pagar']=tabelas_df['Pagar'].loc[~tabelas_df['Pagar']['Contas'].isin(base_contas)]

    valor_pago=round(tabelas_df['Pagar']['Valor Pago R$'].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==data_atual.month)].sum(),2)

    pago_anterior=round(tabelas_df['Pagar']['Valor Pago R$'].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==data_atual.month-1)].sum(),2)

    desconto=round(tabelas_df['Pagar']['Desconto R$'].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==data_atual.month)].sum(),2)

    despesa_rep=round(valor_pago/total,4)*100
    
    titulos_pagos=len(tabelas_df['Pagar']['Título'].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==data_atual.month)].unique().tolist())

    titulos_emitidos=len(tabelas_df['Pagar']['Título'].loc[(tabelas_df['Pagar']['Data de Emissão'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Emissão'].dt.month==data_atual.month)].unique().tolist())

    total_pago=valor_pago+desconto

    recebido=round(tabelas_df['Receber']['Pago R$'].loc[(tabelas_df['Receber']['Data de Pagamento'].dt.year==data_atual.year)&((tabelas_df['Receber']['Data de Pagamento'].dt.month==data_atual.month))].sum(),2)

    tit_venc_df=tabelas_df['Pagar'][['Data de Vencimento','Título R$']].loc[(tabelas_df['Pagar']['Data de Vencimento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Vencimento'].dt.month==data_atual.month)].groupby(['Data de Vencimento','Título R$'],as_index=False).sum()

    #valor_vencer=tit_venc_df['Título R$'].sum()

    margem=(tabelas_df['Estatistico']['MG %'].max())*100

    minimo=0

    maximo=100

    temp_dict={
        
        "Faturamento R$" :float(faturado),
        "Realizado R$" :float(aberto),
        "Total Vendido R$" :float(total),
        "Valor Pago R$" :float(valor_pago),
        "Desconto R$" :float(desconto),
        "Despesas x Total Vendido %" :float(despesa_rep),
        "Mínimo" :float(minimo),
        "Máximo" :float(maximo),
        "Títulos a Vencer" :float(titulos_vencidos),
        "Títulos Pagos" :float(titulos_pagos),
        "Título Emitidos" :float(titulos_emitidos),
        "Valor Pago + Desconto" :float(total_pago),
        'Recebimento R$':float(recebido),
        'Valor a Vencer R$':float(valor_vencer),
        'Despesas Anterior R$':float(pago_anterior),
        'Margem %':float(margem)
    }

    r=requests.post(url_base,json=temp_dict)

    print(r.status_code)

    pass

def Mensal(tabelas_df):

    url_base='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/a9d6d935-9bdf-442a-8ed8-4e9113d0810a/rows?key=lJI5W5ceTvuBVyNn0O2%2B5RVsGY%2FRF4pyP%2FcLPuJ6h0myFhBkXXYJzacHmkxM%2Bylw%2Fd7YMv5nr%2BUsnwX7p4de7A%3D%3D'

    tabelas_df['Pagar']=tabelas_df['Pagar'].loc[~tabelas_df['Pagar']['Contas'].isin(base_contas)]

    data_atual=data.HoraAtual()

    mensal_df=tabelas_df['Pagar'].loc[tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year]

    mensal_df=mensal_df[['Data de Pagamento','Valor Pago R$']].groupby(['Data de Pagamento'],as_index=False).sum()

    mensal_df['ID Mês']=mensal_df['Data de Pagamento'].dt.month

    mensal_df['Mês']=mensal_df.apply(lambda info: data.Mes(info['ID Mês']),axis=1)

    mensal_df=mensal_df[['ID Mês','Mês','Valor Pago R$']].groupby(['ID Mês','Mês'],as_index=False).sum()

    mensal_df['Pago Anterior R$']=mensal_df['ID Mês'].apply(lambda mes:

        tabelas_df['Pagar']['Valor Pago R$'].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==mes-1)].sum() if mes!=1 else tabelas_df['Pagar']['Valor Pago R$'].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year-1)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==12)].sum()
    )

    mensal_df['Cresc %']=mensal_df.apply(lambda info: round(((info['Valor Pago R$']/info['Pago Anterior R$'])-1),4)*100,axis=1)

    mensal_df['Vendas R$']=mensal_df['ID Mês'].apply(

        lambda mes:
        round(tabelas_df['Estatico']['Total Geral'].loc[(tabelas_df['Estatico']['Tipo de Operação']=='VENDAS')&(tabelas_df['Estatico']['Status do Pedido']!='EM ABERTO')&(tabelas_df['Estatico']['Data de Faturamento'].dt.year==data_atual.year)&((tabelas_df['Estatico']['Data de Faturamento'].dt.month==mes))].sum(),2)
    
    )

    mensal_df['Rep %']=mensal_df.apply(lambda info: round(((info['Valor Pago R$']/info['Vendas R$'])),4)*100,axis=1)

    mensal_df.sort_values('ID Mês',ascending=True,inplace=True) 

    requests.post(url=url_base,json=mensal_df.to_dict('records'))

    pass

def Grupos(tabelas_df):

    url_base={1:'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/a471c9e6-015a-4122-838a-26d7cec67922/rows?noSignUpCheck=1&key=J%2BRpdk64bGStNyGPazOA%2FjeW2K0Lt%2FH%2B4NXZRxJmW63qn3k42Q5c3mKF35wtCJRBum7ynHMXCdw7m9MbJYwP1A%3D%3D',2:'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/fd499e52-ed4d-414f-902b-0870147a9422/rows?noSignUpCheck=1&key=42cFexcACZ8rP3TpuWfyWrGehwmuTyxd0eQEKfP7x%2FteUHVARrDPNurVpphQZ%2Fr1deo2EKE2Yza6xFVr8B5DaQ%3D%3D',3:'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/e3c199ce-a346-4ea1-89d3-374d8feed3c2/rows?noSignUpCheck=1&key=9%2BIwFrRkWHEgoL25xvlEpdVoG3luZliBZFLv%2FOfInBfZutm8IF5kdKizAtnHTXyM6d9RwyEO56BWEhUS0SJlig%3D%3D'}

    indice=5

    tabelas_df['Pagar']=tabelas_df['Pagar'].loc[~tabelas_df['Pagar']['Contas'].isin(base_contas)]

    data_atual=data.HoraAtual()

    lista_valores=tabelas_df['Pagar'][['Valor Pago R$','Desconto R$','Total R$']].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==data_atual.month)].sum().to_dict()

    grupo_df=tabelas_df['Pagar'][['Grupo','Valor Pago R$','Desconto R$','Total R$']].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==data_atual.month)].groupby(['Grupo'],as_index=False).sum()

    grupo_df['Rep %']=grupo_df.apply(lambda info: round(info['Valor Pago R$']/lista_valores['Valor Pago R$'],4)*100,axis=1)

    grupo_df.sort_values('Valor Pago R$',ascending=False,inplace=True)

    requests.post(url=url_base[1],json=grupo_df.to_dict('records'))

    tp_conta=pd.DataFrame()

    for g in grupo_df['Grupo'].tolist():
        
        vl_pago=grupo_df['Valor Pago R$'].loc[grupo_df['Grupo']==g].sum()
            
        temp_df=tabelas_df['Pagar'][['Tipo de Conta','Valor Pago R$','Desconto R$','Total R$']].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==data_atual.month)&(tabelas_df['Pagar']['Grupo']==g)].groupby(['Tipo de Conta'],as_index=False).sum()
            
        temp_df.sort_values('Valor Pago R$',ascending=False,inplace=True,ignore_index=True)
        
        temp_df['Rep %']=round(temp_df['Valor Pago R$']/vl_pago,4)*100
        
        temp_df=temp_df.loc[temp_df['Rep %']>=indice]
        
        tp_conta=pd.concat([tp_conta,temp_df],axis=0,ignore_index=True)
        
        pass

    tp_conta.sort_values('Valor Pago R$',ascending=False,inplace=True,ignore_index=True)

    requests.post(url=url_base[2],json=tp_conta.to_dict('records'))

    contas_df=pd.DataFrame()

    for g in tp_conta['Tipo de Conta'].tolist():
        
        vl_pago=tp_conta['Valor Pago R$'].loc[tp_conta['Tipo de Conta']==g].sum()
            
        temp_df=tabelas_df['Pagar'][['Contas','Valor Pago R$','Desconto R$','Total R$']].loc[(tabelas_df['Pagar']['Data de Pagamento'].dt.year==data_atual.year)&(tabelas_df['Pagar']['Data de Pagamento'].dt.month==data_atual.month)&(tabelas_df['Pagar']['Tipo de Conta']==g)].groupby(['Contas'],as_index=False).sum()
            
        temp_df.sort_values('Valor Pago R$',ascending=False,inplace=True,ignore_index=True)
        
        temp_df['Rep %']=round(temp_df['Valor Pago R$']/vl_pago,4)*100
        
        temp_df=temp_df.loc[temp_df['Rep %']>=indice]
        
        contas_df=pd.concat([contas_df,temp_df],axis=0,ignore_index=True)
        
        pass

    contas_df.sort_values('Valor Pago R$',ascending=False,inplace=True,ignore_index=True)

    requests.post(url=url_base[3],json=contas_df.to_dict('records'))

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela()

    Consolidado(tabelas)

    Mensal(tabelas)

    Grupos(tabelas)

    pass