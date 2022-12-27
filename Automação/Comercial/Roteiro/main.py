from Acesso import Login
from Query import Query
from RemoverArquivo import Remover
from Moeda import Moeda
from Tempo import DataHora
from glob import glob
import os
import pandas as pd

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={

    'Roteiro':

    """

    SELECT * FROM netfeira.vw_roteira_visita
    WHERE Categoria='CLT'
    
    """,

    'Calendario':

    """
    
    DECLARE @DTInicial AS DATETIME,@DTFinal AS DATETIME

    SET @DTInicial='2018-01-01'
    SET @DTFinal= CONCAT(YEAR(GETDATE())+1,'-01-','01')

    ;WITH Calendario (Datas) AS(

    SELECT @DTInicial
    UNION ALL
    SELECT Datas+1
    FROM Calendario WHERE  Datas+1<@DTFinal
    )

    SELECT CONVERT(DATETIME,CAST(Datas AS DATE),101) AS 'Data',YEAR(Datas) AS 'Ano',MONTH(Datas) AS 'Cód. Mês',
    CHOOSE(MONTH(Datas),'JANEIRO','FEVEREIRO','MARÇO','ABRIL','MAIO','JUNHO','JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO') AS 'Mês',
    CHOOSE(MONTH(Datas),'JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ') AS 'Mês Resumido',
    DAY(Datas) AS 'Dia',CONVERT(VARCHAR(7),Datas,120) AS 'Mês Meta',
    DATEPART(DW,Datas) AS 'Cód. Semana',CHOOSE(DATEPART(DW,Datas),'DOM','SEG','TER','QUAR','QUI','SEX','SÁB') AS 'Semana',
    CASE WHEN DATEPART(DW,Datas) IN (7,1) THEN 0 ELSE 1 END AS 'Dias Úteis',
    CASE WHEN MONTH(Datas)<=3 THEN '1º TRIM' WHEN MONTH(Datas)<=6 THEN '2º TRIM' WHEN MONTH(Datas)<=9 THEN '3º TRIM' WHEN MONTH(Datas)<=12 THEN '4º TRIM' END AS 'Trimestre Ano',
    CASE WHEN MONTH(Datas)<=6 THEN '1º SEM' ELSE '2º SEM' END AS 'Semestre Ano',DATEPART(WEEK,Datas) AS 'Semana Ano',
    CONVERT(VARCHAR,DAY(Datas))+'/'+CONVERT(VARCHAR,MONTH(Datas)) AS 'Mês Base'
    FROM Calendario OPTION(MAXRECURSION 10000)    
        
    """

}


def Main(tabela_df):

    data_atual=data.HoraAtual()

    data_atual    

    tabela_df['Calendario']=tabela_df['Calendario'].merge(tabela_df['Roteiro'],left_on='Cód. Semana',right_on='ID Semana',how='inner')[['Data', 'Ano', 'Cód. Mês', 'Mês', 'Mês Resumido', 'Dia','Roteiro Semana', 'Seq', 'ID Cliente', 'Razão Social',
        'Nome Fantasia', 'Status do Cliente', 'Segmento', 'Canal', 'Matriz',
        'Endereço', 'Bairro', 'Cidade', 'UF', 'Numero', 'DDD', 'Contato',
        'ID Vendedor', 'Nome', 'Nome Resumido', 'Equipe', 'E-mail', 'Categoria',
        'Supervisor', 'Email Sup', 'Gerente', 'Email Gerente']]

    tabela_df['Calendario']=tabela_df['Calendario'].loc[(tabela_df['Calendario']['Data'].dt.year==data_atual.year)&(tabela_df['Calendario']['Data'].dt.month==data_atual.month)&(tabela_df['Calendario']['Data'].dt.day==data_atual.day)]

    return tabela_df['Calendario']

    pass


def Enviar(tabela_df):

    roteiro_df=Main(tabela_df)

    colunas=[l for l in roteiro_df.columns.tolist() if str(l).find('mail')>0]

    for col in colunas:

        emails=[l for l in roteiro_df[col].unique().tolist() if l!='']

        

        pass

    pass

if __name__=='__main__':

    tabela_df=sql.CriarTabela(kwargs=querys)

    Enviar(tabela_df)

    pass