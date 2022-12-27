from Query import Query
import pandas as pd
from Tempo import DataHora
import requests

sql=Query('Netfeira','sqlserver','MOINHO','192.168.0.252')

url={'Consolidado':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/536ad588-cc04-44a3-a923-cfd7e4e8947b/rows?key=fCKjsjEvlHfEFafNL%2Bgqhywm6ff%2BMOLBtQ98s%2BO28sAOptXIZjfwCEl68ppYj91pz9L%2BVfkM%2B%2FA5ZW%2FUf0LXpg%3D%3D',


'Supervisor':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/2f9e1df4-8bb3-47bf-8378-83a41c60f706/rows?key=n0VLoDleUsQkNQ5Y096uXR9fqdFmZajV9ja7LMDiFjby%2BaSAXG3qtjR8VRM2%2FZJCUhaXNZwHTQYZPhJG25ojkg%3D%3D',


'Equipe':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/0aa821da-ebc0-405b-a5e8-bb8ee2f860eb/rows?key=QdD%2BwkBQ4eyCc23qRz0AHIyii2pqnxcDzrNt%2FY8obZWuvMWtcXIE7Bsj2EHSReM9UasoYqtTYaGucevHp4Z5iA%3D%3D'
}

data=DataHora()

data_atual=data.HoraAtual()

ano=data_atual.year

mes=data_atual.month

dia=data_atual.day

hora=data_atual.hour

minuto=data_atual.minute

def Analise(tabelas_df):

    try:

        Equipes(tabelas_df)

        tabelas_df['Calendario']['Feriado']=tabelas_df['Calendario'].apply(lambda info: len(tabelas_df['Feriado']['Mês Base'].loc[tabelas_df['Feriado']['Mês Base']==info['Mês Base']].unique().tolist()),axis=1)

        tabelas_df['Calendario']['Dias Úteis']=tabelas_df['Calendario'].apply(lambda info: 0 if info['Feriado']==1 else info['Dias Úteis'],axis=1)

        tabelas_df['Calendario'].drop(columns=['Feriado'],inplace=True)

        dias_uteis=tabelas_df['Calendario'][['Dias Úteis']].loc[(tabelas_df['Calendario']['Ano']==ano)&(tabelas_df['Calendario']['Cód. Mês']==mes)].sum()

        dias_trabalhados=tabelas_df['Calendario'][['Dias Úteis']].loc[(tabelas_df['Calendario']['Ano']==ano)&(tabelas_df['Calendario']['Cód. Mês']==mes)&(tabelas_df['Calendario']['Dia']<=dia)].sum()

        dias_restante=dias_uteis[0]-(dias_trabalhados[0]-1)

        dias_trabalhados=dias_trabalhados[0]-1 if (dias_trabalhados[0]-1)>0 else 0 

        dias_uteis=dias_uteis[0]

        vendas_df=tabelas_df['Estático']  

        faturado=vendas_df['Total Geral'].loc[(vendas_df['Data de Faturamento'].dt.month==mes)&(~vendas_df['Status do Pedido'].str.contains('EM ABERTO'))].sum()

        faturado=round(faturado,2)

        df_aberto=tabelas_df['Aberto']

        aberto=df_aberto['Total Geral'].sum()

        peso=df_aberto['Peso Bruto'].sum()

        em_aberto=df_aberto['Total Geral'].loc[df_aberto['Situação']=='AB'].sum()

        aberto=round(aberto,2)

        qtde_cliente=len(df_aberto['ID Cliente'].unique().tolist())

        qtde_pedido=len(df_aberto['Pedido'].unique().tolist())

        situacao_df=vendas_df[['Status do Pedido','Numero do Pedido','ID Cliente']].loc[(vendas_df['Data de Faturamento'].dt.month==mes)].groupby(['Status do Pedido','Numero do Pedido','ID Cliente'],as_index=False).count()

        temp_df=situacao_df[['Status do Pedido']].groupby(['Status do Pedido'],as_index=False).count()

        temp_df['Pedido']=temp_df.apply(lambda info: len(situacao_df['Numero do Pedido'].loc[situacao_df['Status do Pedido']==info['Status do Pedido']].unique().tolist()),axis=1)

        temp_df['Cliente']=temp_df.apply(lambda info: len(situacao_df['ID Cliente'].loc[situacao_df['Status do Pedido']==info['Status do Pedido']].unique().tolist()),axis=1)

        temp_df.loc[~temp_df['Status do Pedido'].isin(['FATURADO','EM ABERTO']),'Pedido']=temp_df['Pedido']*-1

        temp_df.loc[~temp_df['Status do Pedido'].isin(['FATURADO','EM ABERTO']),'Cliente']=temp_df['Cliente']*-1

        pedido=temp_df['Pedido'].loc[~temp_df['Status do Pedido'].isin(['EM ABERTO'])].sum()

        cliente=temp_df['Cliente'].loc[~temp_df['Status do Pedido'].isin(['EM ABERTO'])].sum()  

        ticket=round(faturado/pedido,2)

        metas_df=tabelas_df['Meta'][['cd_vend','FATUVL']].loc[(tabelas_df['Meta']['mes_ref'].dt.year==ano)&(tabelas_df['Meta']['mes_ref'].dt.month==mes)].groupby(['cd_vend','FATUVL'],as_index=False).sum()

        metas_df.rename(columns={'cd_vend':'ID Vendedor','FATUVL':'Meta R$'},inplace=True)

        metas_df=metas_df.merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['ID Vendedor','Vendedor','ID Equipe','Meta R$']]

        metas_df=metas_df.merge(tabelas_df['Equipe'],on='ID Equipe',how='inner')[['ID Vendedor','Vendedor','Equipe','Supervisor','Meta R$']]

        metas_df['Meta Diária']=metas_df.apply(lambda info: round(info['Meta R$']/dias_uteis,2),axis=1)

        metas_df['Faturado R$']=metas_df.apply(lambda info: round(vendas_df['Total Geral'].loc[(vendas_df['Data de Faturamento'].dt.month==mes)&(vendas_df['ID Vendedor']==info['ID Vendedor'])&(~vendas_df['Status do Pedido'].isin(['EM ABERTO']))].sum(),2),axis=1)

        metas_df['Realizado R$']=metas_df.apply(lambda info: df_aberto['Total Geral'].loc[(df_aberto['ID Vendedor']==info['ID Vendedor'])].sum(),axis=1)

        metas_df['Dif Meta']=metas_df.apply(lambda info: info['Faturado R$']-info['Meta R$'],axis=1)

        metas_df['Dif Realizado']=metas_df.apply(lambda info: info['Realizado R$']-info['Meta Diária'],axis=1)

        equipe_df=metas_df.groupby(['Equipe'],as_index=False).sum()

        meta=equipe_df['Meta R$'].sum()

        dif=equipe_df['Dif Meta'].sum()
        
        perc_meta=round(faturado/meta,4)*100

        dia_empresa=round(meta/dias_uteis,2)

        perc_dia=round(aberto/dia_empresa,4)*100

        projecao=round((faturado/dias_trabalhados)*dias_uteis,2) if dias_trabalhados>0 else 0

        qtde_equipe=len(metas_df['Equipe'].unique().tolist())

        qtde_vend=len(metas_df['ID Vendedor'].unique().tolist())

        mix=mix=len(df_aberto['SKU'].unique().tolist())

        realizado=round(faturado+em_aberto,2)

        dif_diario=round(aberto-dia_empresa,2)

        trab_inicio=8

        trab_fim=18

        trab_almoco=1.12     

        trab_almoco=str(trab_almoco)

        hora_almoço=int(trab_almoco[:trab_almoco.find('.')])

        trab_almoco=trab_almoco[trab_almoco.find('.'):]

        trab_almoco=trab_almoco[1:]

        trab_almoco=int(trab_almoco)/60

        hora_almoço=trab_almoco+hora_almoço

        res=round((trab_fim-trab_inicio)-hora_almoço,2)

        hora_atual=round(hora+(minuto/60),2)

        dif_hora=(hora_atual-trab_inicio)-hora_almoço

        dif_restante=(res-dif_hora)

        projecao_dia=round(((aberto/dif_hora)*dif_restante),2)+aberto

        temp_dict={
            
            "Pedido" :float(pedido),
            'Cliente':float(cliente),
            'Faturado':float(faturado),
            'Meta':float(meta),
            'Meta %':float(perc_meta),
            'Diferença R$':float(dif),
            'Projeção':float(projecao),
            'Ticket Médio':float(ticket),
            'Atendimento':float(qtde_cliente),
            'Pedido Realizado':float(qtde_pedido),
            'MIX':float(mix),
            'Meta Diária':float(dia_empresa),
            'Realizado R$':float(aberto),
            'Dias Úteis':float(dias_uteis),
            'Dias Trabalhados':float(dias_trabalhados),
            'Dias Restante':float(dias_restante),
            'Diário %':float(perc_dia),
            'Valor Mínimo':float(0),
            'Valor Máximo':float(100),
            'Faturado + Em Aberto':float(realizado),
            'Dif Diário R$':float(dif_diario),
            'Projeção Dia':float(projecao_dia),
            'KG Vendido':float(peso),
            'Em Aberto R$':float(em_aberto)

            }
        r=requests.post(url['Consolidado'],json=temp_dict)

        if(r.status_code==200):

            supervisor_df=metas_df[['Supervisor','Meta Diária','Realizado R$']].groupby(['Supervisor'],as_index=False).sum()

            supervisor_df['Dif Realizado']=supervisor_df.apply(lambda info: info['Meta Diária']-info['Realizado R$'],axis=1)

            supervisor_df['Realizado %']=supervisor_df.apply(lambda info: round(info['Realizado R$']/info['Meta Diária'],4)*100,axis=1)

            supervisor_df=supervisor_df[['Supervisor','Dif Realizado']]

            supervisor_df.sort_values('Dif Realizado',ascending=False,inplace=True)

            supervisor_df=supervisor_df.loc[supervisor_df['Dif Realizado']>0]

            if(len(supervisor_df)==0):

                supervisor_df=metas_df[['Supervisor','Meta Diária','Realizado R$']].groupby(['Supervisor'],as_index=False).sum()

                supervisor_df['Dif Realizado']=supervisor_df.apply(lambda info: info['Realizado R$'],axis=1)

                supervisor_df.sort_values('Dif Realizado',ascending=False,inplace=True)

                supervisor_df=supervisor_df[['Supervisor','Dif Realizado']]

                pass
          
            equipe_df.sort_values('Realizado R$',ascending=False,inplace=True)         
        
            requests.post(url['Supervisor'],json=supervisor_df.to_dict('records'))

            requests.post(url['Equipe'],json=equipe_df[['Equipe','Realizado R$']].loc[equipe_df['Dif Realizado']>=0].to_dict('records'))

            print(r.status_code)
            
            pass

        pass

    except Exception as erro:

        print(erro)

        pass

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


    for eq,url in lista_equipe.items():

        try:

            tabelas_df['Calendario']['Feriado']=tabelas_df['Calendario'].apply(lambda info: len(tabelas_df['Feriado']['Mês Base'].loc[tabelas_df['Feriado']['Mês Base']==info['Mês Base']].unique().tolist()),axis=1)

            tabelas_df['Calendario']['Dias Úteis']=tabelas_df['Calendario'].apply(lambda info: 0 if info['Feriado']==1 else info['Dias Úteis'],axis=1)

            tabelas_df['Calendario'].drop(columns=['Feriado'],inplace=True)

            dias_uteis=tabelas_df['Calendario'][['Dias Úteis']].loc[(tabelas_df['Calendario']['Ano']==ano)&(tabelas_df['Calendario']['Cód. Mês']==mes)].sum()

            dias_trabalhados=tabelas_df['Calendario'][['Dias Úteis']].loc[(tabelas_df['Calendario']['Ano']==ano)&(tabelas_df['Calendario']['Cód. Mês']==mes)&(tabelas_df['Calendario']['Dia']<=dia)].sum()

            dias_restante=dias_uteis[0]-(dias_trabalhados[0]-1)

            dias_trabalhados=dias_trabalhados[0]-1 if (dias_trabalhados[0]-1)>0 else 0 

            dias_uteis=dias_uteis[0]

            vendas_df=tabelas_df['Estático'].merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['Numero do Pedido', 'NFe', 'ID Cliente', 'ID Vendedor','ID Equipe',
        'Tipo de Pedido', 'Tipo de Operação', 'Tabela de Preço',
        'Data de Emissão', 'Data de Faturamento', 'Status do Pedido', 'ID NFe',
        'SKU', 'Seq', 'Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA',
        'Total Geral', 'Custo da Útima Entrada', 'Peso Bruto', 'Peso Líquido',
        'Preço da Tabela', '% Desconto', '% Comissão', 'Comissão R$']]

            vendas_df=vendas_df.loc[vendas_df['ID Equipe']==eq]

            faturado=vendas_df['Total Geral'].loc[(vendas_df['Data de Faturamento'].dt.month==mes)&(~vendas_df['Status do Pedido'].str.contains('EM ABERTO'))].sum()

            df_aberto=tabelas_df['Aberto'].merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['Data do Pedido', 'Pedido', 'ID Cliente', 'ID Vendedor','ID Equipe', 'SKU', 'Qtde',
        'Unid. VDA', 'Qtde. VDA', 'Valor Unitário', 'Total Geral', 'Peso Bruto',
        'Peso Líquido', 'Situação']]

            df_aberto=df_aberto.loc[df_aberto['ID Equipe']==eq]

            aberto=df_aberto['Total Geral'].sum()

            peso=df_aberto['Peso Bruto'].sum()

            em_aberto=df_aberto['Total Geral'].loc[df_aberto['Situação']=='AB'].sum()

            aberto=round(aberto,2)

            qtde_cliente=len(df_aberto['ID Cliente'].unique().tolist())

            qtde_pedido=len(df_aberto['Pedido'].unique().tolist())

            situacao_df=vendas_df[['Status do Pedido','Numero do Pedido','ID Cliente']].loc[(vendas_df['Data de Faturamento'].dt.month==mes)].groupby(['Status do Pedido','Numero do Pedido','ID Cliente'],as_index=False).count()

            temp_df=situacao_df[['Status do Pedido']].groupby(['Status do Pedido'],as_index=False).count()

            temp_df['Pedido']=temp_df.apply(lambda info: len(situacao_df['Numero do Pedido'].loc[situacao_df['Status do Pedido']==info['Status do Pedido']].unique().tolist()),axis=1)

            temp_df['Cliente']=temp_df.apply(lambda info: len(situacao_df['ID Cliente'].loc[situacao_df['Status do Pedido']==info['Status do Pedido']].unique().tolist()),axis=1)

            temp_df.loc[~temp_df['Status do Pedido'].isin(['FATURADO','EM ABERTO']),'Pedido']=temp_df['Pedido']*-1

            temp_df.loc[~temp_df['Status do Pedido'].isin(['FATURADO','EM ABERTO']),'Cliente']=temp_df['Cliente']*-1

            pedido=temp_df['Pedido'].loc[~temp_df['Status do Pedido'].isin(['EM ABERTO'])].sum()

            cliente=temp_df['Cliente'].loc[~temp_df['Status do Pedido'].isin(['EM ABERTO'])].sum()  

            ticket=round(faturado/pedido,2)

            metas_df=tabelas_df['Meta'][['cd_vend','FATUVL']].loc[(tabelas_df['Meta']['mes_ref'].dt.year==ano)&(tabelas_df['Meta']['mes_ref'].dt.month==mes)].groupby(['cd_vend','FATUVL'],as_index=False).sum()

            metas_df.rename(columns={'cd_vend':'ID Vendedor','FATUVL':'Meta R$'},inplace=True)

            metas_df=metas_df.merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['ID Vendedor','Vendedor','ID Equipe','Meta R$']]

            metas_df=metas_df.loc[metas_df['ID Equipe']==eq]

            metas_df=metas_df.merge(tabelas_df['Equipe'],on='ID Equipe',how='inner')[['ID Vendedor','Vendedor','Equipe','Supervisor','Meta R$']]

            metas_df['Meta Diária']=metas_df.apply(lambda info: round(info['Meta R$']/dias_uteis,2),axis=1)

            metas_df['Faturado R$']=metas_df.apply(lambda info: round(vendas_df['Total Geral'].loc[(vendas_df['Data de Faturamento'].dt.month==mes)&(vendas_df['ID Vendedor']==info['ID Vendedor'])&(~vendas_df['Status do Pedido'].isin(['EM ABERTO']))].sum(),2),axis=1)

            metas_df['Realizado R$']=metas_df.apply(lambda info: df_aberto['Total Geral'].loc[(df_aberto['ID Vendedor']==info['ID Vendedor'])].sum(),axis=1)

            metas_df['Dif Meta']=metas_df.apply(lambda info: info['Faturado R$']-info['Meta R$'],axis=1)

            metas_df['Dif Realizado']=metas_df.apply(lambda info: info['Realizado R$']-info['Meta Diária'],axis=1)

            equipe_df=metas_df.loc[metas_df['Meta R$']>0]

            meta=equipe_df['Meta R$'].sum()

            dif=equipe_df['Dif Meta'].sum()
            
            perc_meta=round(faturado/meta,4)*100 if faturado>0 else 0

            dia_empresa=round(meta/dias_uteis,2)

            perc_dia=round(aberto/dia_empresa,4)*100

            projecao=round((faturado/dias_trabalhados)*dias_uteis,2) if dias_trabalhados>0 else 0

            qtde_equipe=len(metas_df['Equipe'].unique().tolist())

            qtde_vend=len(metas_df['ID Vendedor'].unique().tolist())

            mix=mix=len(df_aberto['SKU'].unique().tolist())

            realizado=round(faturado+em_aberto,2)

            dif_diario=round(aberto-dia_empresa,2)

            trab_inicio=8

            trab_fim=18

            trab_almoco=1.12     

            trab_almoco=str(trab_almoco)

            hora_almoço=int(trab_almoco[:trab_almoco.find('.')])

            trab_almoco=trab_almoco[trab_almoco.find('.'):]

            trab_almoco=trab_almoco[1:]

            trab_almoco=int(trab_almoco)/60

            hora_almoço=trab_almoco+hora_almoço

            res=round((trab_fim-trab_inicio)-hora_almoço,2)

            hora_atual=round(hora+(minuto/60),2)

            dif_hora=(hora_atual-trab_inicio)-hora_almoço

            dif_restante=(res-dif_hora)

            projecao_dia=round(((aberto/dif_hora)*dif_restante),2)+aberto

            temp_dict={
                
                "Pedido" :float(pedido),
                'Cliente':float(cliente),
                'Faturado':float(faturado),
                'Meta':float(meta),
                'Meta %':float(perc_meta),
                'Diferença R$':float(dif),
                'Projeção':float(projecao),
                'Ticket Médio':float(ticket),
                'Atendimento':float(qtde_cliente),
                'Pedido Realizado':float(qtde_pedido),
                'MIX':float(mix),
                'Meta Diária':float(dia_empresa),
                'Realizado R$':float(aberto),
                'Dias Úteis':float(dias_uteis),
                'Dias Trabalhados':float(dias_trabalhados),
                'Dias Restante':float(dias_restante),
                'Diário %':float(perc_dia),
                'Valor Mínimo':float(0),
                'Valor Máximo':float(100),
                'Faturado + Em Aberto':float(realizado),
                'Dif Diário R$':float(dif_diario),
                'Projeção Dia':float(projecao_dia),
                'KG Vendido':float(peso),
                'Em Aberto R$':float(em_aberto)

                }
            
            r=requests.post(url,json=temp_dict)

            if(r.status_code!=200):

                continue

            equipe_df['Dif Realizado']=equipe_df.apply(lambda info: info['Meta Diária']-info['Realizado R$'],axis=1)

            equipe_df.sort_values('Dif Realizado',ascending=False,inplace=True)            

            temp_df=equipe_df[['Vendedor','Realizado R$','Dif Realizado']].loc[equipe_df['Dif Realizado']>0]

            requests.post(lista_em_aberto[eq],json=temp_df.to_dict('records'))

            equipe_df.sort_values('Realizado R$',ascending=False,inplace=True)

            temp_df=equipe_df[['Vendedor','Realizado R$','Dif Realizado']].loc[equipe_df['Dif Realizado']<=0]

            requests.post(lista_realizado[eq],json=temp_df.to_dict('records'))

            print(r.status_code)

            pass

        except:

            continue

        pass

    pass

