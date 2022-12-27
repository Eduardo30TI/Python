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
        'Serie', 'Tipo de Pagamento', 'ID Cliente', 'Razão Social',
        'Nome Fantasia', 'Matriz', 'Segmento','Canal', 'Situação', 'Valor',
        'Desconto R$', 'Multa R$', 'Juros R$', 'Abatimento R$', 'Taxa R$',
        'Valor Líquido', 'Pago R$','Status do Título', 'Dias', 'Alerta']]

    titulos_df['Saldo R$']=titulos_df.apply(lambda info: info['Valor Líquido']-info['Pago R$'],axis=1)
    
    inadiplencia_df=pd.DataFrame()

    titulos_df['Ano']=titulos_df['Data de Vencimento'].dt.year

    inadiplencia_df=titulos_df.loc[titulos_df['Status do Título']=='VENCIDO']

    tit_venc=len(inadiplencia_df['Título'].unique().tolist())

    tot_venc=inadiplencia_df['Saldo R$'].sum()

    tit_as=len(inadiplencia_df['Título'].loc[inadiplencia_df['Canal']=='AS'].unique().tolist())

    tit_fs=len(inadiplencia_df['Título'].loc[inadiplencia_df['Canal']=='FS'].unique().tolist())

    tot_fs=inadiplencia_df['Saldo R$'].loc[inadiplencia_df['Canal']=='FS'].sum()

    tot_as=inadiplencia_df['Saldo R$'].loc[inadiplencia_df['Canal']=='AS'].sum()

    perc_as=round(tit_as/tit_venc,4)*100

    perc_fs=round(tit_fs/tit_venc,4)*100

    grupo_df=inadiplencia_df[['Alerta','Saldo R$']].groupby(['Alerta'],as_index=False).sum()

    grupo_df.sort_values('Saldo R$',ascending=False,ignore_index=True,inplace=True)

    ano_df=pd.DataFrame()

    ano_df=inadiplencia_df[['Ano','Saldo R$']].groupby(['Ano'],as_index=False).sum()

    ano_df['Ano']=ano_df['Ano'].astype('str')

    consolidado_df={

    "Mínimo" :float(0),
    "Máximo" :float(100),
    "Títulos Inadimplência" :float(tit_venc),
    "Total R$" :float(tot_venc),
    "Títulos AS" :float(tit_as),
    "Títulos FS" :float(tit_fs),
    "Total AS" :float(tot_as),
    "Total FS" :float(tot_fs),
    "Percentual AS" :float(perc_as),
    "Percentual FS" :float(perc_fs)

    }

    canal_df=pd.DataFrame()

    canal_df=inadiplencia_df[['Segmento','Canal','Saldo R$']].groupby(['Segmento','Canal'],as_index=False).sum()

    canal_df.sort_values('Saldo R$',ascending=False,ignore_index=True,inplace=True)

    total=canal_df['Saldo R$'].sum()

    canal_df['Total Geral']=total

    res=0

    valores=[]

    for indice,linha in canal_df.iterrows():
        
        res=canal_df['Saldo R$'].iloc[:indice+1].sum()
        
        valores.append(res)
        
        pass

    canal_df['Acumulado']=valores

    canal_df['Perc %']=canal_df.apply(lambda info: round(info['Acumulado']/info['Total Geral'],4)*100,axis=1)

    canal_df['Classificação']=canal_df['Perc %'].apply(Classificacao)

    canal_df=canal_df.loc[canal_df['Classificação']!='C']  

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/69f1f253-d6d4-4367-9da1-b62a6a030f89/rows?noSignUpCheck=1&key=9HFEI%2FkzE%2BuhVdYz6Rb38M6XaXtzK%2B%2BxnJtWMqA1kJGjupTv%2BrH5NIQO2ZZWUSfnED7fy%2BKew7JDq71Q9N91RA%3D%3D',json=grupo_df.to_dict('records'))

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/e47e6cde-b12b-4950-895b-534a071dc9ba/rows?key=Yzby5QNnYNmOhoDXnQf0MK83bxDKo5BADxA77MAqPBk7MgrAdquVzg3OnuX%2B%2BssaoQhhW%2FGWBDoaLzcyw1UOxw%3D%3D',json=consolidado_df)

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/ad32c9c3-441d-4a9f-8ce3-7b42ed5d26b0/rows?key=P%2Fsk8MMXk%2Fs4%2FHZKJc4PuLKiXH5SEbTjgbwOT3hx5a9dr9d4DP3%2BvuI%2BFLwyEUBmv3LF3gR9d9gpT5bw28CCBA%3D%3D',json=ano_df.to_dict('records'))

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/6e656dd0-af53-48b3-bf3b-3cdddd50ec47/rows?key=rBUCI7LdCCj20lYVPm%2FC478XWEKM65buHfcMgoRm6pzO9krswu%2Bz4ELzKoOfQtJJfAIqq8qNEKG2U7l%2BML62lQ%3D%3D',json=canal_df.to_dict('records'))

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