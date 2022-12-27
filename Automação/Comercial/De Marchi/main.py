from email.mime import base
from glob import glob
import pandas as pd
from Acesso import Login
from Query import Query
import requests

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'Vendas':
    
    """
    
    SELECT * FROM netfeira.vw_targetestatico
    
    """,
    
    'Produto':
    
    """
    
    SELECT * FROM netfeira.vw_produto
    
    """,
    
    'Cliente':
    
    """
    
    SELECT * FROM netfeira.vw_cliente
    
    """,
    
    'Segmento':
    
    """
    
    SELECT * FROM netfeira.vw_segmento
    
    
    """,
    
    'Calendario':
    
    """
    
    SELECT * FROM netfeira.vw_calend
    
    """
    
}

mes_util=0

mes_trab=0

def Main(tabelas_df):

    global mes_util

    global mes_trab

    vendas_df=pd.DataFrame()

    vendas_df=tabelas_df['Vendas']

    calend_df=pd.DataFrame()

    calend_df=tabelas_df['Calendario']

    mes_util=len(calend_df['ID Mês'].loc[(calend_df['Ano']==2022)].unique().tolist())

    mes_trab=len(calend_df['ID Mês'].loc[(calend_df['Ano']==2022)&(calend_df['ID Mês']<9)].unique().tolist())

    clien_df=pd.DataFrame()

    clien_df=tabelas_df['Cliente']

    clien_df=clien_df.merge(tabelas_df['Segmento'],on='ID Segmento',how='inner')[['ID Cliente', 'CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'Segmento','Canal', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato', 'Limite de Crédito',
        'Principal', 'E-mail Cliente', 'Tributação do Cliente', 'ID Rota',
        'Latitude', 'Longitude']]

        
    vendas_df=vendas_df.merge(tabelas_df['Produto'],on='SKU',how='inner')[['ID Empresa', 'Pedido', 'Nfe', 'ID Cliente', 'ID Vendedor',
        'Data de Emissão', 'Data de Faturamento', 'ID Motivo', 'Situação',
        'Tipo de Pedido', 'Tipo de Operação', 'ID Roteiro', 'ID Usuário',
        'Tabelas', 'Origem', 'Tipo de Entrega', 'Seq Roteiro', 'SKU','Produto','Grupo Indústria','Fabricante','Linha', 'Seq',
        'Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA', 'Total Venda', 'Total AV',
        'Total Geral', 'Margem Bruta R$', 'Comissão R$', 'IPI R$', 'PIS R$',
        'COFINS R$', 'ICMS R$', 'ICMS ST R$', 'Peso Bruto KG',
        'Peso Líquido KG', 'Cad Vendedor']]


    vendas_df=vendas_df.merge(clien_df,on='ID Cliente',how='inner')[['ID Empresa', 'Pedido', 'Nfe', 'ID Cliente','Nome Fantasia','Matriz','Segmento','Canal', 'ID Vendedor',
        'Data de Emissão', 'Data de Faturamento', 'ID Motivo', 'Situação',
        'Tipo de Pedido', 'Tipo de Operação', 'ID Roteiro', 'ID Usuário',
        'Tabelas', 'Origem', 'Tipo de Entrega', 'Seq Roteiro', 'SKU', 'Produto',
        'Grupo Indústria', 'Fabricante','Linha', 'Seq', 'Qtde', 'Unid. VDA', 'Qtde VDA',
        'Valor VDA', 'Total Venda', 'Total AV', 'Total Geral',
        'Margem Bruta R$', 'Comissão R$', 'IPI R$', 'PIS R$', 'COFINS R$',
        'ICMS R$', 'ICMS ST R$', 'Peso Bruto KG', 'Peso Líquido KG',
        'Cad Vendedor']]


    vendas_df=vendas_df.merge(calend_df,left_on='Data de Faturamento',right_on='Data',how='inner')[['ID Empresa', 'Pedido', 'Nfe', 'ID Cliente','Nome Fantasia','Matriz','Segmento','Canal', 'ID Vendedor',
        'Data de Emissão', 'Data de Faturamento','Ano','ID Mês', 'ID Motivo', 'Situação',
        'Tipo de Pedido', 'Tipo de Operação', 'ID Roteiro', 'ID Usuário',
        'Tabelas', 'Origem', 'Tipo de Entrega', 'Seq Roteiro', 'SKU', 'Produto',
        'Grupo Indústria', 'Fabricante','Linha', 'Seq', 'Qtde', 'Unid. VDA', 'Qtde VDA',
        'Valor VDA', 'Total Venda', 'Total AV', 'Total Geral',
        'Margem Bruta R$', 'Comissão R$', 'IPI R$', 'PIS R$', 'COFINS R$',
        'ICMS R$', 'ICMS ST R$', 'Peso Bruto KG', 'Peso Líquido KG',
        'Cad Vendedor']]

    Analise(vendas_df)

    pass

def Analise(vendas_df):

    links={
        
        'Consolidado':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/2e1b772a-f2df-4a08-8054-ec0ebf467bf5/rows?noSignUpCheck=1&key=dD9HPub381PO6%2Bu%2BtBF5aprRP%2B2JpHAcS%2B%2F5vP%2BLYFQP53E0xu2Gt3uqkc6Kgfz2laOzn0mnije1KWUzipEpMw%3D%3D',

        'Canais':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/1bbf6227-699a-42f1-8ec4-2e8006cd848e/rows?key=d0NOUQaG9DkKlw4L2vgZzNMjdmI5KevyqP%2BmD5sMt%2F8OXOZPyJQq4GAQ3w7sjSUIhc65qqR9mS3tGnInyDC34w%3D%3D',

        'Linha':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/382862c6-04c7-410f-b7df-f8c244bb56d1/rows?key=0%2BKNGn3OmgT245owb%2FGN3fwIY92i9cf6t6I3Xg3AmfAYYkWqDRnQ%2BzI5qlw7dkt3%2FcIzQZIGcD2cJlwbqCDMpA%3D%3D',

        'Produto':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/46bb2fe1-fdae-451c-bd65-0bc33786ac0c/rows?key=1lSp7muonxgp0DITAPI66MX2iLxkGWYQyLQFPX9PKwtTKPlsemytfME51IkLRAAG6TimzfvHEVkrPRWvVFaYyw%3D%3D'
    }

    ano_atual=vendas_df['Ano'].max()

    mes_atual=vendas_df['ID Mês'].loc[vendas_df['Ano']==ano_atual].max()

    grupos=['DE MARCHI','FRAGOLE']

    vendas_df=vendas_df.loc[(vendas_df['Tipo de Operação']!='OUTROS')&(vendas_df['Grupo Indústria'].isin(grupos))]

    ano_df=pd.DataFrame()

    ano_df=vendas_df[['Ano','Peso Líquido KG']].loc[vendas_df['Ano']<ano_atual].groupby(['Ano'],as_index=False).sum()

    ano_df.sort_values('Peso Líquido KG',ascending=False,inplace=True)

    ano_base=ano_df.iloc[0,0]

    #produtos curva abc

    produtos_df=pd.DataFrame()

    produtos_df=vendas_df[['SKU','Produto','Peso Líquido KG','Total Venda']].loc[vendas_df['Ano'].isin([ano_base])].groupby(['SKU','Produto'],as_index=False).sum()

    produtos_df.sort_values('Peso Líquido KG',ascending=False,ignore_index=True,inplace=True)

    produtos_df=produtos_df.loc[produtos_df['Peso Líquido KG']>0]

    val=[]

    soma=0

    for valores in produtos_df['Peso Líquido KG'].tolist():
        
        soma+=valores
        
        val.append(soma)
        
        pass

    produtos_df['Acumulado KG']=val

    total=produtos_df['Peso Líquido KG'].sum()

    produtos_df['Total KG']=total

    produtos_df['Perc %']=round(produtos_df['Acumulado KG']/produtos_df['Total KG'],4)

    produtos_df['Classificação']=produtos_df['Perc %'].apply(Classificacao)

    #produtos_df=produtos_df.loc[produtos_df['Classificação']!='C']

    temp_df=pd.DataFrame()

    temp_df=tabelas_df['Produto'][['SKU','Status']]

    produtos_df=produtos_df.merge(temp_df,on='SKU',how='inner')

    produtos_df=produtos_df.loc[produtos_df['Status']=='ATIVO']

    #funil de vendas por canal

    canal_df=pd.DataFrame()

    canal_df=vendas_df[['Canal','Peso Líquido KG','Total Venda']].loc[(vendas_df['Ano'].isin([ano_atual]))&(vendas_df['ID Mês']<mes_atual)].groupby(['Canal'],as_index=False).sum()

    canal_df['Projeção KG']=(canal_df['Peso Líquido KG']/mes_trab)*mes_util

    canal_df['Projeção R$']=(canal_df['Total Venda']/mes_trab)*mes_util

    canal_df['Ano Base KG']=canal_df['Canal'].apply(lambda info: vendas_df[['Peso Líquido KG']].loc[(vendas_df['Ano'].isin([ano_base]))&(vendas_df['Canal']==info)].sum())

    canal_df['Ano Base R$']=canal_df['Canal'].apply(lambda info: vendas_df[['Total Venda']].loc[(vendas_df['Ano'].isin([ano_base]))&(vendas_df['Canal']==info)].sum())

    canal_df['Perc KG']=(round(canal_df['Projeção KG']/canal_df['Ano Base KG'],4)-1)*100

    canal_df=canal_df.loc[canal_df['Perc KG']<0]

    canais=canal_df['Canal'].unique().tolist()

    #segmento

    segmento_df=pd.DataFrame()

    segmento_df=vendas_df[['Segmento','Peso Líquido KG','Total Venda']].loc[(vendas_df['Ano'].isin([ano_atual]))&(vendas_df['ID Mês']<mes_atual)&(vendas_df['Canal'].isin(canais))].groupby(['Segmento'],as_index=False).sum()

    segmento_df['Projeção KG']=(segmento_df['Peso Líquido KG']/mes_trab)*mes_util

    segmento_df['Projeção R$']=(segmento_df['Total Venda']/mes_trab)*mes_util

    segmento_df['Ano Base KG']=segmento_df['Segmento'].apply(lambda info: vendas_df[['Peso Líquido KG']].loc[(vendas_df['Ano'].isin([ano_base]))&(vendas_df['Segmento']==info)].sum())

    segmento_df['Ano Base R$']=segmento_df['Segmento'].apply(lambda info: vendas_df[['Total Venda']].loc[(vendas_df['Ano'].isin([ano_base]))&(vendas_df['Segmento']==info)].sum())

    segmento_df['Perc KG']=(round(segmento_df['Projeção KG']/segmento_df['Ano Base KG'],4)-1)*100

    segmento_df=segmento_df.loc[segmento_df['Perc KG']<0]

    segmentos=segmento_df['Segmento'].unique().tolist()

    #produtos por segmento

    temp_df=pd.DataFrame()

    for s in segmentos:

        lista_df=pd.DataFrame()
    
        lista_df=vendas_df[['SKU','Produto','Linha','Segmento','Peso Líquido KG','Total Venda']].loc[(vendas_df['Ano'].isin([ano_atual]))&(vendas_df['ID Mês']<mes_atual)&(vendas_df['Segmento']==s)].groupby(['SKU','Produto','Linha','Segmento'],as_index=False).sum()

        lista_df['Projeção KG']=(lista_df['Peso Líquido KG']/mes_trab)*mes_util

        lista_df['Projeção R$']=(lista_df['Total Venda']/mes_trab)*mes_util

        lista_df['Ano Base KG']=lista_df['SKU'].apply(lambda info: vendas_df[['Peso Líquido KG']].loc[(vendas_df['Ano'].isin([ano_base]))&(vendas_df['SKU']==info)&(vendas_df['Segmento']==s)].sum())

        lista_df['Ano Base R$']=lista_df['SKU'].apply(lambda info: vendas_df[['Total Venda']].loc[(vendas_df['Ano'].isin([ano_base]))&(vendas_df['SKU']==info)&(vendas_df['Segmento']==s)].sum())

        lista_df['Perc KG']=(round(lista_df['Projeção KG']/lista_df['Ano Base KG'],4)-1)*100

        lista_df=lista_df.loc[lista_df['Perc KG']<0]
        
        temp_df=pd.concat([lista_df,temp_df],axis=0,ignore_index=True)

        #break
        
        pass

    codigos=temp_df['SKU'].unique().tolist()

    #base de dados por produto

    base_df=pd.DataFrame()

    base_df=vendas_df.loc[(vendas_df['SKU'].isin(codigos))&(vendas_df['Canal'].isin(canais))&(vendas_df['Ano'].isin([ano_atual]))&(vendas_df['ID Mês']<mes_atual)]

    base_df=base_df[['SKU','Produto','Linha','Peso Líquido KG','Total Venda']].groupby(['SKU','Produto','Linha'],as_index=False).sum()

    base_df['Projeção KG']=(base_df['Peso Líquido KG']/mes_trab)*mes_util

    base_df['Projeção R$']=(base_df['Total Venda']/mes_trab)*mes_util

    base_df['Ano Base KG']=base_df['SKU'].apply(lambda info: vendas_df['Peso Bruto KG'].loc[(vendas_df['SKU']==info)&(vendas_df['Canal'].isin(canais))&(vendas_df['Ano'].isin([ano_base]))].sum())

    base_df['Ano Base R$']=base_df['SKU'].apply(lambda info: vendas_df['Total Venda'].loc[(vendas_df['SKU']==info)&(vendas_df['Canal'].isin(canais))&(vendas_df['Ano'].isin([ano_base]))].sum())

    base_df['Perc KG']=(round(base_df['Projeção KG']/base_df['Ano Base KG'],4)-1)*100

    base_df=base_df.loc[base_df['Perc KG']<0]

    temp_df=produtos_df[['SKU','Classificação']]

    base_df=base_df.merge(temp_df,on='SKU',how='inner')

    base_df.sort_values('Peso Líquido KG',ascending=False,ignore_index=True,inplace=True)

    #curva abc dos produtos

    curva_df=pd.DataFrame()

    curva_df=base_df.groupby(['Classificação'],as_index=False).agg({'Peso Líquido KG':'sum','Total Venda':'sum','Produto':'count'})

    curva_df['Perc %']=round(curva_df['Produto']/curva_df['Produto'].sum(),4)*100

    #linha

    linha_df=pd.DataFrame()

    linha_df=base_df.groupby(['Linha'],as_index=False).agg({'Peso Líquido KG':'sum','Total Venda':'sum','Produto':'count'})

    linha_df.sort_values('Peso Líquido KG',ascending=False,ignore_index=True,inplace=True)

    temp_dict=[
        {
        "Peso A KG" :float(curva_df['Peso Líquido KG'].loc[curva_df['Classificação']=='A'].sum()),
        "Total A R$" :float(curva_df['Total Venda'].loc[curva_df['Classificação']=='A'].sum()),
        "Produto A" :float(curva_df['Produto'].loc[curva_df['Classificação']=='A'].sum()),
        "Perc % A" :float(curva_df['Perc %'].loc[curva_df['Classificação']=='A'].sum()),
        "Peso B KG" :float(curva_df['Perc %'].loc[curva_df['Classificação']=='B'].sum()),
        "Total B R$" :float(curva_df['Perc %'].loc[curva_df['Classificação']=='B'].sum()),
        "Produto B" :float(curva_df['Perc %'].loc[curva_df['Classificação']=='B'].sum()),
        "Perc % B" :float(curva_df['Perc %'].loc[curva_df['Classificação']=='B'].sum()),
        "Peso C KG" :float(curva_df['Perc %'].loc[curva_df['Classificação']=='C'].sum()),
        "Total C R$" :float(curva_df['Perc %'].loc[curva_df['Classificação']=='C'].sum()),
        "Produto C" :float(curva_df['Perc %'].loc[curva_df['Classificação']=='C'].sum()),
        "Perc % C" :float(curva_df['Perc %'].loc[curva_df['Classificação']=='C'].sum()),
        "Máx" :float(100),
        "Mín" :float(0)

        }
    ]

    requests.post(url=links['Consolidado'],json=temp_dict)

    requests.post(url=links['Canais'],json=canal_df[['Canal','Peso Líquido KG']].to_dict('records'))

    requests.post(url=links['Linha'],json=linha_df[['Linha','Peso Líquido KG']].loc[base_df['Classificação']!='C'].to_dict('records'))

    requests.post(url=links['Produto'],json=base_df[['SKU','Produto','Peso Líquido KG']].loc[base_df['Classificação']!='C'].to_dict('records'))

    pass

def Classificacao(perc):
    
    perc=perc*100
    
    if(perc<=80):
        
        val='A'
        
        pass
    
    elif(perc<=95):
        
        val='B'
        
        pass
    
    else:
        
        val='C'
        
        pass
    
    
    return val
    
    pass

def Crescimento(vendas_df):

    grp_df=pd.DataFrame()

    ano_atual=vendas_df['Ano'].max()

    mes_atual=vendas_df['ID Mês'].loc[vendas_df['Ano']==ano_atual].max()    

    grp_df=vendas_df[['SKU','Produto','Fabricante','Linha','Ano','Peso Líquido KG']].loc[vendas_df['Ano']<ano_atual].groupby(['SKU','Produto','Fabricante','Linha','Ano'],as_index=False).sum()

    lista_ano=vendas_df['Ano'].unique().tolist()

    grp_df=grp_df.pivot(index=['SKU','Produto','Fabricante','Linha'],columns='Ano',values='Peso Líquido KG').reset_index()

    grp_df[vendas_df['Ano'].max()]=grp_df['SKU'].apply(lambda info: vendas_df['Peso Líquido KG'].loc[(vendas_df['SKU']==info)&(vendas_df['Ano']==ano_atual)&(vendas_df['ID Mês']<mes_atual)].sum())

    ano=grp_df.columns[-1]

    col=(f'Projeção {grp_df.columns[-1]} KG')

    grp_df[col]=(grp_df.iloc[:,-1]/mes_trab)*mes_util

    ult_col=grp_df.columns[-1]

    while True:
        
        ano-=1
        
        if(lista_ano.count(ano)>0):
            
            col=(f'Perc % {ano}')
            
            grp_df[col]=(round(grp_df[ult_col]/grp_df[ano],4)-1)*100
                            
            pass
        
        else:
                    
            break
            
            pass
        
        pass

    #codigos=tabelas_df['Produto']['SKU'].loc[tabelas_df['Produto']['Status']=='ATIVO'].tolist()

    colunas=grp_df.filter(like='Perc').columns.tolist()

    val=[]

    for i in grp_df.index.tolist():
        
        c=0
        
        temp=[]
        
        for e in grp_df.loc[i,colunas].tolist():
            
            if(e>0):
                
                temp.append(1)
                
                pass
            
            else:
                
                temp.append(0)
                
                pass
                            
            pass
        
        if(temp.count(1)==len(grp_df.loc[i,colunas].tolist())):
            
            val.append('CRESCIMENTO')
            
            pass
        
        else:
            
            if(temp[:3].count(0)==3):
                        
                val.append('QUEDA')
                
                pass
            
            else:
                
                val.append('')
                
                pass
            
            pass
        
        #break
        
        pass

    grp_df['Status Anual']=val

    grp_df.loc[grp_df[colunas].isnull().any(axis=1),'Status Anual']=''

    print(grp_df)

    pass

if __name__=='__main__':

    tabelas_df=sql.CriarTabela(kwargs=querys)

    Main(tabelas_df)

    pass