def Margens(tabelas_df):

    urls={
        'Geral':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/7b94b6cf-0dc3-42f0-8517-547713253937/rows?noSignUpCheck=1&key=u0ySyLK8yzHMWAh7hgB4Ya8PSj8mHXRxTtss1aF463g01dG8PGz7u2cTNRhSNKczR8Avf6mlIcM37GO9ZKs7LQ%3D%3D',
        'Mensal':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/edcf0476-f066-4bcd-9dc7-ffb49e44cbed/rows?noSignUpCheck=1&key=m%2BGSuAq4OBCoo7BegWx0gCIEyN%2BYk6tNoW27gWubtt6hnmCQL5ZeWOh7rdubW9lYBUG2RcyyVV6HA%2B0rBiIuOg%3D%3D',
        'Diaria':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/40eaefea-331d-41a0-b011-12b9e9dd0fd6/rows?key=PV2oKRTlvdgT5zz6XcNoGZQG1Bz%2BEzqJtdeHnKOYoENWiQ5QAuWy0VXwbzfZZcG1qMiud%2FEYFtcBWZyCHNFnYg%3D%3D'
    
    }
    

    tabelas_df['TargetEstatico']=tabelas_df['TargetEstatico'].loc[tabelas_df['TargetEstatico']['Tipo de Operação']!='OUTROS']    

    if((mes-1)==0):
        
        ano_ant=ano-1
        
        mes_ant=12
        
        pass

    else:
        
        mes_ant=mes-1

        ano_ant=ano
        
        pass

    tabelas_df['Cliente']=tabelas_df['Cliente'].merge(tabelas_df['Segmento'],on='ID Segmento',how='inner')[['ID Cliente', 'CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'Segmento', 'Canal', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato']]

    tabelas_df['TargetEstatico']=tabelas_df['TargetEstatico'].merge(tabelas_df['Produto'],on='SKU',how='inner')[['Data de Emissão', 'Data de Faturamento', 'Pedido', 'Nfe', 'ID Empresa',
        'ID Cliente', 'ID Vendedor', 'Tipo de Pedido', 'Tipo de Operação',
        'SKU','Produto', 'Status', 'Fabricante',
        'Departamento', 'Seção', 'Categoria', 'Linha','Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA', 'Total Geral',
        'Total Venda', 'Comissão R$', 'Margem Bruta R$', 'Cad Vendedor',
        'Situação', 'Peso Bruto KG', 'Peso Líquido KG']]


    tabelas_df['TargetEstatico']=tabelas_df['TargetEstatico'].merge(tabelas_df['Cliente'],on='ID Cliente',how='inner')[['Data de Emissão', 'Data de Faturamento', 'Pedido', 'Nfe', 'ID Empresa',
        'ID Cliente', 'CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'Segmento', 'Canal', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato','ID Vendedor', 'Tipo de Pedido', 'Tipo de Operação',
        'SKU', 'Produto', 'Status', 'Fabricante', 'Departamento', 'Seção',
        'Categoria', 'Linha', 'Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA',
        'Total Geral', 'Total Venda', 'Comissão R$', 'Margem Bruta R$',
        'Cad Vendedor', 'Situação', 'Peso Bruto KG', 'Peso Líquido KG']]
        
    
    #Analise funil por fabricante

    fabric_df=tabelas_df['TargetEstatico'][['Fabricante','Total Venda']].loc[(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.year==ano_ant)&(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.month==mes_ant)].groupby(['Fabricante'],as_index=False).sum()

    fabric_df.sort_values('Total Venda',ascending=False,ignore_index=True,inplace=True)

    total=round(fabric_df['Total Venda'].sum(),2)

    indice=fabric_df.index.tolist()

    fabric_df['Rank']=indice

    fabric_df['Total Acumulado']=fabric_df['Rank'].apply(lambda info: fabric_df['Total Venda'].loc[fabric_df['Rank']<=info].sum())

    fabric_df['Total Geral']=total

    fabric_df['Rep %']=round(fabric_df['Total Acumulado']/fabric_df['Total Geral'],4)*100

    fabric_df['Classificação']=fabric_df['Rep %'].apply(Classificar)

    marca=fabric_df['Fabricante'].loc[fabric_df['Classificação']!='C'].tolist()

    #Analise funil por linha

    temp_df=pd.DataFrame()

    for m in marca:
        
        linha_df=tabelas_df['TargetEstatico'][['Linha','Fabricante','Total Venda']].loc[(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.year==ano_ant)&(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.month==mes_ant)&(tabelas_df['TargetEstatico']['Fabricante']==m)].groupby(['Linha','Fabricante'],as_index=False).sum()
    
        linha_df.sort_values('Total Venda',ascending=False,ignore_index=True,inplace=True)

        total=round(linha_df['Total Venda'].sum(),2)

        indice=linha_df.index.tolist()

        linha_df['Rank']=indice

        linha_df['Total Acumulado']=linha_df['Rank'].apply(lambda info: linha_df['Total Venda'].loc[linha_df['Rank']<=info].sum())

        linha_df['Total Geral']=total

        linha_df['Rep %']=round(linha_df['Total Acumulado']/linha_df['Total Geral'],4)*100

        linha_df.loc[~linha_df['Rep %'].isnull()]
        
        linha_df['Classificação']=linha_df['Rep %'].apply(Classificar)
        
        linha_df=linha_df.loc[linha_df['Classificação']!='C']
        
        temp_df=pd.concat([temp_df,linha_df],axis=0,ignore_index=True)
            
        pass

    lista=temp_df[['Linha','Fabricante']].to_dict('records')    

    #Analise funil por produto

    df=pd.DataFrame()

    for i in range(0,len(lista)):
        
        linha=lista[i]['Linha']
        
        fabricante=lista[i]['Fabricante']
        
        prod_df=tabelas_df['TargetEstatico'][['SKU','Produto','Fabricante','Linha','Total Venda']].loc[(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.year==ano_ant)&(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.month==mes_ant)&(tabelas_df['TargetEstatico']['Fabricante']==fabricante)&(tabelas_df['TargetEstatico']['Linha']==linha)].groupby(['SKU','Produto','Fabricante','Linha'],as_index=False).sum()

        prod_df.sort_values('Total Venda',ascending=False,ignore_index=True,inplace=True)

        total=round(prod_df['Total Venda'].sum(),2)

        indice=prod_df.index.tolist()

        prod_df['Rank']=indice

        prod_df['Total Acumulado']=prod_df['Rank'].apply(lambda info: prod_df['Total Venda'].loc[prod_df['Rank']<=info].sum())

        prod_df['Total Geral']=total

        prod_df['Rep %']=round(prod_df['Total Acumulado']/prod_df['Total Geral'],4)*100

        prod_df.loc[~prod_df['Rep %'].isnull()]
        
        prod_df['Classificação']=prod_df['Rep %'].apply(Classificar)
        
        prod_df=prod_df.loc[prod_df['Classificação']!='C']
        
        df=pd.concat([df,prod_df],axis=0,ignore_index=True)    
                
        pass

    lista_codigo=df['SKU'].tolist()

    base_df=tabelas_df['TargetEstatico'].loc[(tabelas_df['TargetEstatico']['SKU'].isin(lista_codigo))&(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.year==ano)&(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.month==mes)]

    margem_ideal=round(round(tabelas_df['TargetMargem']['Margem Média'].mean(axis=0),4)*100,2)
    
    tabelas_df['TargetMargem']=tabelas_df['TargetMargem'][['SKU','Margem B','Margem F','Margem Média']]

    df=tabelas_df['TargetMargem']

    df['Margem B']=df['Margem B']*100

    df['Margem F']=df['Margem F']*100

    df['Margem Média']=df['Margem Média']*100

    #produtos abaixo da f mensal

    margens_df=base_df[['SKU','Produto','Fabricante','Linha','Total Venda','Margem Bruta R$']].loc[base_df['Situação']!='EM ABERTO'].groupby(['SKU','Produto','Fabricante','Linha'],as_index=False).sum()

    margens_df['MG %']=margens_df.apply(lambda info: round(info['Margem Bruta R$']/info['Total Venda'],4)*100,axis=1)    

    mg_df=margens_df.merge(tabelas_df['TargetMargem'],on='SKU',how='inner')[['SKU', 'Produto', 'Fabricante', 'Linha', 'Total Venda',
        'Margem Bruta R$', 'MG %','Margem B','Margem F','Margem Média']]

    mg_df['Status']=mg_df.apply(lambda info: 'SIM' if info['MG %']<info['Margem F'] else 'NÃO',axis=1)

    mg_df['Descrição']=mg_df['SKU'].map(str) + ' - ' + mg_df['Produto'].map(str)

    mg_df=mg_df.loc[mg_df['Status']=='SIM']

    mg_df.sort_values('Total Venda',ascending=False,inplace=True)

    requests.post(url=urls['Mensal'],json=mg_df.to_dict('records'))

    margens_df=base_df[['SKU','Produto','Fabricante','Linha','Total Venda','Margem Bruta R$']].loc[(base_df['Situação']=='EM ABERTO')&(base_df['Data de Faturamento'].dt.day==dia)].groupby(['SKU','Produto','Fabricante','Linha'],as_index=False).sum()

    margens_df['MG %']=margens_df.apply(lambda info: round(info['Margem Bruta R$']/info['Total Venda'],4)*100,axis=1)

    mg_df=margens_df.merge(tabelas_df['TargetMargem'],on='SKU',how='inner')[['SKU', 'Produto', 'Fabricante', 'Linha', 'Total Venda',
        'Margem Bruta R$', 'MG %','Margem B','Margem F','Margem Média']]

    mg_df['Status']=mg_df.apply(lambda info: 'SIM' if info['MG %']<info['Margem F'] else 'NÃO',axis=1)

    mg_df['Descrição']=mg_df['SKU'].map(str) + ' - ' + mg_df['Produto'].map(str)

    mg_df=mg_df.loc[mg_df['Status']=='SIM']

    mg_df.sort_values('Total Venda',ascending=False,inplace=True)

    requests.post(url=urls['Diaria'],json=mg_df.to_dict('records'))

    base_df=tabelas_df['TargetEstatico'].loc[(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.year==ano)&(tabelas_df['TargetEstatico']['Data de Faturamento'].dt.month==mes)]

    canal_df=base_df[['Canal','Total Venda','Margem Bruta R$']].loc[(base_df['Tipo de Operação']!='OUTROS')].groupby('Canal',as_index=False).sum()

    canal_df['MG %']=canal_df.apply(lambda info: round(info['Margem Bruta R$']/info['Total Venda'],4)*100,axis=1)

    margem_as=canal_df['MG %'].loc[canal_df['Canal']=='AS'].tolist()

    margem_fs=canal_df['MG %'].loc[canal_df['Canal']=='FS'].tolist()

    realizado=base_df[['Total Venda']].sum().tolist()

    margem_mes=base_df[['Margem Bruta R$']].sum().tolist()

    perc_mes=round(margem_mes[0]/realizado[0],4)*100

    bonificacao=round(base_df['Total Geral'].loc[base_df['Tipo de Operação'].str.strip().isin(['BONIFICAÇÃO','AMOSTRA'])].sum(),2)

    total=round(base_df['Total Geral'].loc[~base_df['Tipo de Operação'].str.strip().isin(['BONIFICAÇÃO','AMOSTRA'])].sum(),2)

    perc_bonif=round(bonificacao/total,4)*100

    temp_dict={
        
        "Máximo" :float(100),
        "Mínimo" :float(0),
        "Margem Ideal" :float(margem_ideal),
        "Margem AS" :float(margem_as[-1]),
        "Margem FS" :float(margem_fs[-1]),
        "Margem Empresa" :float(perc_mes),
        "Realizado R$" :float(total),
        "Bonificado R$" :float(bonificacao),
        "Bonificado %" :float(perc_bonif)

        }

    requests.post(url=urls['Geral'],json=temp_dict)

    pass

def Classificar(valor):
    
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

    tabelas=sql.CriarTabela()

    Analise(tabelas)

    Margens(tabelas)

    pass