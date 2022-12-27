from Acesso import Login
from Query import Query
from Moeda import Moeda
import os
import pandas as pd
from datetime import datetime,timedelta

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)


querys={

    'Devolucao':

    """
    
    SELECT *
    FROM netfeira.vw_devolucao
    WHERE [Data de Entrada]=DATEADD(DAY,-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)) 
    AND [Situação do Pedido]<>'CANCELADO' 
    
    """,

    'Vendedor':

    """
    
    SELECT * FROM netfeira.vw_vendedor
    WHERE [Status do Vendedor]='ATIVO'
    
    """,

    'Supervisor':

    """
    
    SELECT * FROM netfeira.vw_supervisor
    
    """,

    'Produto':

    """
   
    SELECT SKU,Produto,Fabricante 
    FROM netfeira.vw_produto

    """,

    'Cliente':

    """
    
    SELECT [ID Cliente],[Razão Social],[Nome Fantasia] 
    FROM netfeira.vw_cliente
    
    """

}

def Main(df):

    df['Vendedor']=df['Vendedor'].merge(df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria', 'Data de Cadastro', 'Status do Vendedor', 'DDD',
        'Telefone','ID Sup', 'Supervisor', 'Email Sup', 'DDD Sup',
        'Telefone Sup', 'ID Gerente', 'Gerente', 'Email Gerente', 'DDD Gerente',
        'Telefone Gerente']]

    df['Devolucao']=df['Devolucao'].merge(df['Cliente'],on='ID Cliente',how='inner')

    df['Devolucao']=df['Devolucao'].merge(df['Produto'],on='SKU',how='inner')

    df['Devolucao']=df['Devolucao'].merge(df['Vendedor'],on='ID Vendedor',how='inner')

    df['Devolucao']=df['Devolucao'][['Data de Entrada', 'Motivo',
        'Situação do Pedido', 'Tipo de Pedido', 'Tipo de Operação', 'Tabelas',
        'Pedido', 'NFe', 'ID Cliente','Razão Social', 'Nome Fantasia', 'ID Vendedor','Vendedor',
        'Nome Resumido', 'Equipe', 'E-mail', 'Categoria', 'Data de Cadastro',
        'Status do Vendedor', 'DDD', 'Telefone', 'ID Sup', 'Supervisor',
        'Email Sup', 'DDD Sup', 'Telefone Sup', 'ID Gerente', 'Gerente',
        'Email Gerente', 'DDD Gerente', 'Telefone Gerente', 'SKU','Produto', 'Fabricante', 'Qtde',
        'Unid. VDA', 'Qtde VDA', 'Valor Unitário', 'Total Geral']]


    colunas={'ID Vendedor':'ID Sup','ID Sup':'ID Gerente','ID Gerente':'ID Gerente'}

    nomes={'ID Vendedor':'Nome Resumido','ID Sup':'Supervisor','ID Gerente':'Gerente'}

    col_ddd={'ID Vendedor':'DDD','ID Sup':'DDD Sup','ID Gerente':'DDD Gerente'}

    col_tel={'ID Vendedor':'Telefone','ID Sup':'Telefone Sup','ID Gerente':'Telefone Gerente'}

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    for col1,col2 in colunas.items():

        codigos=df['Devolucao'][col1].loc[(df['Devolucao']['Categoria']=='CLT')&(~df['Devolucao']['Telefone'].isnull())].unique().tolist()
        
        for c in codigos:
            
            temp_df=pd.DataFrame()
            
            sup=df['Devolucao'][col2].loc[df['Devolucao'][col1]==c].unique().tolist()[-1]
            
            if(col1=='ID Gerente'):
                
                nome=str(df['Devolucao'][nomes[col1]].loc[df['Devolucao'][col1]==c].unique().tolist()[-1]).title()
                
                ddd=df['Devolucao'][col_ddd[col1]].loc[df['Devolucao'][col1]==c].unique().tolist()[-1]
                
                telefone=df['Devolucao'][col_tel[col1]].loc[df['Devolucao'][col1]==c].unique().tolist()[-1]
                
                temp_df=df['Devolucao'].loc[df['Devolucao'][col1]==c]
                
                pass
            
            else:

                if(c==sup):

                    continue
            
                nome=str(df['Devolucao'][nomes[col1]].loc[df['Devolucao'][col1]==c].unique().tolist()[-1]).title()
                
                ddd=df['Devolucao'][col_ddd[col1]].loc[df['Devolucao'][col1]==c].unique().tolist()[-1]
                
                telefone=df['Devolucao'][col_tel[col1]].loc[df['Devolucao'][col1]==c].unique().tolist()[-1]
                
                temp_df=df['Devolucao'].loc[df['Devolucao'][col1]==c]
                            
                pass

            if(len(temp_df)<=0 or datetime.now().day==1):

                continue

            total=Moeda.FormatarMoeda(temp_df['Total Geral'].sum())

            pedido=Moeda.Numero(len(temp_df['Total Geral'].unique().tolist()))

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'
                    
            assunto='Devolução'

            data=datetime.strftime(datetime.now()-timedelta(days=1),'%d/%m/%Y')

            mensagem=f"""
            
            {assunto}

            {msg};

            {nome} tudo bem, identificamos referente ao {data} cerca de {pedido} pedido(s) que foram devolvido(s) dando um total de R$ {total}
            
            """

            temp_df=temp_df[['Data de Entrada', 'Motivo',
        'Situação do Pedido', 'Tipo de Pedido', 'Tipo de Operação', 'Tabelas',
        'Pedido', 'NFe', 'ID Cliente','Razão Social', 'Nome Fantasia', 'ID Vendedor','Vendedor',
        'Nome Resumido', 'Equipe','SKU','Produto', 'Fabricante', 'Qtde',
        'Unid. VDA', 'Qtde VDA', 'Valor Unitário', 'Total Geral']]

            temp_df.to_excel(f'{nome}.xlsx',index=False,encoding='UTF-8')

            temp_path=os.path.join(os.getcwd(),f'{nome}.xlsx')

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,temp_path]            
            
            pass
                            
        pass

    whatsapp_df.to_excel(f'whatsapp.xlsx',index=False,encoding='UTF-8')

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass