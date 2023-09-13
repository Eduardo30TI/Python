from ConectionSQL import SQL
import pandas as pd

class Query(SQL):

    def __init__(self, usuario, senha, database, server):
        super().__init__(usuario, senha, database, server)

        sql=SQL(usuario,senha,database,server)

        self.conectando=sql.ConexaoSQL()
        
        pass

    def CriarTabela(self,**kwargs):
        
        querys=kwargs['kwargs']

        tabelas_df=dict()

        for tabela,query in querys.items():
            
            tabelas_df[tabela]=pd.read_sql(query,self.conectando)
            
            pass

        return tabelas_df

        pass

    def GetDados(self,querys: dict,tabela: list):

        temp_dict=dict()

        for tab in tabela:

            temp_dict[tab]=pd.read_sql(querys[tab],self.conectando)

            pass

        return temp_dict

        pass

    pass