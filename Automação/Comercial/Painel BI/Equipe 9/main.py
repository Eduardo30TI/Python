from Acesso import Login
from Query import Query
import pandas as pd
import requests
import time
import os
from glob import glob

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

links={'Geral':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/220441ac-f887-4ef5-9ddb-4d84e0b5c7a0/rows?noSignUpCheck=1&key=hD9mYpvCj%2FbmyoM1biuGj8KpmOXOcbBBumogzXvTUQR9EPmx9rXA5CjBzu7BsBrpnNro0tqFRZzTku1Z3ux6OQ%3D%3D',

'Metas':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/1f33007f-ebf4-4493-963e-6b5f330c2fe5/rows?key=iTQ4vg%2BgQnyaTUEKjms3liccmnFSg9KRJWUSYjHJSrlWAI0olDu9152AGNAzQx4EmUwHVTTi9Jl9qx%2Fyl6LAqQ%3D%3D',

'Positivado':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/35a5d5f3-50f4-48b1-aa01-ce0d7fde0616/rows?key=u0hjeJ2LzogcNOmBFIqee5c%2B5qsOldzmI%2F0YddvP87vh1pu0XPVxt%2B5OwXaOZ%2FRt8cTzV%2BP8lk4FkB2EZqZz7w%3D%3D'

}

querys={

    'TargetEstatico':

    """
    
    DECLARE @DTBASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=CONCAT(YEAR(@DTFIM),'-',MONTH(@DTFIM),'-01')

    SELECT * FROM netfeira.vw_targetestatico
    WHERE [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM
    ORDER BY [Data de Faturamento]

    
    """,
    
    'Aberto':
    
    """
    
    SELECT * FROM netfeira.vw_aberto
    WHERE [Data do Pedido]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)
    
    """,
    
    'Meta':
    
    """
    
    SELECT * FROM netfeira.vw_metas
    
    """,
    
    'Calendario':
    
    
    """
    
    SELECT * FROM netfeira.vw_calend
    WHERE YEAR(Data)=YEAR(GETDATE()) AND MONTH(Data)=MONTH(GETDATE())
    
    """,
    
    'Vendedor':
    
    """
    
    SELECT * FROM netfeira.vw_vendedor
    
    """,
    
    
    'Supervisor':
    
    
    """
    
    SELECT * FROM netfeira.vw_supervisor
    
    """,
    
    'Produto':
    
    """
    
    SELECT * FROM netfeira.vw_produto
    
    """,
    
    'Carteira':
    
    """
    
    SELECT * FROM netfeira.vw_carteira
    WHERE Dias<366 AND [Status do Cliente]='ATIVO' 
    
    """,

    'MIX':
    
    """
    
    SELECT * FROM netfeira.vw_mix
    
    """    

}

