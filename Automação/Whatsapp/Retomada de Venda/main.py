from Acesso import Login
from Query import Query
import os
from glob import glob
import pandas as pd
from datetime import datetime
from Moeda import Moeda

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'venda':

    """

    DECLARE @DTBASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=DATEADD(DAY,1,DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))

    ;WITH TabVendas AS (

        SELECT [ID Cliente],SKU,SUM(Qtde) AS Qtde 
        FROM netfeira.vw_targetestatistico
        WHERE [ID Situação] IN ('AB','FA') AND [Tipo de Operação]='VENDAS'
        AND [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM
        GROUP BY [ID Cliente],SKU

    ),

    TabSTK AS (

        SELECT SKU,
        COUNT(SKU)OVER(PARTITION BY SKU) AS Disponível
        FROM netfeira.vw_estoque
        WHERE Tipo='CENTRAL' AND [Qtde Disponível]>0

    )

    SELECT a.[ID Cliente],a.[Nome Fantasia],c.Principal,v.[Nome Resumido],v.DDD,v.Telefone,
    a.SKU,a.Produto,a.Fabricante,a.Disponível,a.Qtde,a.Corte,a.[Data Máx],
    CONCAT(a.[ID Cliente],c.Principal,a.SKU,YEAR(a.[Data Máx]),MONTH(a.[Data Máx]),DAY(a.[Data Máx])) AS ID
    FROM (

        SELECT f.[ID Cliente],f.[Nome Fantasia],f.SKU,f.Produto,f.Fabricante,
        SUM(f.[Qtde. VDA]) AS Corte,v.Qtde,s.Disponível,MAX(f.[Data de Falta]) AS [Data Máx]
        FROM netfeira.vw_falta f
        INNER JOIN it_pedv_local i ON f.Pedido=i.nu_ped
        INNER JOIN local l ON i.cd_local=l.cd_local AND i.cd_emp=l.cd_emp
        INNER JOIN empresa emp ON l.cd_emp=emp.cd_emp AND emp.ativo=1
        INNER JOIN TabSTK s ON f.SKU=s.SKU
        LEFT JOIN TabVendas v ON f.[ID Cliente]=v.[ID Cliente] AND f.SKU=v.SKU
        WHERE f.[Data de Falta] BETWEEN DATEADD(DAY,-30,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101))
        AND DATEADD(DAY,-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101))
        GROUP BY f.[ID Cliente],f.[Nome Fantasia],f.SKU,f.Produto,f.Fabricante,v.Qtde,s.Disponível

    )a
    INNER JOIN produto p ON a.SKU=p.cd_prod AND p.venda=1 AND p.ativo=1
    INNER JOIN netfeira.vw_cliente c ON a.[ID Cliente]=c.[ID Cliente]
    INNER JOIN netfeira.vw_vendedor v ON c.Principal=v.[ID Vendedor] AND v.Telefone IS NOT NULL
    WHERE a.Qtde IS NULL AND a.Disponível IS NOT NULL
    ORDER BY c.Principal

    """,

    'carteira':

    """

    SELECT * FROM netfeira.vw_carteira
    WHERE Principal='SIM'

    """

}

def main():

    df=sql.CriarTabela(kwargs=querys)

    path_base=os.path.join(os.getcwd(),'Memoria')
    os.makedirs(path_base,exist_ok=True)
    path_base=os.path.join(path_base,'memoria.csv')
    arq=glob(path_base)

    excel_df=pd.DataFrame()

    if len(arq)>0:
                
        excel_df=pd.read_csv(arq[-1])
        lista=excel_df['ID'].unique().tolist()
 
        df['venda']=df['venda'].loc[~df['venda']['ID'].isin(lista)]

        pass

    if len(df['venda'])>0:

        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        for c in df['venda']['Principal'].unique().tolist():

            temp_df=pd.DataFrame()
            temp_df=df['venda'].loc[df['venda']['Principal']==c]
            
            nome=str(temp_df.loc[temp_df['Principal']==c,'Nome Resumido'].unique().tolist()[-1]).title()
            ddd=temp_df.loc[temp_df['Principal']==c,'DDD'].unique().tolist()[-1]
            telefone=temp_df.loc[temp_df['Principal']==c,'Telefone'].unique().tolist()[-1]
            lista=temp_df.loc[temp_df['Principal']==c,'Produto'].unique().tolist()

            clientes=Moeda.Numero(len(df['venda'].loc[df['venda']['Principal']==c,'ID Cliente'].unique().tolist()))

            mensagem=f'Olá {nome} tudo bem? Sou Iris um assistente virtual da DE MARCHI SP estou mandando uma relação contendo {clientes} cliente(s) que teve interesse em alguns de nossos produtos que agora está disponível para venda. Peço que entre em contato para que possamos sempre melhorar nossa parceria. Grato e tenha um excelente dia.\n\nProdutos:\n'

            for p in lista:

                mensagem+=f'\n.*{p}*'

                for i in temp_df.loc[temp_df['Produto']==p].index.tolist():

                    codigo=temp_df.loc[i,'ID Cliente']
                    cliente=temp_df.loc[i,'Nome Fantasia']

                    cliente=f'{codigo} - {cliente}'

                    mensagem+=f'\n\t.{cliente}'

                    pass
                
                mensagem+='\n'

                pass

            lista=temp_df['ID Cliente'].unique().tolist()
            temp_df=df['carteira'].loc[df['carteira']['ID Cliente'].isin(lista)]
            
            temp_path=os.path.join(os.getcwd(),f'{nome}.xlsx')
            temp_df.to_excel(temp_path,index=False)
                                    
            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,temp_path]

            #break

            pass

        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)
        temp_df.drop(columns=temp_df.columns.tolist(),inplace=True)
        temp_df=pd.concat([excel_df,df['venda']],axis=0,ignore_index=True)
        temp_df.to_csv(path_base,index=False,encoding='UTF-8')

        pass

    pass


if __name__=='__main__':

    main()

    pass