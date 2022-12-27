from ConectionSQL import SQL
import pandas as pd

querys={
    
    'Carteira':
    
    """
    
    SELECT * FROM netfeira.vw_carteira
    
    """,
    
    'Venda':"""
    

    SELECT * FROM netfeira.vw_estatico
    
    
    """,
    
    'Supervisor':"""
    
    
    SELECT * FROM netfeira.vw_supervisor
    
    
    """,
    
    'Vendedor':"""
    
    SELECT * FROM netfeira.vw_vendedor
    
    
    """,
    
    'Calendario':"""
    
    
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
    
    
    """,
    
    'Feriado':"""
        
    DECLARE @DateInicial AS DATETIME,@DateFinal AS DATETIME

    SET @DateInicial='2018-01-01'
    SET @DateFinal=CONCAT(YEAR(GETDATE())+1,'-01-01')

    ;WITH TabDatas(dt_calend) AS (
    SELECT @DateInicial
    UNION ALL
    SELECT dt_calend+1 FROM TabDatas WHERE dt_calend+1<@DateFinal),

    TabCalendario (dt_calend,mes_base) AS(

    SELECT CONVERT(DATETIME,CAST(dt_calend AS DATE),101),CONVERT(VARCHAR,DAY(dt_calend))+'/'+CONVERT(VARCHAR,MONTH(dt_calend)) AS mes_base
    FROM TabDatas 
    ),

    TabFeriado (dt_calend,mes_base,dias_feriado) AS (

    SELECT dt_calend,mes_base,
    CASE WHEN mes_base IN ('1/1','10/4','21/4','1/5','11/6','7/9','12/10','2/11','15/11','25/12','8/4') THEN 0 ELSE 1 END 
    FROM TabCalendario)

    SELECT DISTINCT mes_base AS 'Mês Base'
    FROM TabFeriado
    WHERE dias_feriado=0
    ORDER BY 1
    OPTION(MAXRECURSION 10000)    
    
    """,
    
    'Segmento':"""
    
    SELECT * FROM netfeira.vw_segmento
            
    """,
    
    'Meta':"""
    
    SET NOCOUNT ON;

    Declare @Coluna_Pivot AS NVARCHAR(MAX),@Comando AS NVARCHAR(MAX)

    SET @Coluna_Pivot=STUFF((SELECT DISTINCT ', ' + cd_tp_prev FROM prev_vda FOR XML PATH('')),1,1,'')

    SET @Comando='
    SELECT * FROM (
    SELECT DISTINCT mes_ref,CONVERT(VARCHAR(7),mes_ref,120) mes_meta,
    cd_tp_prev,it_prev_vda.cd_vend,
    valor
    FROM prev_vda
    INNER JOIN it_prev_vda ON prev_vda.cd_prev_vda=it_prev_vda.cd_prev_vda AND prev_vda.cd_tp_prev=it_prev_vda.cd_tp_prev_det
    )linha
    PIVOT(SUM(valor) FOR cd_tp_prev IN ('+@Coluna_Pivot+'))coluna
    '

    EXECUTE(@Comando)  
    
    
    """
    
}

class Query(SQL):

    def __init__(self, usuario, senha, database, server):
        super().__init__(usuario, senha, database, server)

        sql=SQL(usuario,senha,database,server)

        self.conectando=sql.ConexaoSQL()

        pass
    
    def CriarTabela(self):

        tabela_dict=dict()

        for tabela,query in querys.items():

            tabela_dict[tabela]=pd.read_sql(query,self.conectando)

            pass

        return tabela_dict

        pass

    pass