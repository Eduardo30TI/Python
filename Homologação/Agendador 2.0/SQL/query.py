import sqlite3
import pandas as pd

class SQL:

    def __init__(self,database):

        self.database=database

        pass

    def Conexao(self):

        try:

            conecta=sqlite3.connect(self.database)

            return conecta

            pass

        except:

            print('Sem conexão com o banco de dados!')

            pass

        pass


    def Salve(self,query: str):

        conecta=self.Conexao()

        cursor=conecta.cursor()

        cursor.execute(query)

        conecta.commit()

        pass


    def GetDados(self,querys: dict):

        conecta=self.Conexao()

        temp_dict=dict()

        for tabela,query in querys.items():

            temp_dict[tabela]=pd.read_sql(query,conecta)

            pass

        return temp_dict

        pass


    def Codigo(self,query: str):

        conecta=self.Conexao()

        cursor=conecta.cursor()

        cursor.execute(query)

        codigo=[l for l in cursor.fetchone()]

        return codigo[-1]  

        pass


    def CreateTable(self,querys: list):

        for query in querys:

            self.Salve(query)

            pass

        pass


    pass