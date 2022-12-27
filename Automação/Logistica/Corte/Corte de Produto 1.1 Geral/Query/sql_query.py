from ConectionSQL import SQL
import pandas as pd

pd.set_option('float.format','{:.2f}'.format)

querys={
    
    'Faltas':"""
    
    IF MONTH(GETDATE())=1

        SELECT * FROM netfeira.vw_falta
        WHERE YEAR([Data de Falta])=(YEAR(GETDATE())-1) AND MONTH([Data de Falta])=12

    ELSE

        SELECT * FROM netfeira.vw_falta
        WHERE YEAR([Data de Falta])=YEAR(GETDATE()) AND MONTH([Data de Falta])=(MONTH(GETDATE())-1)

    
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