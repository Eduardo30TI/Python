from Acesso import Login
from Query import Query
import os
from glob import glob
import pandas as pd
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'corte':

    """

    DECLARE @SEMANAMES SMALLINT, @DTFIM DATETIME,@DTINICIO DATETIME

    SET @SEMANAMES=(

        SELECT [Semana Ano]
        FROM netfeira.vw_calend
        WHERE Data=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    )

    SET @DTFIM=(

        SELECT MAX(Data)
        FROM netfeira.vw_calend
        WHERE [Semana Ano]=@SEMANAMES
        AND YEAR(Data)=YEAR(GETDATE())

    )


    SET @DTINICIO=(

        SELECT MIN(Data)
        FROM netfeira.vw_calend
        WHERE [Semana Ano]=@SEMANAMES
        AND YEAR(Data)=YEAR(GETDATE())

    );

    WITH TabCusto AS (

        SELECT c.SKU,c.[Última Entrada] 
        FROM netfeira.vw_custo c
        WHERE [Tipo de Custo]='ULTIMA ENTRADA' AND Status='ATIVO'

    )


    SELECT * FROM (

        SELECT a.SKU,a.Produto,a.Fabricante,a.Corte,a.[Data Máx],a.[Última Entrada],
        CONCAT(a.SKU,YEAR(a.[Data Máx]),MONTH(a.[Data Máx]),DAY(a.[Data Máx])) AS ID,
        DATEDIFF(DAY,a.[Última Entrada],a.[Data Máx]) AS Dias
        FROM (

            SELECT f.SKU,f.Produto,f.Fabricante,SUM(f.[Qtde. VDA]) AS Corte,MAX(f.[Data de Falta]) AS [Data Máx],c.[Última Entrada]
            FROM netfeira.vw_falta f
            INNER JOIN it_pedv_local i ON f.SKU=i.cd_prod AND f.Pedido=i.nu_ped
            INNER JOIN local l ON i.cd_emp=l.cd_emp AND i.cd_local=l.cd_local AND l.central=1
            INNER JOIN empresa emp ON l.cd_emp=emp.cd_emp AND emp.ativo=1
            INNER JOIN produto p ON f.SKU=p.cd_prod AND p.ativo=1
            INNER JOIN TabCusto c ON f.SKU=c.SKU
            WHERE f.[Data de Falta] BETWEEN @DTINICIO AND @DTFIM AND CONVERT(INT,f.[Qtde. VDA])>0
            GROUP BY f.SKU,f.Produto,f.Fabricante,c.[Última Entrada]

        )a

    )b
    WHERE b.Dias>0

    """
}

def main():

    df=sql.CriarTabela(kwargs=querys)

    temp_path=os.path.join(os.getcwd(),'memoria.csv')
    arq=glob(temp_path)

    temp_df=pd.DataFrame()

    if len(arq)>0:

        temp_df=pd.read_csv(temp_path,encoding='UTF-8')
        lista=df['corte']['ID'].unique().tolist()

        df['corte']=df['corte'].loc[~df['corte']['ID'].isin(lista)]

        pass

    if len(df['corte'])>0:
        
        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        contatos={'Omário':'11940240053','Compras':'11942987717','Edson':'11974660844','Julio':'11997683699','Renato':'11995088584'}

        for k,v in contatos.items():

            ddd=v[:2]
            telefone=v[2:]
            
            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            mensagem=f'{msg} {k} tudo bem? Aqui quem fala é a Iris, segue a relação de produtos que foram cortados. Caso esses itens não estiverem disponíveis, por favor fazer o bloqueio para não a ver a comercialização.\n\nRelação de itens:\n'

            for i in df['corte']['Produto'].index.tolist():

                codigo=df['corte'].loc[i,'SKU']
                produto=df['corte'].loc[i,'Produto']
                qtde=df['corte'].loc[i,'Corte']

                mensagem+=f'\n.*{codigo}-{produto}*\nTotal de Corte: {qtde}'

                pass

            whatsapp_df.loc[len(whatsapp_df)]=[k,ddd,telefone,mensagem,'']

            pass
                
        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)
        temp_df=pd.concat([temp_df,df['corte']],axis=0,ignore_index=True)
        temp_df.to_csv(temp_path,index=False)

        pass

    pass


if __name__=='__main__':

    main()

    pass