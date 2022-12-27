from .sqlite import SQL
import pandas as pd



class Query(SQL):

    def __init__(self, database):
        super().__init__(database)

        self.sql=SQL(database)

        self.conectando=self.sql.Connection()

        pass

    def CreateTable(self,*query):

        try:

            for tab in query[0]:

                self.sql.Save(tab,self.conectando)

                pass

            print('Tabela criada com sucesso!')

            pass


        except Exception as erro:

            print(f'Erro: {erro}')

            pass

        pass

    def DataBase(self,**querys):

        try:

            tabela_df=dict()

            for tabela,query in querys['querys'].items():

                tabela_df[tabela]=pd.read_sql(query,self.conectando)

                pass

            return tabela_df

            pass


        except Exception as erro:

            print(f'Erro: {erro}')

            pass        

        pass

    pass