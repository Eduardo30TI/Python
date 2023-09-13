from Acesso import Login
from Query import Query
from Moeda import Moeda
import pandas as pd
from glob import glob
import os
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Vendedor':

    """
    
    SELECT [ID Vendedor],[Nome Resumido],[ID Equipe],DDD,Telefone 
    FROM netfeira.vw_vendedor
    WHERE [Status do Vendedor]='ATIVO' AND Categoria='CLT' AND Telefone IS NOT NULL
    
    """,

    'Supervisor':

    """
    
    SELECT [ID Equipe],Equipe,[ID Sup],Supervisor,[DDD Sup],[Telefone Sup],
    [ID Gerente],Gerente,[DDD Gerente],[Telefone Gerente]
    FROM netfeira.vw_supervisor
    WHERE NOT Equipe LIKE '%120%'
    
    """,

    'Aberto':

    """
    
    DECLARE @DTBASE DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SELECT Pedido,[ID Cliente],[ID Vendedor],SKU,[Unid. VDA],[Qtde VDA],[Valor VDA],[Total Venda]
	FROM netfeira.vw_aberto
    WHERE [Data do Pedido]=@DTBASE
    
    """,
    
    'Cliente':
    
    """
    
    SELECT [ID Cliente],[Razão Social],[Nome Fantasia]
    FROM netfeira.vw_cliente    
    
    """,
    
    'Produto':
    
    """
    
    SELECT SKU,Produto,Fabricante
    FROM netfeira.vw_produto    
    
    """

}

def Main(df):

    df['Analise']=df['Aberto'].groupby(['ID Vendedor'],as_index=False).agg({'Total Venda':'sum'})

    df['Analise']['Pedidos']=df['Analise']['ID Vendedor'].apply(lambda codigo: len(df['Aberto']['Pedido'].loc[(df['Aberto']['ID Vendedor']==codigo)].unique().tolist()))

    df['Analise']['Clientes']=df['Analise']['ID Vendedor'].apply(lambda codigo: len(df['Aberto']['ID Cliente'].loc[(df['Aberto']['ID Vendedor']==codigo)].unique().tolist()))

    df['Analise']['Produtos']=df['Analise']['ID Vendedor'].apply(lambda codigo: len(df['Aberto']['SKU'].loc[(df['Aberto']['ID Vendedor']==codigo)].unique().tolist()))

    df['Vendedor']=df['Vendedor'].merge(df['Supervisor'],on='ID Equipe',how='inner')

    df['Vendedor']=df['Vendedor'][['ID Vendedor', 'Nome Resumido', 'DDD', 'Telefone',
        'Equipe']]

    df['Vendedor']=df['Vendedor'].merge(df['Analise'],on='ID Vendedor',how='inner')

    df['Vendedor'].rename(columns={'Total Venda':'Realizado R$'},inplace=True)

    #lista de pedidos

    df['Aberto']=df['Aberto'].merge(df['Vendedor'],on='ID Vendedor',how='inner')[['Pedido', 'ID Cliente', 'ID Vendedor','Nome Resumido', 'Equipe', 'SKU', 'Unid. VDA', 'Qtde VDA',
        'Valor VDA', 'Total Venda']]

    df['Aberto']=df['Aberto'].merge(df['Cliente'],on='ID Cliente',how='inner')[['Pedido', 'ID Cliente','Razão Social', 'Nome Fantasia', 'ID Vendedor','Nome Resumido', 'Equipe', 'SKU', 'Unid. VDA', 'Qtde VDA',
        'Valor VDA', 'Total Venda']]

    df['Aberto']=df['Aberto'].merge(df['Produto'],on='SKU',how='inner')[['Pedido', 'ID Cliente','Razão Social', 'Nome Fantasia', 'ID Vendedor','Nome Resumido', 'Equipe', 'SKU','Produto', 'Fabricante', 'Unid. VDA', 'Qtde VDA',
        'Valor VDA', 'Total Venda']]

    temp_df=pd.DataFrame()

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    if(len(df['Aberto'])>0):

        for c in df['Vendedor']['ID Vendedor'].tolist():

            temp_df=df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==c]
            
            total=Moeda.FormatarMoeda(temp_df['Realizado R$'].sum())

            pedido=Moeda.Numero(temp_df['Pedidos'].sum())

            cliente=Moeda.Numero(temp_df['Clientes'].sum())

            nome=str(temp_df['Nome Resumido'].tolist()[-1]).title()

            ddd=temp_df.loc[temp_df['ID Vendedor']==c,'DDD'].tolist()[-1]

            telefone=temp_df.loc[temp_df['ID Vendedor']==c,'Telefone'].tolist()[-1]

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            mensagem=f"""

            Extrato de Pedido
            
            '{msg}';

            {nome} tudo bem, você atendeu {cliente} cliente(s) com {pedido} pedido(s). Dando um total de R$ {total}.
            
            """

            df['Aberto'].loc[df['Aberto']['ID Vendedor']==c].to_excel(f'{nome}.xlsx',index=False)

            temp_path=os.path.join(os.getcwd(),f'{nome}.xlsx')

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,temp_path]
                    
            pass

        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)

        pass

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass