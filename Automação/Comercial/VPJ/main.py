from Acesso import Login
from Email import Email
from Moeda import Moeda
from RemoverArquivo import Remover
from Query import Query
import pandas as pd
from datetime import datetime
import os

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'vendas':

    """

    DECLARE @DTBASE DATETIME,@DTFIM DATETIME, @DTINICIO DATETIME,@SEMANASMAX SMALLINT

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @SEMANASMAX=(

    SELECT MAX([Semana Ano])-1
    FROM netfeira.vw_calend
    WHERE Data=@DTBASE

    )

    IF @SEMANASMAX=0

        BEGIN
        
        SET @DTFIM=DATEADD(DAY,DAY(@DTBASE)*-1,@DTBASE)

        SET @DTINICIO=DATEADD(DAY,-7,@DTFIM)

        END;

    ELSE


        BEGIN

        SET @DTFIM=(

        SELECT MAX(Data)
        FROM netfeira.vw_calend
        WHERE [Semana Ano]=@SEMANASMAX
        AND YEAR(Data)=YEAR(@DTBASE)

        )

        SET @DTINICIO=(

        SELECT MIN(Data)
        FROM netfeira.vw_calend
        WHERE [Semana Ano]=@SEMANASMAX
        AND YEAR(Data)=YEAR(@DTBASE)

        )
        
        END;


    SELECT a.[ID Cliente],c.[Razão Social],a.SKU,p.Produto,p.Fabricante,p.[Fator CX],a.Qtde,a.[Total Venda],
    CONVERT(INT,a.Qtde/NULLIF(p.[Fator CX],0)) AS Caixa
    FROM (

        SELECT ped.[ID Cliente],ped.SKU,
        SUM(ped.[Qtde]) AS Qtde,SUM(ped.[Total Geral]) AS [Total Venda]
        FROM netfeira.vw_venda_estatico ped
        WHERE [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM
        AND [Tipo de Operação] IN ('VENDAS','BONIFICAÇÃO')
        GROUP BY ped.[ID Cliente],ped.SKU

    )a
    INNER JOIN netfeira.vw_cliente c ON a.[ID Cliente]=c.[ID Cliente]
    INNER JOIN netfeira.vw_produto p ON a.SKU=p.SKU AND p.Fabricante='VPJ'

    """,

    'calendario':

    """

    DECLARE @DTBASE DATETIME,@DTFIM DATETIME, @DTINICIO DATETIME,@SEMANASMAX SMALLINT

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @SEMANASMAX=(

    SELECT MAX([Semana Ano])-1
    FROM netfeira.vw_calend
    WHERE Data=@DTBASE

    )

    IF @SEMANASMAX=0

        BEGIN
        
        SET @DTFIM=DATEADD(DAY,DAY(@DTBASE)*-1,@DTBASE)

        SET @DTINICIO=DATEADD(DAY,-7,@DTFIM)

        END;

    ELSE


        BEGIN

        SET @DTFIM=(

        SELECT MAX(Data)
        FROM netfeira.vw_calend
        WHERE [Semana Ano]=@SEMANASMAX
        AND YEAR(Data)=YEAR(@DTBASE)

        )

        SET @DTINICIO=(

        SELECT MIN(Data)
        FROM netfeira.vw_calend
        WHERE [Semana Ano]=@SEMANASMAX
        AND YEAR(Data)=YEAR(@DTBASE)

        )
        
        END;


    SELECT @DTINICIO AS DTINICIO,@DTFIM AS DTFIM


    """


}

def main():

    df=sql.CriarTabela(kwargs=querys)

    if len(df)>0:

        dt_min=datetime.strftime(df['calendario']['DTINICIO'].max(),'%d/%m/%Y')
        dt_max=datetime.strftime(df['calendario']['DTFIM'].max(),'%d/%m/%Y')

        msg='Bom dia' if datetime.now().hour else 'Boa tarde'

        temp_path=os.path.join(os.getcwd(),'SELL OUT VPJ.xlsx')

        assunto='SELL OUT VPJ - SP'
        
        mensagem=f"""

        <p>{msg};</p>

        <p>Andre</p>

        <p>Segue o SELL OUT referente ao dia {dt_min} até {dt_max}.</p>

        <P>Por favor não responder mensagem automática</P>

        <p>Atenciosamente</p>

        <p>BOT TI</p>


        """

        df['consolidado']=df['vendas'].groupby(['SKU','Produto','Fabricante'],as_index=False).agg({'Total Venda':'sum','Qtde':'sum','Caixa':'sum'})
        df['consolidado']['Cliente']=df['consolidado']['SKU'].apply(lambda info: len(df['vendas'].loc[df['vendas']['SKU']==info,'ID Cliente'].unique().tolist()))

        with pd.ExcelWriter(temp_path,engine='xlsxwriter') as excel:

            df['vendas'].to_excel(excel,sheet_name='Vendas',index=False)
            df['consolidado'].to_excel(excel,sheet_name='Produtos',index=False)

            pass

        temp_dict={'To':['andre.barbosa@vpjalimentos.com.br'],'CC':['julio@demarchibrasil.com.br','eduardo.marfim@demarchibrasil.com.br'],'Anexo':[temp_path]}

        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)
        Remover.RemoverArquivo('.xlsx')
        
        pass

    pass



if __name__=='__main__':

    main()

    pass