def Main(tabelas_df):

    vendedores = {

        'JUVILARE':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/b6bfb40b-64b4-4528-b0a6-14a65ac5d1b6/rows?key=nksVnKnteVhdXAOrS9mjXrnYs6aR2%2FIv2WgxPPrDO81NLSy65DmREMKvZ3AhOhhPMgJhk3blUBlJHBnOFe7kyA%3D%3D',

        'LETICIAG':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/7b71723b-1908-4b7c-9453-38179085ebe1/rows?key=xwzAuH5jRDuBXbrCysy5kAVwsicqZe4bJ5LeCK6gAui%2BxnEC8I2aLN13IdIhqzbHA9u2DvmjXPRsL%2FVJgbATkg%3D%3D',

        'MAYRAQS':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/52f68bc0-da36-47f1-985e-a14b6f2364ef/rows?key=w%2BpxrJ8a5IumB%2F81gzujJ0gosUM4BPWg3ISFZl7zK5sj7ak6dyw01aLpsNsSrsI3wBYMuAhMOCCxgYLnXGqJpQ%3D%3D',

        'MILENA': 'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/cbb41929-92fd-4d31-aaf4-1157dd8bc2dd/rows?key=ivUVANsupg%2BACMzgjVy28pO2hwP582Ff2fA0wvdV08jUKI6MT%2B527BTmmbERNAM8d60fxZu7mdEtaRjPGRKoDA%3D%3D',

        'RAQUELSO':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/269ed601-9860-4778-8be0-1cd2045a5884/rows?key=JnJTxSe0OuHqeSLg%2F99iwTnA%2FVp9l1mOWHmLKJ%2FBOItR5sZA0baHtOJqGGBwChsY7s5xgT%2BmZDkbzZfo9yU8lg%3D%3D',

        'RENATAAP':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/7c08b06b-1f62-49b8-8159-384f43e1274b/rows?key=cRri7LYxFMp%2B%2BcDTK3125yS39PKMhEP%2FCRmRDt%2B6%2F2LHcM8Tp%2FuCIdM8OSQdmsNMN7eC%2BGFB7C6AVK0E8gW3nw%3D%3D',

        'TALITA': 'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/599f9dd2-1fce-48f5-a6ed-574ee922da5e/rows?key=pBdYBEv%2F4ohKGGZkYoBnxWrLUKnQxEhGp1twdA6BnqUuf%2FL4ytASq6BIj2d%2F%2BtmP%2BiW%2F3QMr4WQgym9br8568w%3D%3D',

        'THAISFRE': 'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/954cdbf3-9398-433f-baa4-3b243b1eb066/rows?key=taEkQcKY3ublqEW%2BBLWEVDDyAX7M6YjgyyfhA7NaOi8aXtCy73IqEJNrLgw90qQgHZrOaNEfSsJzPXUI1V6nrQ%3D%3D',

        'MAIARARO':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/01c94e36-118b-4d7f-bfc1-564e8db0eba9/rows?noSignUpCheck=1&key=0kbFlqFn5Rw5dvTpBouh2jPQH6J3I%2B4cLSbu7yJ1P0RwpwsWIhqmqm2cBotXTOfI1np%2F3FcbQLMsXM83kRVu7A%3D%3D'


    }

    df=pd.DataFrame()

    codigos=[]

    supervisor_df=pd.DataFrame()

    supervisor_df=tabelas_df['Supervisor'].loc[tabelas_df['Supervisor']['Equipe'].str.contains('9')]

    vendedor_df=pd.DataFrame()

    vendedor_df=tabelas_df['Vendedor'].merge(supervisor_df,on='ID Equipe',how='inner')

    vendedor_df=vendedor_df.loc[vendedor_df['Status do Vendedor']=='ATIVO']

    meta_df=pd.DataFrame()

    meta_df=vendedor_df.merge(tabelas_df['Meta'],on='ID Vendedor',how='inner')

    meta_df=meta_df.loc[meta_df['Meta R$']>0]    
    
    contagem=len(meta_df['ID Vendedor'].loc[~meta_df['ID Vendedor'].isin(codigos)].unique().tolist())
    
    if(contagem>0):

        meta_df=meta_df.loc[~meta_df['ID Vendedor'].isin(codigos)]

        pass

    else:

        df=pd.DataFrame()

        pass

    meta_df.sort_values('Meta R$',ascending=False,inplace=True)

    calend_df=pd.DataFrame()

    calend_df=tabelas_df['Calendario']

    uteis=len(calend_df['Data'].loc[calend_df['Dia Útil']==True].unique().tolist())

    trabalhado=len(calend_df['Data Trabalhada'].loc[(calend_df['Dia Útil']==True)&(~calend_df['Data Trabalhada'].isnull())].unique().tolist())-1

    restante=uteis-trabalhado

    for indice,linha in meta_df.iterrows():

        try:
        
            vendas_df=pd.DataFrame()
            
            vendas_df=tabelas_df['TargetEstatico'].loc[(tabelas_df['TargetEstatico']['ID Vendedor']==linha['ID Vendedor'])&(tabelas_df['TargetEstatico']['Tipo de Operação']=='VENDAS')]

            codigo=linha['ID Vendedor']
            
            aberto_df=pd.DataFrame()
            
            aberto_df=tabelas_df['Aberto'].loc[tabelas_df['Aberto']['ID Vendedor']==linha['ID Vendedor']]

            #mix

            produto_df=pd.DataFrame()

            produto_df=tabelas_df['MIX'].loc[tabelas_df['MIX']['ID Vendedor']==linha['ID Vendedor']]

            produto_df=produto_df.merge(tabelas_df['Produto'],on='SKU',how='inner')[['SKU','Produto', 'Seq', 'Positivado', 'Qtde']]

            produto_df.loc[produto_df['Positivado']==0,'Qtde']=0

            mix_positivado=len(produto_df['SKU'].loc[produto_df['Positivado']==1].tolist())

            mix_faltante=len(produto_df['SKU'].loc[produto_df['Positivado']==0].tolist())

            mix_geral=len(produto_df['SKU'].tolist())

            mix_perc=round(mix_positivado/mix_geral,4)*100
            
            situacao_df=pd.DataFrame()
            
            situacao_df=vendas_df[['Situação','Total Venda']].groupby(['Situação'],as_index=False).sum()
                
            situacao_df['Cliente']=situacao_df['Situação'].apply(lambda info: len(vendas_df['ID Cliente'].loc[vendas_df['Situação']==info].unique().tolist()))
            
            situacao_df['Pedido']=situacao_df['Situação'].apply(lambda info: len(vendas_df['Pedido'].loc[vendas_df['Situação']==info].unique().tolist()))
            
            situacao_df['MIX']=situacao_df['Situação'].apply(lambda info: len(vendas_df['SKU'].loc[vendas_df['Situação']==info].unique().tolist()))

            situacao_df.loc[situacao_df['Situação']!='FATURADO','Cliente']=situacao_df['Cliente'].loc[situacao_df['Situação']!='FATURADO']*-1
            
            situacao_df.loc[situacao_df['Situação']!='FATURADO','Pedido']=situacao_df['Pedido'].loc[situacao_df['Situação']!='FATURADO']*-1
            
            situacao_df.loc[situacao_df['Situação']!='FATURADO','MIX']=situacao_df['MIX'].loc[situacao_df['Situação']!='FATURADO']*-1
            
            cliente=situacao_df['Cliente'].sum()
                    
            pedido=situacao_df['Pedido'].sum()
            
            mix=situacao_df['MIX'].sum()
            
            meta=linha['Meta R$']
            
            faturado=vendas_df['Total Venda'].sum()
            
            perc_meta=round(faturado/meta,4)*100
            
            carteira=len(tabelas_df['Carteira']['ID Cliente'].loc[(tabelas_df['Carteira']['ID Vendedor']==linha['ID Vendedor'])].unique().tolist())
            
            qtd_cli=cliente if cliente>0 else 0
            
            perc_carteira=round(qtd_cli/carteira,4)*100
            
            dif_cart=carteira-cliente
            
            minimo=0
            
            maximo=100

            ticket=round(faturado/pedido,2)

            dif_meta=round(faturado-meta,2)

            projecao=round((faturado/trabalhado)*uteis,2)
            
            #pedidos em aberto atual
            
            atendimento=len(aberto_df['ID Cliente'].unique().tolist())
            
            pedido_real=len(aberto_df['Pedido'].unique().tolist())
            
            realizado=aberto_df['Total Venda'].sum()
            
            meta_diaria=round(meta/uteis,2)
            
            em_aberto=aberto_df['Total Venda'].loc[aberto_df['Situação']=='AB'].sum()
            
            total=round(faturado+em_aberto,2)
            
            perc_diario=round(realizado/meta_diaria,4)*100

            dif_diario=round(realizado-meta_diaria,2)

            kg_real=aberto_df['Peso Bruto KG'].sum()
            
            temp_dict={

            "Cliente" :float(cliente),
            "Pedido" :float(pedido),
            "Meta" :float(meta),
            "Ticket" :float(ticket),
            "Faturado" :float(faturado),
            "Meta %" :float(perc_meta),
            "Dif Meta" :float(dif_meta),
            "Projeção" :float(projecao),
            "Atendimento" :float(atendimento),
            "Pedido Realizado" :float(pedido_real),
            "Meta Diária" :float(meta_diaria),
            "KG Vendido" :float(kg_real),
            "Diária %" :float(perc_diario),
            "Dif Diário" :float(dif_diario),
            "Realizado R$" :float(realizado),
            "Em Aberto R$" :float(em_aberto),
            "Faturado + Em Aberto" :float(total),
            "Carteira" :float(carteira),
            "Dif Carteira" :float(dif_cart),
            "Carteira %" :float(perc_carteira),
            "Mínimo" :float(minimo),
            "Máximo" :float(maximo),
            "MIX Positivado":float(mix_positivado),
            "MIX Geral":float(mix_geral),
            "MIX Faltante":float(mix_faltante),
            "MIX Perc":float(mix_perc)

            }

            requests.post(url=vendedores[str(codigo).strip()],json=temp_dict)
            
            pass

        except Exception as erro:

            continue

            pass

        #break
        
        pass

    pass


if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass