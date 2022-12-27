from ConectionSQL import SQL
import pandas as pd

pd.set_option('float.format','{:.2f}'.format)

querys={
    
    'Faltas':"""
    
    SELECT * FROM netfeira.vw_falta
    WHERE [Data de Falta]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)    
    
    """,
    
    'Vendedores':"""
    
    SELECT * FROM netfeira.vw_vendedor
    
    
    """,
    
    'Supervisor':"""
    
    SELECT * FROM netfeira.vw_supervisor
    
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