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
    WHERE [Status do Vendedor]='ATIVO'
    
    """,

    'Supervisor':

    """
    
    SELECT [ID Equipe],Equipe,[ID Sup],Supervisor,[DDD Sup],[Telefone Sup],
    [ID Gerente],Gerente,[DDD Gerente],[Telefone Gerente]
    FROM netfeira.vw_supervisor
    
    """,

    'Aberto':

    """
    
    DECLARE @DTBASE DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SELECT Pedido,[ID Cliente],[ID Vendedor],SKU,[Unid. VDA],[Qtde VDA],[Valor VDA],[Total Venda]
	FROM netfeira.vw_aberto
    WHERE [Data do Pedido]=@DTBASE
    
    """

}

def Main(df):

    df['Analise']=df['Aberto'].groupby(['ID Vendedor'],as_index=False).agg({'Total Venda':'sum'})

    df['Analise']['Pedidos']=df['Analise']['ID Vendedor'].apply(lambda codigo: len(df['Aberto']['Pedido'].loc[(df['Aberto']['ID Vendedor']==codigo)].unique().tolist()))

    df['Analise']['Clientes']=df['Analise']['ID Vendedor'].apply(lambda codigo: len(df['Aberto']['ID Cliente'].loc[(df['Aberto']['ID Vendedor']==codigo)].unique().tolist()))

    df['Analise']['Produtos']=df['Analise']['ID Vendedor'].apply(lambda codigo: len(df['Aberto']['SKU'].loc[(df['Aberto']['ID Vendedor']==codigo)].unique().tolist()))

    df['Vendedor']=df['Vendedor'].merge(df['Supervisor'],on='ID Equipe',how='inner')

    df['Vendedor']=df['Vendedor'][['ID Vendedor', 'Nome Resumido', 'DDD', 'Telefone',
        'Equipe','ID Sup','Supervisor','DDD Sup','Telefone Sup','ID Gerente','Gerente','DDD Gerente','Telefone Gerente']]

    df['Vendedor']=df['Vendedor'].merge(df['Analise'],on='ID Vendedor',how='inner')

    df['Vendedor'].rename(columns={'Total Venda':'Realizado R$'},inplace=True)

    df['Vendedor'].sort_values('Realizado R$',ascending=False,inplace=True)

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    if(len(df['Vendedor'])>0):

        colunas={'ID Sup':'ID Gerente','ID Gerente':'ID Gerente'}

        col_nome={'ID Sup':'Supervisor','ID Gerente':'Gerente'}

        col_ddd={'ID Sup':'DDD Sup','ID Gerente':'DDD Gerente'}

        col_tel={'ID Sup':'Telefone Sup','ID Gerente':'Telefone Gerente'}

        for coluna in colunas.keys():

            temp_df=pd.DataFrame()

            supervisores=[l for l in df['Vendedor'][coluna].unique().tolist() if l]

            for sup in supervisores:

                temp_df=df['Vendedor'].loc[df['Vendedor'][coluna]==sup]

                gerentes=[l for l in temp_df[colunas[coluna]].unique().tolist() if l]
                
                if(sup in gerentes):

                    if(coluna=='ID Sup'):

                        continue

                    nome=str(temp_df[col_nome[colunas[coluna]]].loc[temp_df[colunas[coluna]]==sup].unique().tolist()[-1]).title()

                    temp_df=temp_df.loc[temp_df[colunas[coluna]]==sup]
                                        
                    pass

                else:
                    
                    nome=str(temp_df[col_nome[coluna]].loc[temp_df[coluna]==sup].unique().tolist()[-1]).title()

                    temp_df=temp_df.loc[temp_df[coluna]==sup]

                    pass

                ddd=temp_df[col_ddd[coluna]].unique().tolist()[-1]

                telefone=temp_df[col_tel[coluna]].unique().tolist()[-1]

                temp_df=temp_df[['ID Vendedor','Nome Resumido','Equipe','Realizado R$','Pedidos','Clientes','Produtos']]

                temp_dict=dict()

                col=temp_df.columns[3:]

                for c in col:

                    temp_dict[c]=temp_df[c].sum()

                    pass
                
                msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

                total=Moeda.FormatarMoeda(temp_dict['Realizado R$'])

                pedido=Moeda.Numero(temp_dict['Pedidos'])

                cliente=Moeda.Numero(temp_dict['Clientes'])

                mensagem=f"""
                
                Realizado Geral

                {msg};

                {nome} tudo bem, estou aqui para te informar que sua equipe atendeu {cliente} cliente(s) e fez {pedido} pedido(s). Dando um total R$ {total}.               
                
                """

                temp_df.to_excel(f'{nome}.xlsx',index=False)

                temp_path=os.path.join(os.getcwd(),f'{nome}.xlsx')

                whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,temp_path]

                pass
                                                
            pass

        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)

        pass

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass