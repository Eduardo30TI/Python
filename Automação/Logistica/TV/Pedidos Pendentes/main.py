from Acesso import Login
from Query import Query
import pandas as pd
import requests

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'Pedidos':
    
    """
    
    SELECT * FROM netfeira.vw_pedpendente
    
    """,
    
    'Cliente':
    
    """
    
    SELECT * FROM netfeira.vw_cliente
    
    """
    
}


def Main(tabelas_df):

    pedidos_df=pd.DataFrame()

    pedidos_df=tabelas_df['Pedidos']

    cliente_df=pd.DataFrame()

    cliente_df=tabelas_df['Cliente']

    pedidos_df=pedidos_df.merge(cliente_df,on='ID Cliente',how='inner')[['Seq. Evento', 'Rota', 'Tipo de Entrega', 'Fila', 'Pedido',
        'ID Cliente','CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'ID Segmento', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato', 'Limite de Crédito',
        'Principal', 'E-mail Cliente', 'Tributação do Cliente', 'ID Rota',
        'Latitude', 'Longitude', 'ID Usuário', 'Data da Expedição', 'Data do Pedido',
        'Tipo de Pedido', 'Tabela', 'ID Vendedor', 'Origem', 'SKU', 'Seq.',
        'Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA', 'Total Venda','Total Geral',
        'Peso Bruto KG', 'Peso Líquido KG']]

    Analise(pedidos_df)

    pass


def Analise(pedidos_df):

    links={

        'Consolidado':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/13e5ffed-f8ab-4ce8-b781-21df7f1a6b33/rows?key=0fGhthZtgYn%2FKEJmHg%2F2PE08dNajEetb7vUm%2Fted0lVL8OsDm60ddDhe%2FtBZllC0OOVd1dQQLSspmP1qw2hzRg%3D%3D',

        'Rota':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/9b451a3d-4fca-4b3f-aaa6-96b567bc5945/rows?key=5Rdo8hlyYpQw0yR5X0QJxyMcZkG%2BZxJcU%2BrmU7fu39tbWGUk15WzHW8bdYMXWbOrhkDRL9wEhAKT4u1nmr2Y6A%3D%3D',

        'Clientes':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/ee976a16-0555-4231-9429-374186b5d49c/rows?key=gAEvvUqffnje5g9FHk0CADeqg%2BLqShgM%2F1LzYV%2BwXfY0hA2LpFvXsIKHO24rbJAw7yIk5SGxmjvoj9UQZ9rpFA%3D%3D'

    }

    pedidos=len(pedidos_df['Pedido'].unique().tolist())

    cliente=len(pedidos_df['ID Cliente'].unique().tolist())

    total=pedidos_df['Total Geral'].sum()

    peso=pedidos_df['Peso Bruto KG'].sum()

    mix=len(pedidos_df['SKU'].unique().tolist())

    #principais rotas

    rota_df=pd.DataFrame()

    rota_df=pedidos_df[['Rota','Total Geral','Peso Bruto KG']].groupby(['Rota'],as_index=False).sum()

    rota_df['Pedidos']=rota_df['Rota'].apply(lambda info: len(pedidos_df['Pedido'].loc[pedidos_df['Rota']==info].unique().tolist()))

    rota_df['Clientes']=rota_df['Rota'].apply(lambda info: len(pedidos_df['ID Cliente'].loc[pedidos_df['Rota']==info].unique().tolist()))

    rota_df.sort_values('Clientes',ascending=False,ignore_index=True,inplace=True)

    #redes
    matriz_df=pd.DataFrame()

    matriz_df=pedidos_df[['Matriz','Total Geral','Peso Bruto KG']].loc[~pedidos_df['Matriz'].isnull()].groupby(['Matriz'],as_index=False).sum()

    matriz_df['Pedidos']=matriz_df['Matriz'].apply(lambda info: len(pedidos_df['Pedido'].loc[pedidos_df['Matriz']==info].unique().tolist()))

    matriz_df['Clientes']=matriz_df['Matriz'].apply(lambda info: len(pedidos_df['ID Cliente'].loc[pedidos_df['Matriz']==info].unique().tolist()))

    matriz_df.sort_values('Total Geral',ascending=False,ignore_index=True,inplace=True)

    temp_dict=[

        {
        "Pedidos" :float(pedidos),
        "Cliente" :float(cliente),
        "Total R$" :float(total),
        "Peso Bruto" :float(peso),
        "MIX" :float(mix)
        }

    ]

    requests.post(url=links['Consolidado'],json=temp_dict)

    requests.post(url=links['Rota'],json=rota_df.to_dict('records'))

    requests.post(url=links['Clientes'],json=matriz_df.to_dict('records'))

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass