from os import link
import pandas as pd
from Acesso import Login
from Query import Query
from datetime import datetime,timedelta
import requests

pd.set_option('display.max_columns',None)

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'TabMargem':
    
    """
    
    SELECT * FROM netfeira.vw_targetmargem
    
    """,
    
    'SELLIN':
    
    """
    
    SELECT * FROM netfeira.vw_sellin
    WHERE Empresa='NETFEIRA' AND NOT [Tipo de Entrada] LIKE '%DEVO%'

    """,
    
    'Metas':
    
    """
    
    SELECT * FROM netfeira.vw_metas
    
    """,
    
    'Calendario':
    
    """
    
    SELECT * FROM netfeira.vw_calend
    WHERE Ano=YEAR(GETDATE()) AND [ID Mês]=MONTH(GETDATE())
    
    """
    
    
}

def Main(tabelas_df):

    links={

        'Consolidado':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/681cd50e-2654-45ee-863f-c044f7eec2e2/rows?key=t0IP0Jaso%2FMFoWqq7%2BMhle2tUFMVDELp%2F%2BlFpqVJnjcChC7p1mQdI57pZ94B9J9P7Ch2KrQojZOSQRrvRjsiLw%3D%3D',

        'Produto':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/da366fcf-96da-421b-ab36-6f3aeaa6307c/rows?key=pBvoD1D6QmzpF%2BCmuXmTWi9iC1HL9SN0jpV2WT%2BIbP%2F3hI%2FrwHS%2BX817%2F9mn5vYD%2FEITFooXpjIZz%2BUc5mwNPw%3D%3D'
    }

    #consolidado

    perc_meta=1-round(tabelas_df['TabMargem']['Margem Média'].mean(),4)

    total=tabelas_df['Metas']['Meta R$'].sum()

    val_meta=round(total*perc_meta,2)

    tabelas_df['Semana Ano']=tabelas_df['Calendario'][['Semana Ano','Dia','Data Trabalhada']].loc[tabelas_df['Calendario']['Dia Útil']==True].groupby(['Semana Ano'],as_index=False).count()

    tabelas_df['Semana Ano']['Positivado']=tabelas_df['Semana Ano'].apply(lambda info: 1 if info['Dia']==info['Data Trabalhada'] else 0,axis=1)

    semana_util=tabelas_df['Semana Ano']['Semana Ano'].count()

    semana_trab=tabelas_df['Semana Ano']['Semana Ano'].loc[tabelas_df['Semana Ano']['Positivado']==1].count()

    dia_util=tabelas_df['Semana Ano']['Dia'].sum()

    valores=[]

    for i in tabelas_df['Semana Ano']['Semana Ano'].tolist():
        
        list_datas=tabelas_df['Calendario']['Data'].loc[tabelas_df['Calendario']['Semana Ano']==i].loc[tabelas_df['Calendario']['Dia Útil']==True].tolist()
        
        val_semana=round(tabelas_df['SELLIN']['Total NFe'].loc[(tabelas_df['SELLIN']['Tipo']=='PADRAO')&(tabelas_df['SELLIN']['Data de Recebimento'].isin(list_datas))].sum(),2)
        
        valores.append(val_semana)
        
        pass

    tabelas_df['Semana Ano']['Meta Semanal']=round((val_meta/dia_util)*tabelas_df['Semana Ano']['Dia'],2)

    tabelas_df['Semana Ano']['Valor Semanal']=valores

    tabelas_df['Semana Ano']['Dif Semanal']=tabelas_df['Semana Ano']['Meta Semanal']-tabelas_df['Semana Ano']['Valor Semanal']

    for i,val in enumerate(tabelas_df['Semana Ano']['Semana Ano'].tolist()):
        
        if(i==0):
            
            valores.append(0)
            
            pass
        
        else:
            
            soma=tabelas_df['Semana Ano']['Dif Semanal'].loc[tabelas_df['Semana Ano']['Semana Ano']==(val-1)].sum()
                    
            tabelas_df['Semana Ano'].loc[tabelas_df['Semana Ano']['Semana Ano']==val,'Meta Semanal']=tabelas_df['Semana Ano']['Meta Semanal'].loc[tabelas_df['Semana Ano']['Semana Ano']==val]+soma
            
            pass
        
        pass

    tabelas_df['Semana Ano']['Dif Semanal']=tabelas_df['Semana Ano']['Meta Semanal']-tabelas_df['Semana Ano']['Valor Semanal']

    tabelas_df['Semana Ano']['Perc %']=round(tabelas_df['Semana Ano']['Valor Semanal']/tabelas_df['Semana Ano']['Meta Semanal'],4)*100

    tabelas_df['Semana Ano'].loc[tabelas_df['Semana Ano']['Perc %'].isnull(),'Perc %']=0

    #curva abc

    semana_atu=tabelas_df['Calendario']['Semana Ano'].loc[(tabelas_df['Calendario']['Ano']==datetime.now().year)&(tabelas_df['Calendario']['ID Mês']==datetime.now().month)&(tabelas_df['Calendario']['Dia']==datetime.now().day)].max()

    list_datas=tabelas_df['Calendario']['Data'].loc[tabelas_df['Calendario']['Semana Ano']==semana_atu].loc[tabelas_df['Calendario']['Dia Útil']==True].tolist()    

    dt_atual=datetime.now()-timedelta(days=1)

    dt_ant=datetime.now()-timedelta(days=7)

    tabelas_df['Consolidado']=tabelas_df['SELLIN'].loc[(tabelas_df['SELLIN']['Tipo']=='PADRAO')&(tabelas_df['SELLIN']['Data de Recebimento'].between(dt_ant,dt_atual))]

    tabelas_df['Consolidado']=tabelas_df['Consolidado'][['SKU','Produto','Fabricante','Total NFe']].groupby(['SKU','Produto','Fabricante'],as_index=False).sum()

    tabelas_df['Consolidado'].sort_values('Total NFe',ascending=False,ignore_index=True,inplace=True)

    valores=[]

    soma=0

    total=tabelas_df['Consolidado']['Total NFe'].sum()

    for val in tabelas_df['Consolidado']['Total NFe'].tolist():
        
        soma+=val
        
        valores.append(soma)    
        
        pass

    tabelas_df['Consolidado']['Acumulado']=valores

    tabelas_df['Consolidado']['Total']=total

    tabelas_df['Consolidado']['Perc %']=round(tabelas_df['Consolidado']['Acumulado']/tabelas_df['Consolidado']['Total'],4)*100

    tabelas_df['Consolidado']['Classificação']=tabelas_df['Consolidado']['Perc %'].apply(Classificacao)

    tabelas_df['Classificação ABC']=tabelas_df['Consolidado'].groupby(['Classificação'],as_index=False).agg({'Total NFe':'sum','SKU':'count'})

    tabelas_df['Lista']=tabelas_df['SELLIN'][['SKU','Produto','Fabricante','Total NFe']].loc[(tabelas_df['SELLIN']['Tipo']=='PADRAO')&(tabelas_df['SELLIN']['Data de Recebimento'].isin(list_datas))].groupby(['SKU','Produto','Fabricante'],as_index=False).sum()

    tabelas_df['Consolidado']=tabelas_df['Consolidado'][['SKU','Classificação']]

    tabelas_df['Lista']=tabelas_df['Lista'].merge(tabelas_df['Consolidado'],on='SKU',how='left')

    tabelas_df['Lista'].loc[tabelas_df['Lista']['Classificação'].isnull(),'Classificação']='C'

    tabelas_df['Lista'].sort_values('Total NFe',ascending=False,ignore_index=True,inplace=True)

    tabelas_df['Classificação ABC']['Entradas']=tabelas_df['Classificação ABC']['Classificação'].apply(lambda info: tabelas_df['Lista']['Total NFe'].loc[tabelas_df['Lista']['Classificação']==info].sum())

    tabelas_df['Classificação ABC']['Produtos']=tabelas_df['Classificação ABC']['Classificação'].apply(lambda info: len(tabelas_df['Lista']['SKU'].loc[tabelas_df['Lista']['Classificação']==info].unique().tolist()))

    tabelas_df['Classificação ABC']=tabelas_df['Classificação ABC'][['Classificação','Entradas','Produtos']]

    total=round(tabelas_df['Classificação ABC']['Entradas'].sum(),2)

    tabelas_df['Classificação ABC']['Perc %']=round(tabelas_df['Classificação ABC']['Entradas']/total,4)*100

    tabelas_df['Classificação ABC'].loc[tabelas_df['Classificação ABC']['Perc %'].isnull(),'Perc %']=0

    #analise consolidado

    val_total=round(tabelas_df['SELLIN']['Total NFe'].loc[(tabelas_df['SELLIN']['Tipo']=='PADRAO')&(tabelas_df['SELLIN']['Data de Recebimento'].dt.year==datetime.now().year)&(tabelas_df['SELLIN']['Data de Recebimento'].dt.month==datetime.now().month)].sum(),2)

    perc_total=round(val_total/val_meta,4)*100 if val_meta>0 else 0

    meta_semanal=tabelas_df['Semana Ano']['Meta Semanal'].loc[tabelas_df['Semana Ano']['Semana Ano']==semana_atu].max()

    val_semanal=tabelas_df['Semana Ano']['Valor Semanal'].loc[tabelas_df['Semana Ano']['Semana Ano']==semana_atu].max()

    perc_semanal=tabelas_df['Semana Ano']['Perc %'].loc[tabelas_df['Semana Ano']['Semana Ano']==semana_atu].max()

    dif_mes=val_meta-val_total

    dif_semanal=tabelas_df['Semana Ano']['Dif Semanal'].loc[tabelas_df['Semana Ano']['Semana Ano']==semana_atu].max()

    val_a=tabelas_df['Classificação ABC']['Entradas'].loc[tabelas_df['Classificação ABC']['Classificação']=='A'].max()

    perc_a=tabelas_df['Classificação ABC']['Perc %'].loc[tabelas_df['Classificação ABC']['Classificação']=='A'].max()

    val_b=tabelas_df['Classificação ABC']['Entradas'].loc[tabelas_df['Classificação ABC']['Classificação']=='B'].max()

    perc_b=tabelas_df['Classificação ABC']['Perc %'].loc[tabelas_df['Classificação ABC']['Classificação']=='B'].max()

    val_c=tabelas_df['Classificação ABC']['Entradas'].loc[tabelas_df['Classificação ABC']['Classificação']=='C'].max()

    perc_c=tabelas_df['Classificação ABC']['Perc %'].loc[tabelas_df['Classificação ABC']['Classificação']=='C'].max()

    temp_dict=[
        {
                                    
            "Máx" :float(100),
            "Mín" :float(0),
            "Meta %" :float(perc_total),
            "Meta R$" :float(val_meta),
            "Semana Útil" :float(semana_util),
            "Semana Trabalhada" :float(semana_trab),
            "Meta Semanal R$" :float(meta_semanal),
            "Total Semanal" :float(val_semanal),
            "Semanal %" :float(perc_semanal),
            "Total R$" :float(val_total),
            "Á Realizar R$" :float(dif_mes),
            "Á Realizar Semana" :float(dif_semanal),
            "A R$":float(val_a),
            "B R$":float(val_b),
            "C R$":float(val_c),
            "A %":float(perc_a),
            "B %":float(perc_b),
            "C %":float(perc_c)

        }
    ]

    requests.post(url=links['Consolidado'],json=temp_dict)
    
    tabelas_df['Lista']=tabelas_df['Lista'].loc[tabelas_df['Lista']['Classificação']!='C']

    requests.post(url=links['Produto'],json=tabelas_df['Lista'].to_dict('records'))

    pass

def Classificacao(val):
    
    if(val<=80):
        
        tipo='A'
        
        pass
    
    elif(val<=95):
        
        tipo='B'
        
        pass
    
    else:
        
        tipo='C'
        
        pass
    
    return tipo
    
    
    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass