from ConectionSQL import SQL
import pandas as pd

querys={
    
    
    'Carteira':"""
    
    SELECT * FROM netfeira.vw_carteira
    WHERE Dias IS NOT NULL
    
    
    """,
    
    
    'Vendedor':"""
    
    
    SELECT * FROM netfeira.vw_vendedor
    

    """,
    
    
    'Supervisor':"""
        
    SELECT * FROM netfeira.vw_supervisor
    
    """,

    'Cliente':

    """
    
    SELECT cd_clien AS 'ID Cliente',cd_vend AS 'Principal'
    FROM cliente
    
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