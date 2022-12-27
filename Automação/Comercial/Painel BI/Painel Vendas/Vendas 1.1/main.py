from Acesso import Login
from Query import Query
import pandas as pd
import requests

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

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
    
    """

}

def Main(tabelas_df):

    vendas_df=pd.DataFrame()

    vendas_df=tabelas_df['TargetEstatico'].loc[tabelas_df['TargetEstatico']['Tipo de Operação']=='VENDAS']

    base_df=pd.DataFrame()

    base_df=vendas_df[['Situação','Total Venda']].groupby(['Situação'],as_index=False).sum()

    base_df['Pedido']=base_df['Situação'].apply(lambda info: len(vendas_df['Pedido'].loc[vendas_df['Situação']==info].unique().tolist()))

    base_df['Cliente']=base_df['Situação'].apply(lambda info: len(vendas_df['ID Cliente'].loc[vendas_df['Situação']==info].unique().tolist()))

    base_df['MIX']=base_df['Situação'].apply(lambda info: len(vendas_df['SKU'].loc[vendas_df['Situação']==info].unique().tolist()))

    base_df.loc[base_df['Situação']!='FATURADO','Pedido']=base_df.loc[base_df['Situação']!='FATURADO','Pedido']*-1

    base_df.loc[base_df['Situação']!='FATURADO','Cliente']=base_df.loc[base_df['Situação']!='FATURADO','Cliente']*-1

    base_df.loc[base_df['Situação']!='FATURADO','MIX']=base_df.loc[base_df['Situação']!='FATURADO','MIX']*-1

    #calculo

    pedido=base_df['Pedido'].sum()

    cliente=base_df['Cliente'].sum()

    faturado=round(base_df['Total Venda'].sum(),2)

    meta=round(tabelas_df['Meta']['Meta R$'].sum(),2)

    meta=meta if meta!='' else 0

    perc_meta=round(faturado/meta,4)*100 if meta>0 else 0

    dif_meta=faturado-meta

    ticket=round(faturado/pedido,2)

    calend_df=pd.DataFrame()

    calend_df=tabelas_df['Calendario']

    uteis=len(calend_df['Data'].loc[calend_df['Dia Útil']==True].unique().tolist())

    trabalhado=len(calend_df['Data Trabalhada'].loc[(calend_df['Dia Útil']==True)&(~calend_df['Data Trabalhada'].isnull())].unique().tolist())-1

    restante=uteis-trabalhado

    projecao=(faturado/trabalhado)*uteis if trabalhado>0 else 0

    meta_diaria=round(meta/uteis,2)

    aberto_df=pd.DataFrame()

    aberto_df=tabelas_df['Aberto']

    atendimento=len(aberto_df['ID Cliente'].unique().tolist())

    realizado=round(aberto_df['Total Geral'].sum(),2)

    ped_realizado=len(aberto_df['Pedido'].unique().tolist())

    perc_diario=round(realizado/meta_diaria,4)*100 if meta_diaria>0 else 0

    real_aberto=round(aberto_df['Total Geral'].loc[aberto_df['Situação']=='AB'].sum(),2)

    total=faturado+real_aberto

    kg_real=round(aberto_df['Peso Bruto KG'].sum(),3)

    mix=len(aberto_df['SKU'].unique().tolist())

    dif_diario=round(realizado-meta_diaria,2)

    temp_dict={


        "Pedido" :float(pedido),
        "Cliente" :float(cliente),
        "Faturado" :float(faturado),
        "Meta" :float(meta),
        "Meta %" :float(perc_meta),
        "Diferença R$" :float(dif_meta),
        "Projeção" :float(projecao),
        "Ticket Médio" :float(ticket),
        "Atendimento" :float(atendimento),
        "Pedido Realizado" :float(ped_realizado),
        "MIX" :float(mix),
        "Meta Diária" :float(meta_diaria),
        "Realizado R$" :float(realizado),
        "Dias Úteis" :float(uteis),
        "Dias Trabalhados" :float(trabalhado),
        "Dias Restante" :float(restante),
        "Diário %" :float(perc_diario),
        "Valor Mínimo" :float(0),
        "Valor Máximo" :float(100),
        "Faturado + Em Aberto" :float(total),
        "Dif Diário R$" :float(dif_diario),
        "KG Vendido" :float(kg_real),
        "Em Aberto R$" :float(real_aberto)

        }

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/536ad588-cc04-44a3-a923-cfd7e4e8947b/rows?noSignUpCheck=1&key=fCKjsjEvlHfEFafNL%2Bgqhywm6ff%2BMOLBtQ98s%2BO28sAOptXIZjfwCEl68ppYj91pz9L%2BVfkM%2B%2FA5ZW%2FUf0LXpg%3D%3D',json=temp_dict)

    equipes_df=pd.DataFrame()

    equipes_df=tabelas_df['Vendedor'].merge(tabelas_df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe','Supervisor']]

    equipes_df=equipes_df.merge(tabelas_df['Meta'],on='ID Vendedor',how='inner')

    equipes_df=equipes_df.loc[equipes_df['Meta R$']>0]

    equipes_df.loc[:,'Diário']=round(equipes_df['Meta R$']/uteis,2)

    vendedores_df=pd.DataFrame()

    vendedores_df=aberto_df[['ID Vendedor','Total Venda']].groupby(['ID Vendedor'],as_index=False).sum()

    equipes_df=equipes_df.merge(vendedores_df,on='ID Vendedor',how='left')

    equipes_df.loc[equipes_df['Total Venda'].isnull(),'Total Venda']=0

    equipes_df.loc['Diferença']=0

    if(len(equipes_df)>0):

        equipes_df['Diferença']=equipes_df.apply(lambda info: info['Diário']-info['Total Venda'],axis=1)

        pass

    consolidado_df=pd.DataFrame()

    consolidado_df=equipes_df[['Supervisor','Diferença']].groupby(['Supervisor'],as_index=False).sum()

    #consolidado_df['Diferença']=consolidado_df['Diferença']*-1

    consolidado_df.sort_values('Diferença',ascending=False,inplace=True)

    consolidado_df=consolidado_df.loc[consolidado_df['Diferença']>0]

    if(len(consolidado_df)<=0):

        requests.delete(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/2f9e1df4-8bb3-47bf-8378-83a41c60f706/rows?key=n0VLoDleUsQkNQ5Y096uXR9fqdFmZajV9ja7LMDiFjby%2BaSAXG3qtjR8VRM2%2FZJCUhaXNZwHTQYZPhJG25ojkg%3D%3D')

        pass

    else:

        requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/2f9e1df4-8bb3-47bf-8378-83a41c60f706/rows?key=n0VLoDleUsQkNQ5Y096uXR9fqdFmZajV9ja7LMDiFjby%2BaSAXG3qtjR8VRM2%2FZJCUhaXNZwHTQYZPhJG25ojkg%3D%3D',json=consolidado_df.to_dict('records'))

        pass

    consolidado_df=equipes_df[['Equipe','Total Venda','Diferença']].groupby(['Equipe'],as_index=False).sum()

    consolidado_df.rename(columns={'Total Venda':'Realizado R$'},inplace=True)

    consolidado_df.sort_values('Realizado R$',ascending=False,inplace=True)

    consolidado_df=consolidado_df[['Equipe','Realizado R$']].loc[consolidado_df['Diferença']<=0]

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/0aa821da-ebc0-405b-a5e8-bb8ee2f860eb/rows?key=QdD%2BwkBQ4eyCc23qRz0AHIyii2pqnxcDzrNt%2FY8obZWuvMWtcXIE7Bsj2EHSReM9UasoYqtTYaGucevHp4Z5iA%3D%3D',json=consolidado_df.to_dict('records'))
        
    pass

def Equipes(tabelas_df):

    lista_equipe={'0009':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/bb178347-7076-4750-8cea-fcff4c09b8ce/rows?key=nNj7e4Qe7bPBet7X5msDSjPkF9%2F7JQUhfxDjr2MJJ22vEZsOfL%2BGrB%2FJxYcB4T17BOt8j04%2FNr6mrxcaDrR4pg%3D%3D',
    '0003':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/8cd03dc3-3bcb-4cb4-88da-21edeaa11ac0/rows?key=CkauTGJB6UdIntHriqHAvXRN2WZcSyUu0jo7pjDaQSg85t5S%2Bz2wznhYU%2FkrryjzI0N%2B7Y9PwsCzU70GKdUpjQ%3D%3D',
    '0004':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/190de494-6b67-44cf-b499-66bd34032bd8/rows?key=7c4R34fEjOsCS%2F7t%2FN%2F3oYWVwxgKKkduxxJKuXi72n%2BTZvXNUAOGVhnvERp1nl3F4BiHjdBlt8joG5Iy3j4ZDA%3D%3D',
    '0006':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/572ffb39-fb63-447d-bf9e-e3ba58170374/rows?key=0DLxORkcIcrvQ%2BiOShp2XP2ek4EtvKO3Xg0NjyPgq1vN4qSITpv7vUCFg6Ze%2Bx03RRg72XNWHOEo7%2FRIr8Dm%2FQ%3D%3D',
    '0005':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/0c318066-1fa8-4151-a317-c06a59bdf736/rows?noSignUpCheck=1&key=zEGyeOveujBLQsJzvdq4aXWY1NKQxfkLxojom5ZDktfJ2o8fPrFsRW2dErur%2FBbx2I1tSZfOOWPkRQkbv6Qkgg%3D%3D',
    '0002':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/a606a6ec-84f7-4f9e-b03f-bf5034cc1a95/rows?noSignUpCheck=1&key=zC1WgFvlU6l5LRYJVyuC3%2FEjiqpjbJeQ%2BGIu923gfxUF9sCyAaWLLc02Ss64vF4M5qQ9cCZQ5w%2Byac8Or6uY2w%3D%3D',
    '0001':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/fd76ee16-9b3a-421b-b294-18b847f8e55d/rows?noSignUpCheck=1&key=1V1hKzcH4MP7KBYlGNT4jloP98MVuKwte6d2KepUS004N79DWy7Ccz%2F0V%2BLlR76jxPHcoTvvKvVYAl9BNgKySQ%3D%3D'
    
    }

    
    lista_em_aberto={

        '0009':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/e2a751bc-b662-407e-849c-ec3a1d576567/rows?key=7cpom8kzI%2B5Rt6aMBgDVgyrWKCTHdJ4KPl23KDAFqtOK0F95gdWCXznnGgtxXE8kTqXVh%2BNdjjSDZehNP0zusw%3D%3D',
        '0003':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/0b67eb8f-1577-4355-bdab-6a7430597598/rows?key=rQ2ZZFRmrG29PX7QXkV9P03Si8dJ%2FCWRj4NXEW0KHobJf3JGvvywe3N0YvCaCmYMyGEzWE%2BitWPrWUkEZIo66g%3D%3D',
        '0004':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/21392bc7-bab8-4e2b-8e56-d792ea263303/rows?key=%2FczqkFtQRDb5hQTCbhs90KFH5PJjv6m%2FqsdyVn%2FdwNGw0KUP8kJPY1dRqutocK6WOnNctP1hGHxZs40vXcEIfQ%3D%3D',
        '0006':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/d433c1ab-806b-4506-bd39-f106d2ce1007/rows?key=kgXzK6Rm0lkzkG5RWAOa5Uy%2BDrm7vxDKvb7zcu%2FN%2BcQxxnxx02mz4MDebwnUUE%2Bbmm1wWp96NfcJCJTgQK4q9w%3D%3D',
        '0005':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/0fb1e921-7174-4791-90ba-a750a86878af/rows?noSignUpCheck=1&key=eoT0Om1EsKmjOYh%2FBjZqvsyh2BA31sNlyy%2BWcMlxElhZjEgeUe61XGYL6kL0t%2BUKKYVAsVDM%2Bq1qYxqjlTy%2BIw%3D%3D',
        '0002':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/bb0e14ae-f24e-4b3f-aa46-c52561b4c2fc/rows?noSignUpCheck=1&key=4%2FfTRJKW4v24CSQmeaYrQSDAFBTMdOno8yuJ%2Fg1GFB2NVdhEKemEI2g1SEWMyv7wDQI%2FgV0bCIfs7ncaRnIPKQ%3D%3D',
        '0001':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/b3067c70-66e7-40e6-ba1a-85e079f48b04/rows?noSignUpCheck=1&key=ixlLK%2F%2FtOPw6ElLO489euhA6mphc3%2B%2FsxzN%2FMit7DkQalI9CCUq0VsQjznjImB6oJQKJY2pT37GcJlUJIZjKKA%3D%3D'

    }

    lista_realizado={

        '0009':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/88fe1763-ca0c-4b14-90f2-3efd83ab0e79/rows?key=UUzWNN2MzL7e5DA8NMETWMYt%2BtwecqY7g%2Bk5Ab7zjzeLOVVKzSNVvJNfK7nEaHyRiEpy4SrwXuSCb75tehI6rw%3D%3D',
        '0003':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/c25dcc9e-c277-4f85-ac1b-2fe31a50e85b/rows?key=ugFSo3Y6CukyzTBcVWibJECFKA1ot5uTfolXRxcBMCu41hgw0I4uWbzaSYgf1d1e90aTQ%2F8AKDR6zs0WnECwpw%3D%3D',
        '0004':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/fc117733-a1be-4ee8-b621-1d7055e1b759/rows?key=kQ88TNGzEGKQ%2BBKHGHJT8ybqt2K%2FzOZAdVYWQULHvhwTWLu9ba1DoQ1qEuCPHUTfWzCVrrAsQNVhX5v6f2pwbA%3D%3D',
        '0006':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/9fb37c4a-5cf8-475c-9c5b-ff0ed4fb654d/rows?key=qDcR5MSv%2FnoEtELNC1xnkk0Sz8NUAFCX2e2kgGdfvJOKddq6uN6D45e0Jn12uTj%2BS4oyW7kDAV6CeO3nZ7COsw%3D%3D',
        '0005':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/416b4624-3071-46b6-8381-90b761663cc1/rows?noSignUpCheck=1&key=CPQ1lkryqfaKtdy0XHJpOzje%2F7pTQ8XdFsaOfpARxUxacQFHJhFwREgDc92NhPIGf5HQj4d%2Fi9J5L561P%2FDEUQ%3D%3D',
        '0002':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/0bc2e408-2d90-4ece-bfa2-4ea76ea7ff88/rows?noSignUpCheck=1&key=d5qAaYdcjqJ%2FpjwYkmANk9qYetYCK0H6i5G9G9gXmachQg%2FVpQ4fyRgQ2JnPGHAdIBTuSqzKQKVfSrPjt561Tw%3D%3D',
        '0001':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/7ffec982-d917-4565-bed5-4a9ccecd97e6/rows?noSignUpCheck=1&key=433XKkDcl0pcVFogMYGhutwZHEJMW1LPZWNTMY2G95HZBDAQh7vMpa4fLDB%2Fx%2Bof%2BgF2TYeXJj0R0ss0DkZMGg%3D%3D'

    }

    for cod,url in lista_equipe.items():

        try:

            vendas_df=pd.DataFrame()

            vendas_df=tabelas_df['TargetEstatico'].loc[tabelas_df['TargetEstatico']['Tipo de Operação']=='VENDAS']

            vendas_df=vendas_df.merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['ID Empresa', 'Pedido', 'Nfe', 'ID Cliente', 'ID Vendedor',
                'Data de Emissão', 'Data de Faturamento', 'ID Motivo', 'Situação',
                'Tipo de Pedido', 'Tipo de Operação', 'ID Roteiro', 'ID Usuário',
                'Tabelas', 'Origem', 'Tipo de Entrega', 'Seq Roteiro', 'SKU', 'Seq',
                'Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA', 'Total Venda', 'Total AV',
                'Total Geral', 'Margem Bruta R$', 'Comissão R$', 'IPI R$', 'PIS R$',
                'COFINS R$', 'ICMS R$', 'ICMS ST R$', 'Peso Bruto KG',
                'Peso Líquido KG', 'Cad Vendedor','ID Equipe']]

            vendas_df=vendas_df.loc[vendas_df['ID Equipe']==cod]

            base_df=pd.DataFrame()

            base_df=vendas_df[['Situação','Total Venda']].groupby(['Situação'],as_index=False).sum()

            base_df['Pedido']=base_df['Situação'].apply(lambda info: len(vendas_df['Pedido'].loc[vendas_df['Situação']==info].unique().tolist()))

            base_df['Cliente']=base_df['Situação'].apply(lambda info: len(vendas_df['ID Cliente'].loc[vendas_df['Situação']==info].unique().tolist()))

            base_df['MIX']=base_df['Situação'].apply(lambda info: len(vendas_df['SKU'].loc[vendas_df['Situação']==info].unique().tolist()))

            base_df.loc[base_df['Situação']!='FATURADO','Pedido']=base_df.loc[base_df['Situação']!='FATURADO','Pedido']*-1

            base_df.loc[base_df['Situação']!='FATURADO','Cliente']=base_df.loc[base_df['Situação']!='FATURADO','Cliente']*-1

            base_df.loc[base_df['Situação']!='FATURADO','MIX']=base_df.loc[base_df['Situação']!='FATURADO','MIX']*-1

            #calculo

            pedido=base_df['Pedido'].sum()

            cliente=base_df['Cliente'].sum()

            faturado=round(base_df['Total Venda'].sum(),2)

            meta_df=pd.DataFrame()

            meta_df=tabelas_df['Meta'].merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['ID Vendedor','Meta R$','ID Equipe']]

            meta_df=meta_df.loc[meta_df['ID Equipe']==cod]

            meta=round(meta_df['Meta R$'].sum(),2)

            perc_meta=round(faturado/meta,4)*100 if meta>0 else 0

            dif_meta=faturado-meta

            ticket=round(faturado/pedido,2) if faturado>0 else 0

            calend_df=pd.DataFrame()

            calend_df=tabelas_df['Calendario']

            uteis=len(calend_df['Data'].loc[calend_df['Dia Útil']==True].unique().tolist())

            trabalhado=len(calend_df['Data Trabalhada'].loc[(calend_df['Dia Útil']==True)&(~calend_df['Data Trabalhada'].isnull())].unique().tolist())-1

            restante=uteis-trabalhado

            projecao=(faturado/trabalhado)*uteis if trabalhado>0 else 0

            meta_diaria=round(meta/uteis,2)

            aberto_df=pd.DataFrame()

            aberto_df=tabelas_df['Aberto']

            aberto_df=aberto_df.merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['ID Empresa', 'Pedido', 'ID Cliente', 'ID Vendedor', 'Data do Pedido',
                'SKU', 'Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA', 'Total Venda',
                'Total AV', 'Total Geral', 'Margem Bruta R$', 'Margem Bruta CRP',
                'Situação', 'Peso Bruto KG', 'Peso Líquido KG','ID Equipe']]

            aberto_df=aberto_df.loc[aberto_df['ID Equipe']==cod]

            atendimento=len(aberto_df['ID Cliente'].unique().tolist())

            realizado=round(aberto_df['Total Geral'].sum(),2)

            ped_realizado=len(aberto_df['Pedido'].unique().tolist())

            perc_diario=round(realizado/meta_diaria,4)*100 if meta_diaria>0 else 0

            real_aberto=round(aberto_df['Total Geral'].loc[aberto_df['Situação']=='AB'].sum(),2)

            total=faturado+real_aberto

            kg_real=round(aberto_df['Peso Bruto KG'].sum(),3)

            mix=len(aberto_df['SKU'].unique().tolist())

            dif_diario=round(realizado-meta_diaria,2)

            temp_dict={


                "Pedido" :float(pedido),
                "Cliente" :float(cliente),
                "Faturado" :float(faturado),
                "Meta" :float(meta),
                "Meta %" :float(perc_meta),
                "Diferença R$" :float(dif_meta),
                "Projeção" :float(projecao),
                "Ticket Médio" :float(ticket),
                "Atendimento" :float(atendimento),
                "Pedido Realizado" :float(ped_realizado),
                "MIX" :float(mix),
                "Meta Diária" :float(meta_diaria),
                "Realizado R$" :float(realizado),
                "Dias Úteis" :float(uteis),
                "Dias Trabalhados" :float(trabalhado),
                "Dias Restante" :float(restante),
                "Diário %" :float(perc_diario),
                "Valor Mínimo" :float(0),
                "Valor Máximo" :float(100),
                "Faturado + Em Aberto" :float(total),
                "Dif Diário R$" :float(dif_diario),
                "KG Vendido" :float(kg_real),
                "Em Aberto R$" :float(real_aberto)


                }

            requests.post(url=lista_equipe[cod],json=temp_dict)

            equipes_df=pd.DataFrame()
            
            temp_df=pd.DataFrame()

            temp_df=tabelas_df['Supervisor'].loc[tabelas_df['Supervisor']['ID Equipe']==cod]

            equipes_df=tabelas_df['Vendedor'].merge(temp_df,on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe','Supervisor']]

            equipes_df=equipes_df.merge(tabelas_df['Meta'],on='ID Vendedor',how='inner')

            equipes_df=equipes_df.loc[equipes_df['Meta R$']>0]

            equipes_df.loc[:,'Diário']=round(equipes_df['Meta R$']/uteis,2)

            vendedores_df=pd.DataFrame()

            vendedores_df=aberto_df[['ID Vendedor','Total Venda']].groupby(['ID Vendedor'],as_index=False).sum()

            equipes_df=equipes_df.merge(vendedores_df,on='ID Vendedor',how='left')

            equipes_df.loc[equipes_df['Total Venda'].isnull(),'Total Venda']=0

            equipes_df.loc['Diferença']=0

            if(len(equipes_df)>0):

                equipes_df['Diferença']=equipes_df.apply(lambda info: info['Diário']-info['Total Venda'],axis=1)

                pass

            consolidado_df=pd.DataFrame()

            consolidado_df=equipes_df[['Vendedor','Diferença']].groupby(['Vendedor'],as_index=False).sum()

            #consolidado_df['Diferença']=consolidado_df['Diferença']*-1

            consolidado_df.sort_values('Diferença',ascending=False,inplace=True)

            consolidado_df=consolidado_df.loc[consolidado_df['Diferença']>0]

            if(len(consolidado_df)<=0):
            
                requests.delete(url=lista_em_aberto[cod])

                pass

            else:

                requests.post(url=lista_em_aberto[cod],json=consolidado_df.to_dict('records'))

                pass

            consolidado_df=equipes_df[['Vendedor','Total Venda','Diferença']].groupby(['Vendedor'],as_index=False).sum()

            consolidado_df.rename(columns={'Total Venda':'Realizado R$'},inplace=True)

            consolidado_df.sort_values('Realizado R$',ascending=False,inplace=True)

            consolidado_df=consolidado_df[['Vendedor','Realizado R$']].loc[consolidado_df['Diferença']<=0]

            requests.post(url=lista_realizado[cod],json=consolidado_df.to_dict('records'))

            pass
                        
        except:

            continue

        pass

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    Equipes(tabelas)

    pass