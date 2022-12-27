from ConectionSQL import SQL
import pandas as pd

querys={

'Romaneio':"""

IF MONTH(GETDATE())=1

SELECT * FROM netfeira.vw_romaneio
WHERE YEAR([Data da Montagem])=YEAR(GETDATE())-1 AND MONTH([Data da Montagem])=12

ELSE

SELECT * FROM netfeira.vw_romaneio
WHERE YEAR([Data da Montagem])=YEAR(GETDATE()) AND MONTH([Data da Montagem])=(MONTH(GETDATE())-1)

""",
    
'Cliente':
    
"""

SELECT * FROM netfeira.vw_cliente


""",
    
'Vendedor':"""

SELECT * FROM netfeira.vw_vendedor


""",
    
'Supervisor':"""


SELECT * FROM netfeira.vw_supervisor


""",
    
'Frete':"""


SELECT * FROM netfeira.vw_frete


""",
    
'Produto':"""


WITH TabCaixa (cd_prod,qtde_caixa) AS (

SELECT produto.cd_prod,
CASE WHEN unid_prod.qtde_unid IS NULL THEN 0 ELSE unid_prod.qtde_unid END AS qtde_caixa
FROM produto
LEFT JOIN unid_prod ON produto.cd_prod=unid_prod.cd_prod AND unid_prod.unid_vda='CX')

SELECT produto.cd_prod AS 'SKU',produto.cd_prod_fabric AS 'Cód. Fabricante',produto.descricao AS 'Produto',
CASE WHEN produto.ativo=1 THEN 'ATIVO' ELSE 'INATIVO' END 'Status',fabric.descricao AS 'Fabricante',
depto.descricao AS 'Departamento',secao.descricao AS 'Seção',categprd.descricao AS 'Categoria',linha.descricao AS 'Linha'
FROM produto
INNER JOIN fabric ON produto.cd_fabric=fabric.cd_fabric
INNER JOIN linha ON produto.cd_linha=dbo.linha.cd_linha 
INNER JOIN categprd ON linha.cd_categprd=dbo.categprd.cd_categprd
INNER JOIN secao ON linha.cd_secao=dbo.secao.cd_secao 
INNER JOIN depto ON secao.cd_depto=dbo.depto.cd_depto
INNER JOIN TabCaixa ON produto.cd_prod=TabCaixa.cd_prod


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