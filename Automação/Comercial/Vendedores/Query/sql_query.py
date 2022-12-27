from ConectionSQL import SQL
import pandas as pd

querys={
    
    'Vendedor':
    
    """
    
    SELECT * FROM netfeira.vw_vendedor
    WHERE [Status do Vendedor]='ATIVO'
    
    """,
    
    'Supervisor':
    
    """
    
    SELECT * FROM netfeira.vw_supervisor
    
    """,
    
    'Carteira':
    
    """
    
    SELECT cd_clien AS 'ID Cliente',cd_vend AS 'ID Vendedor' FROM vend_cli
    
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