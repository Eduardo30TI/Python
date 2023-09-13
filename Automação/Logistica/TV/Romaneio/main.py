from Acesso import Login
from Query import Query
import pandas as pd
import requests

pd.set_option('display.max_columns',None)

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'Rota':
    
    """
    
    SELECT * FROM netfeira.vw_roteiros
    WHERE YEAR([Data da Montagem])=YEAR(GETDATE()) AND MONTH([Data da Montagem])=MONTH(GETDATE())
    ORDER BY [Data da Montagem]
    
    """,
    
    'Calendario':
    
    """
    
    SELECT * FROM netfeira.vw_calend
    WHERE YEAR(Data)=YEAR(GETDATE()) AND MONTH(Data)=MONTH(GETDATE())    
    
    """,
    
    'Log':
    
    """
    
    SELECT * FROM netfeira.vw_log_conta
    
    """,
    
    'Meta':
    
    """
    
    SELECT * FROM netfeira.vw_metas    
    
    """,

    'Vendas':

    """
    
    SELECT ev.[Total Venda],ev.Úteis,ev.Trabalhado,
    CONVERT(decimal(15,2),(ev.[Total Venda]/ev.Trabalhado)*ev.Úteis) AS Projeção
    FROM (

        SELECT SUM([Total Venda]) AS [Total Venda],
        (SELECT COUNT(Data)
        FROM netfeira.vw_calend calend
        WHERE YEAR(calend.Data)=YEAR(GETDATE()) AND MONTH(calend.Data)=MONTH(GETDATE()) AND [Dia Útil]=1) AS [Úteis],
        (
        SELECT COUNT([Data Trabalhada])-1
        FROM netfeira.vw_calend calend
        WHERE YEAR(calend.Data)=YEAR(GETDATE()) AND MONTH(calend.Data)=MONTH(GETDATE()) AND [Dia Útil]=1) AS [Trabalhado]
        FROM netfeira.vw_venda_estatico vda
        WHERE [Tipo de Operação]='VENDAS' AND YEAR(vda.[Data de Faturamento])=YEAR(GETDATE()) 
        AND MONTH(vda.[Data de Faturamento])=MONTH(GETDATE())

    )ev
    
    """
    
}

def Main(df):

    links={

        'Geral':
        
        'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/cbc36179-48ba-49e7-8ff3-3c3fe2f7e6e8/rows?noSignUpCheck=1&key=cKVRxRRIyeZPMqqmPTVqLFcW5okXr3vGq4oDdjPLengXn4j182HLm4OuEtLTSyUhZTjs5wVhei3VUAIerTwIbw%3D%3D',
        
        'Rota':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/7fd59e2d-04eb-4192-89db-95c2979ab6fd/rows?key=F83SV5YnvHSn4S865E95cKbC%2FF1WYDOkLlQ%2F6lZ%2Fr7NYY2Yk4%2BwInyIzqTGfALN8w2NCmGKF9RGNLkGZ%2BKzOJg%3D%3D'        

        }

    meta=df['Vendas']['Projeção'].sum()

    perc=df['Log']['Perc'].values[-1]

    df['Temp']=df['Rota'].groupby(['Romaneio','Frete Pago'],as_index=False).agg({'Pedido':'count'})

    frete=df['Temp']['Frete Pago'].sum()

    util=df['Calendario'].loc[df['Calendario']['Dia Útil']==1,'Data'].count()

    meta_frete=round(meta*perc,2)

    meta_dia=round(meta_frete/util,2)

    df['Semana']=df['Calendario'].loc[df['Calendario']['Dia Útil']==1].groupby(['Semana Ano'],as_index=False).agg({'Dia Útil':'count'})

    df['Semana']['Meta Semanal']=df['Semana']['Dia Útil']*meta_dia

    df['Semana']['Data Mín']=df['Semana']['Semana Ano'].apply(lambda info: df['Calendario']['Data'].loc[df['Calendario']['Semana Ano']==info].min())

    df['Semana']['Data Máx']=df['Semana']['Semana Ano'].apply(lambda info: df['Calendario']['Data'].loc[df['Calendario']['Semana Ano']==info].max())

    df['Temp']=df['Rota'].groupby(['Romaneio','Frete Pago','Data da Montagem'],as_index=False).agg({'Pedido':'count'})

    df['Semana']['Frete R$']=df['Semana'].apply(lambda info: df['Temp']['Frete Pago'].loc[df['Temp']['Data da Montagem'].between(info['Data Mín'],info['Data Máx'])].sum(),axis=1)

    df['Semana']['Dif']=round(df['Semana']['Meta Semanal']-df['Semana']['Frete R$'],2)

    soma=0

    valores=[]

    for i,total in enumerate(df['Semana']['Dif']):
                
        if(i==0):
            
            valores.append(0)
            
            continue
            
        dif=df['Semana']['Dif'].iloc[i-1].sum()
        
        valores.append(dif)
        
        pass

    df['Semana']['Ant Dif']=valores

    df['Semana']['Meta Semanal']=round(df['Semana']['Meta Semanal']+df['Semana']['Ant Dif'],2)

    df['Semana']['Dif']=round(df['Semana']['Meta Semanal']-df['Semana']['Frete R$'],2)

    df['Semana'].drop(columns=['Ant Dif'],inplace=True)

    df['Semana']['Perc']=round(df['Semana']['Frete R$']/df['Semana']['Meta Semanal'],2)*100

    df['Semana'].loc[df['Semana']['Frete R$']<=0,'Dif']=0

    semana_ano=df['Semana'].loc[df['Semana']['Frete R$']>0,'Semana Ano'].max()

    meta_semanal=df['Semana'].loc[df['Semana']['Semana Ano']==semana_ano,'Meta Semanal'].sum()

    realizado_semanal=df['Semana'].loc[df['Semana']['Semana Ano']==semana_ano,'Frete R$'].sum()

    saldo_semanal=df['Semana'].loc[df['Semana']['Semana Ano']==semana_ano,'Dif'].sum()

    perc_meta=round(frete/meta_frete,4)*100

    perc_semanal=round(realizado_semanal/meta_semanal,4)*100

    saldo=meta_frete-frete

    df['Temp']=df['Rota'].groupby(['Romaneio','Rota','Frete Pago'],as_index=False).agg({'Pedido':'count'})

    df['Regiao']=df['Temp'].groupby(['Rota'],as_index=False).agg({'Frete Pago':'sum'})

    df['Regiao']['Pedidos']=df['Regiao']['Rota'].apply(lambda info: len(df['Rota']['Pedido'].loc[df['Rota']['Rota']==info].unique().tolist()))

    df['Regiao'].sort_values('Pedidos',ascending=False,inplace=True)

    df['Regiao']['Clientes']=df['Regiao']['Rota'].apply(lambda info: len(df['Rota']['ID Cliente'].loc[df['Rota']['Rota']==info].unique().tolist()))

    temp_dict={

        "Mín" :float(0),
        "Máx" :float(100),
        "Meta" :float(meta_frete),
        "Meta Semanal" :float(meta_semanal),
        "Perc Meta" :float(perc_meta),
        "Perc Semanal" :float(perc_semanal),
        "Realizado" :float(frete),
        "Realizado Semanal" :float(realizado_semanal),
        "Saldo" :float(saldo),
        "Saldo Semanal" :float(saldo_semanal)
        }

    requests.post(url=links['Geral'],json=temp_dict)

    requests.post(url=links['Rota'],json=df['Regiao'].to_dict('records'))



    pass


if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass