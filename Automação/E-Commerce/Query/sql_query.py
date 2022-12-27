from ConectionSQL import SQL
import pandas as pd

querys={

    'Estoque':"""
        
    DECLARE @DTATUAL DATETIME

    SET @DTATUAL=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101);

    WITH TabSTK (cd_emp,local,cd_prod,qtde,qtde_pend_pedv,qtde_saldo,dt_ult_movimentacao) AS (

    SELECT estoque.cd_emp,local.descricao AS local,
    cd_prod,qtde,qtde_pend_pedv,(qtde-qtde_pend_pedv) as qtde_saldo,
    CONVERT(DATETIME,CAST(dt_ult_movimentacao AS DATE),101)
    FROM (
    SELECT cd_emp,cd_local,cd_prod,qtde,qtde_pend_pedv,
    dt_ult_movimentacao
    FROM estoque)estoque
    INNER JOIN local ON estoque.cd_local=local.cd_local AND estoque.cd_emp=local.cd_emp AND local.central=1
    INNER JOIN empresa ON estoque.cd_emp=empresa.cd_emp AND empresa.ativo=1),

    TabSTKDia (data,local,cd_emp,cd_prod,qtde,qtde_pend_pedv,qtde_saldo,dt_ultima) AS (

    SELECT estoque.data,local,estoque.cd_emp,estoque.cd_prod,estoque.qtde,estoque.qtde_pend_pedv,
    qtde_saldo,
    (SELECT MAX(est_dia.data) FROM est_dia WHERE estoque.cd_emp=est_dia.cd_emp AND estoque.cd_prod=est_dia.cd_prod
    AND est_dia.data<estoque.data) AS dt_ultima
    FROM (
    SELECT CONVERT(DATETIME,CAST(data AS DATE),101) AS data,local.descricao AS local,
    est_dia.cd_emp,cd_prod,SUM(qtde) AS qtde,SUM(qtde_pend_pedv) AS qtde_pend_pedv,
    SUM(qtde-qtde_pend_pedv) as qtde_saldo
    FROM est_dia
    INNER JOIN local ON est_dia.cd_local=local.cd_local AND est_dia.cd_emp=local.cd_emp AND local.central=1
    INNER JOIN empresa ON est_dia.cd_emp=empresa.cd_emp AND empresa.ativo=1
    --WHERE cd_prod=3
    GROUP BY data,est_dia.cd_emp,cd_prod,local.descricao)estoque),

    TabMovimentacao (data,local,cd_emp,cd_prod,qtde,qtde_pend_pedv,qtde_saldo,dt_ultima,penul_saldo) AS (

    SELECT Tab01.data,Tab01.local,Tab01.cd_emp,Tab01.cd_prod,Tab01.qtde,Tab01.qtde_pend_pedv,
    Tab01.qtde_saldo,Tab01.dt_ultima,Tab02.qtde_saldo AS penul_saldo
    FROM TabSTKDia AS Tab01
    INNER JOIN TabSTKDia AS Tab02 ON Tab01.cd_emp=Tab02.cd_emp AND Tab01.cd_prod=Tab02.cd_prod
    AND Tab01.dt_ultima=Tab02.data
    WHERE Tab01.data=@DTATUAL
    ),

    TabLinha (cd_linha,linha,categoria,secao,departamento) AS (

    SELECT cd_linha,linha.descricao as linha,categprd.descricao as categoria,
    secao.descricao as secao,depto.descricao as departamento
    FROM linha
    INNER JOIN categprd ON linha.cd_categprd=categprd.cd_categprd
    INNER JOIN secao ON linha.cd_secao=secao.cd_secao
    INNER JOIN depto ON secao.cd_depto=depto.cd_depto
    WHERE linha.ativo=1)


    SELECT TabSTK.local AS 'Local de Estoque',
    preco.cd_prod AS 'SKU',produto.descricao AS 'Produto',fabric.descricao AS 'Fabricante',
    TabLinha.departamento AS 'Departamento',TabLinha.secao AS 'Seção',
    TabLinha.categoria AS 'Categoria',TabLinha.linha AS 'Linha',
    TabSTK.qtde_saldo AS 'Saldo Atual',TabSTK.dt_ult_movimentacao AS 'Data da Movimentação',
    TabMovimentacao.penul_saldo AS 'Penúltima Movimentação',
    TabMovimentacao.dt_ultima AS 'Penúltima Data',
    CASE WHEN TabSTK.qtde_saldo<=10 THEN 'INATIVAR'
    WHEN TabSTK.qtde_saldo>10 AND TabMovimentacao.penul_saldo<=10 THEN 'REATIVAR'
    ELSE 'OK' END AS 'Acompanhamento'
    FROM preco
    INNER JOIN tab_pre ON preco.cd_tabela=tab_pre.cd_tabela
    INNER JOIN TabSTK ON preco.cd_prod=TabSTK.cd_prod
    INNER JOIN TabMovimentacao ON preco.cd_prod=TabMovimentacao.cd_prod
    INNER JOIN produto ON preco.cd_prod=produto.cd_prod and produto.ativo=1
    INNER JOIN TabLinha ON produto.cd_linha=TabLinha.cd_linha
    INNER JOIN fabric ON produto.cd_fabric=fabric.cd_fabric
    WHERE tab_pre.descricao LIKE '%CONSUMIDOR%' AND vl_preco>0
    
    """
    
}


class Query(SQL):

    def __init__(self, usuario, senha, database, server):
        super().__init__(usuario, senha, database, server)

        sql=SQL(usuario,senha,database,server)

        self.conectando=sql.ConexaoSQL()
        
        pass

    def CriarTabela(self):
        
        tabelas_df=dict()

        for tabela,query in querys.items():
            
            tabelas_df[tabela]=pd.read_sql(query,self.conectando)
            
            pass

        return tabelas_df

        pass

    pass