from ConectionSQL import SQL
import pandas as pd

querys={
    
    'Pagar':"""
    
    SELECT * FROM netfeira.vw_contapagar
    
    """,

    'Receber':"""
    
    SELECT * FROM netfeira.vw_contareceber
    
    """,
    
    'Estatico':"""
    
    SELECT * FROM netfeira.vw_venda_estatico
    WHERE YEAR([Data de Faturamento])=YEAR(GETDATE())
    
    """,
    
    'Aberto':"""
    
    SELECT * FROM netfeira.vw_aberto
    
    """,
    'Estatistico':

    """
    
    SELECT ROUND(SUM([Total Geral]),2) AS 'Total',SUM([Custo CUE]) AS 'Custo',
    (ROUND(SUM([Total Geral]),2)-SUM([Custo CUE])) AS 'MG Bruta',ROUND(
    ((ROUND(SUM([Total Geral]),2)-SUM([Custo CUE])))/NULLIF(ROUND(SUM([Total Geral]),2),0),4) AS 'MG %'
    FROM netfeira.vw_estatistico
    WHERE YEAR([Data de Faturamento])=YEAR(GETDATE()) AND MONTH([Data de Faturamento])=MONTH(GETDATE())
    AND [ID Situação]='FA'
    
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