from Acesso import Login
from Query import Query
from Moeda import Moeda
import pandas as pd
from datetime import datetime
import os
from glob import glob

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Meta':

    """

    SELECT * FROM netfeira.vw_metas
    WHERE [Meta R$]>0
    
    """,

    'Vendedor':

    """
    
    SELECT * FROM netfeira.vw_vendedor
    WHERE Categoria='CLT' AND [Status do Vendedor]='ATIVO' AND Telefone IS NOT NULL
    
    """,

    'Supervisor':

    """
    
    SELECT * FROM netfeira.vw_supervisor
    WHERE NOT Equipe LIKE '%120%'
    
    """,

    'Estatico':

    """
    
    DECLARE @DTBASE DATETIME, @DTFIM DATETIME,@DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=CONCAT(YEAR(@DTFIM),'-',MONTH(@DTFIM),'-01')

    SELECT * FROM netfeira.vw_targetestatico
    WHERE [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM AND [Tipo de Operação]='VENDAS'
    
    """,

    'Aberto':

    """
    
    DECLARE @DTBASE DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SELECT *
	FROM netfeira.vw_aberto
    WHERE [Data do Pedido]=@DTBASE
    
    """,

    'Calendario':

    """
    
    DECLARE @DTBASE DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SELECT COUNT(DATA) AS [Útil],COUNT([Data Trabalhada])-1 AS [Trabalhado],
    COUNT(DATA)-(COUNT([Data Trabalhada])-1) AS [Restante]
    FROM netfeira.vw_calend
    WHERE YEAR(Data)=YEAR(@DTBASE) AND MONTH(Data)=MONTH(@DTBASE) AND [Dia Útil]=1    
    
    """

}

def Main(df):

    df['Consolidado']=df['Estatico'].groupby(['ID Vendedor'],as_index=False).agg({'Total Venda':'sum'})

    df['Consolidado'].rename(columns={'Total Venda':'Faturado'},inplace=True)

    df['Pendente']=df['Aberto'].loc[df['Aberto']['Situação']=='AB'].groupby(['ID Vendedor'],as_index=False).agg({'Total Venda':'sum'})

    df['Pendente'].rename(columns={'Total Venda':'Em Aberto'},inplace=True)

    df['Meta']=df['Meta'].groupby(['ID Vendedor'],as_index=False).agg({'Meta R$':'sum'})

    df['Meta']=df['Meta'].merge(df['Consolidado'],on='ID Vendedor',how='left')

    df['Meta']=df['Meta'].merge(df['Pendente'],on='ID Vendedor',how='left')

    colunas=df['Meta'].columns[1:]

    for coluna in colunas:
        
        df['Meta'].loc[df['Meta'][coluna].isnull(),coluna]=0    
        
        pass

    df['Meta']['Realizado R$']=round(df['Meta']['Faturado']+df['Meta']['Em Aberto'],2)

    df['Meta']['Dif']=round(df['Meta']['Realizado R$']-df['Meta']['Meta R$'],2)

    df['Meta']['Perc']=round(df['Meta']['Realizado R$']/df['Meta']['Meta R$'],4)*100

    util=df['Calendario']['Útil'].max()

    trabalhado=df['Calendario']['Trabalhado'].max()

    df['Meta']['Projeção']=round((df['Meta']['Realizado R$']/trabalhado)*util,2)

    df['Meta']['Perc Projeção']=round(df['Meta']['Projeção']/df['Meta']['Meta R$'],4)*100

    colunas=df['Meta'].columns[1:]

    for coluna in colunas:
        
        df['Meta'].loc[df['Meta'][coluna].isnull(),coluna]=0    
        
        pass

    df['Vendedor']=df['Vendedor'].merge(df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe','DDD',
        'Telefone']]

    df['Vendedor']=df['Vendedor'].merge(df['Meta'],on='ID Vendedor',how='inner')

    if(len(df['Vendedor'])>0 and datetime.now().isoweekday() in [1,2,3,4,5]):

        codigos=df['Vendedor']['ID Vendedor'].tolist()

        temp_df=pd.DataFrame()

        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        for c in codigos:

            temp_df=df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==c]

            meta=Moeda.FormatarMoeda(temp_df['Meta R$'].sum())

            total=Moeda.FormatarMoeda(temp_df['Realizado R$'].sum())

            diferenca=Moeda.FormatarMoeda(temp_df['Dif'].sum())

            projecao=Moeda.FormatarMoeda(temp_df['Projeção'].sum())

            perc=Moeda.FormatarMoeda(temp_df['Perc'].sum())

            nome=str(temp_df['Nome Resumido'].tolist()[-1]).title()

            ddd=temp_df['DDD'].tolist()[-1]

            telefone=temp_df['Telefone'].tolist()[-1]

            path=''

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            mensagem=f"""
            
            {msg};

            {nome} tudo bem, você realizou R$ {total} atingindo {perc}% comparando com a meta de R$ {meta} falta realizar R$ {diferenca}. A projeção para este mês é de R$ {projecao}.
            
            """ if (temp_df['Perc'].sum())<100 else f"""
            
            {msg};

            {nome} tudo bem, venho te parabenizar você realizou R$ {total} atingindo {perc}% comparando com a meta de R$ {meta} com isso atingindo a sua meta.            
            
            """

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,path]

            pass

        whatsapp_df.to_excel('whatsapp.xlsx',index=False,encoding='UTF-8')

        pass

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass