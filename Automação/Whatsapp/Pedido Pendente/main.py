from Acesso import Login
from Moeda import Moeda
from Query import Query
import os
from datetime import datetime,timedelta
import pandas as pd

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Pendente':

    """
    
    SELECT Origem,Situação,Pedido,NFe,[Tipo de Pedido],Tabelas,[Data de Emissão],[Data de Entrega],
	cli.[ID Cliente],cli.[Razão Social],cli.[Nome Fantasia],
	vend.[ID Vendedor],vend.[Nome Resumido],vend.Categoria,vend.DDD,vend.Telefone,sup.Equipe,
	sup.[ID Sup],sup.Supervisor,sup.[DDD Sup],sup.[Telefone Sup],sup.[ID Gerente],sup.Gerente,sup.[DDD Gerente],
	sup.[Telefone Gerente],
	prod.SKU,prod.Produto,prod.Fabricante,[Unid. VDA],[Qtde. VDA],[Valor VDA],[Total Venda]
	FROM netfeira.vw_targetestatistico vda
	INNER JOIN netfeira.vw_cliente cli ON vda.[ID Cliente]=cli.[ID Cliente]
	INNER JOIN netfeira.vw_vendedor vend ON vda.[ID Vendedor]=vend.[ID Vendedor]
	INNER JOIN netfeira.vw_supervisor sup ON vend.[ID Equipe]=sup.[ID Equipe]
	INNER JOIN netfeira.vw_produto prod ON vda.SKU=prod.SKU
    WHERE [ID Situação]='AB' AND [Data de Entrega]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101) 
    AND [Data de Emissão]=DATEADD(DAY,-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101))
    AND [Tipo de Operação]<>'OUTROS' 
    
    """

}


def Main(df):

    colunas={'ID Vendedor':'ID Sup','ID Sup':'ID Gerente','ID Gerente':'ID Gerente'}

    nomes={'ID Vendedor':'Nome Resumido','ID Sup':'Supervisor','ID Gerente':'Gerente'}

    col_ddd={'ID Vendedor':'DDD','ID Sup':'DDD Sup','ID Gerente':'DDD Gerente'}

    col_tel={'ID Vendedor':'Telefone','ID Sup':'Telefone Sup','ID Gerente':'Telefone Gerente'}

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])
    
    for col1,col2 in colunas.items():

        if(len(df['Pendente'])<=0):

            continue
        
        codigos=df['Pendente'][col1].loc[(df['Pendente']['Categoria']=='CLT')&(~df['Pendente'][col_tel[col1]].isnull())].unique().tolist()

        for c in codigos:

            temp_df=pd.DataFrame()

            sup=df['Pendente'][col2].loc[(df['Pendente'][col1]==c)].unique().tolist()[-1]

            if(col1=='ID Gerente'):

                temp_df=df['Pendente'].loc[(df['Pendente'][col1]==c)]

                nome=str(df['Pendente'][nomes[col1]].loc[(df['Pendente'][col1]==c)].unique().tolist()[-1]).title()

                ddd=df['Pendente'][col_ddd[col1]].loc[(df['Pendente'][col1]==c)].unique().tolist()[-1]

                telefone=df['Pendente'][col_tel[col1]].loc[(df['Pendente'][col1]==c)].unique().tolist()[-1]

                pass

            else:

                if(c==sup):

                    continue

                temp_df=df['Pendente'].loc[(df['Pendente'][col1]==c)]

                nome=str(df['Pendente'][nomes[col1]].loc[(df['Pendente'][col1]==c)].unique().tolist()[-1]).title()

                ddd=df['Pendente'][col_ddd[col1]].loc[(df['Pendente'][col1]==c)].unique().tolist()[-1]

                telefone=df['Pendente'][col_tel[col1]].loc[(df['Pendente'][col1]==c)].unique().tolist()[-1]                

                pass

            assunto='Pedios não faturados'

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            pedido=Moeda.Numero(len(temp_df['Pedido'].unique().tolist()))

            total=Moeda.FormatarMoeda(temp_df['Total Venda'].sum())

            data=datetime.strftime(datetime.now()-timedelta(days=1),'%d/%m/%Y')

            mensagem=f"""
            
            {assunto}

            {msg};

            {nome} tudo bem, identificamos referente ao dia {data} cerca de {pedido} pedido(s) que não foram faturados. E o valor total R$ {total}.
            
            """

            temp_df=temp_df[['Origem', 'Situação', 'Pedido', 'NFe', 'Tipo de Pedido', 'Tabelas',
       'Data de Emissão', 'Data de Entrega', 'ID Cliente', 'Razão Social',
       'Nome Fantasia', 'ID Vendedor', 'Nome Resumido','Equipe','SKU',
       'Produto', 'Fabricante', 'Unid. VDA', 'Qtde. VDA', 'Valor VDA',
       'Total Venda']]

            df['Pedidos']=temp_df

            df['Cliente']=temp_df.groupby(['ID Cliente','Razão Social','Nome Fantasia'],as_index=False).agg({'Total Venda':'sum'}).sort_values('Total Venda',ascending=False,ignore_index=True)

            writer=pd.ExcelWriter(f'{nome}.xlsx',engine='xlsxwriter')
            
            tabelas=['Cliente','Pedidos']

            for tabela in tabelas:

                df[tabela].to_excel(writer,sheet_name=tabela,index=False)

                pass

            writer.save()

            temp_path=os.path.join(os.getcwd(),f'{nome}.xlsx')

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,temp_path]
            
            pass

        pass

    whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)

    pass


if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass