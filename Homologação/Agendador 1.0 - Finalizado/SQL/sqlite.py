import sqlite3
import pandas as pd

class SQL:

    def __init__(self,database) -> None:

        self.database=database

        pass

    def Conexao(self):

        try:

            conecta=sqlite3.connect(self.database)

            return conecta

            pass


        except:

            print('Sem conexão com a base de dados')

            pass


        pass


    def Salvar(self,query):

        conecta=self.Conexao()

        cursor=conecta.cursor()

        cursor.execute(query)

        conecta.commit()
        
        pass


    def Read(self,query):

        conecta=self.Conexao()

        cursor=conecta.cursor()

        cursor.execute(query)

        return cursor.fetchall()

        pass


    def Codigo(self,query):

        conecta=self.Conexao()

        cursor=conecta.cursor()

        cursor.execute(query)
        
        codigo=[l for l in cursor.fetchone()]

        return codigo[-1]

        pass


    def CriarTabela(self,*querys):

        conecta=self.Conexao()

        for query in querys[-1]:

            self.Salvar(query)

            pass

        pass

    def GetDados(self,query):

        conecta=self.Conexao()

        df=pd.read_sql(query,conecta)

        return df

        pass

    pass