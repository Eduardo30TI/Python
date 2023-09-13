from Acesso import Login
from Query import Query
import pandas as pd

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'Vendas':
    
    """
    
    DECLARE @DTBASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    IF MONTH(@DTBASE)=1

        BEGIN

            SET @DTFIM=DATEADD(DAY,-365,DATEADD(DAY,DAY(@DTBASE)*-1,@DTBASE))

            SET @DTINICIO=DATEADD(DAY,-365,DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))

        END;


    ELSE

        BEGIN

            SET @DTFIM=@DTBASE

            SET @DTINICIO=DATEADD(DAY,-365,DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))

        END;

    SELECT * FROM netfeira.vw_targetestatistico
    WHERE [ID Situação]='FA' AND [Tipo de Operação]='VENDAS'
	AND [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM
    
    """,
    
    'Receber':
    
    """
    
    SELECT * FROM netfeira.vw_contareceber
    WHERE Situação<>'CANCELADO'
        
    """,
    
    'Calendario':
    
    """
    
    SELECT * FROM netfeira.vw_calend
    
    """,
    
    'Data':
    
    """
    
    DECLARE @DTBASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    IF DAY(@DTBASE)=1

        BEGIN

            SET @DTFIM=DATEADD(DAY,DAY(@DTBASE)*-1,@DTBASE)

            SET @DTINICIO=DATEADD(DAY,1,DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))

        END;


    ELSE

        BEGIN

            SET @DTFIM=DATEADD(DAY,DAY(@DTBASE)*-1,@DTBASE)

            SET @DTINICIO=DATEADD(DAY,1,DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))

        END;

    SELECT @DTFIM AS [Anterior DTFIM],@DTINICIO AS [Anterior DTINICIO],
    @DTBASE DTFIM,
    DATEADD(DAY,1,DATEADD(DAY,DAY(@DTBASE)*-1,@DTBASE)) AS DTINICIO
    
    """,
    
    'Notas':
    
    """
    
    SELECT NFe 
	FROM netfeira.vw_targetestatistico
    WHERE [ID Situação]='FA' AND [Tipo de Operação]='VENDAS'
	GROUP BY NFe
    
    """
    
}

def Main(df):

    notas=df['Notas']['NFe'].unique().tolist()

    df['Receber']=df['Receber'].loc[df['Receber']['Título'].isin(notas)]

    #datas

    dt_antfim=df['Data']['Anterior DTFIM'].max()

    dt_antinicio=df['Data']['Anterior DTINICIO'].max()

    dt_fim=df['Data']['DTFIM'].max()

    dt_inicio=df['Data']['DTINICIO'].max()

    #Análise de dados
    df['Analise']=df['Receber'].loc[~df['Receber']['Data de Emissão'].between(dt_inicio,dt_fim)]

    df['Analise']=df['Analise'].loc[(df['Analise']['ID Situação'].isin(['AB','PL']))&(df['Analise']['Data de Fluxo'].between(dt_inicio,dt_fim))]

    total_pendente=round(df['Analise']['Valor'].sum(),2)

    #mensal

    df['Mensal']=df['Receber'].loc[(df['Receber']['Data de Emissão'].between(dt_inicio,dt_fim))]

    df['Mensal']=df['Mensal'].merge(df['Calendario'],left_on='Data de Fluxo',right_on='Data',how='inner')

    df['Mensal']=df['Mensal'].groupby(['ID Mês','Mês'],as_index=False).agg({'Valor':'sum'})

    df['Mensal']['Total']=df['Mensal']['Valor'].sum()

    df['Mensal']['Perc']=df['Mensal'].apply(lambda info: round(info['Valor']/info['Total'],4)*100 if info['Total']>0 else 0,axis=1)

    total_receber=round(df['Mensal']['Valor'].sum(),2)

    print(total_pendente)

    pass


if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass