import sqlite3 as sql
import pandas as pd


class SQL:

    def __init__(self,database):

        self.database=database

        pass

    def Conexao(self):

        try:

            return sql.connect(self.database)

            pass

        except Exception as erro:

            print(erro)

            pass

        pass


    def Salvar(self,query):

        conecta=self.Conexao()

        cursor=conecta.cursor()

        cursor.execute(query)

        conecta.commit()

        pass


    def Validar(self,query):

        conecta=self.Conexao()

        cursor=conecta.cursor()

        cursor.execute(query)

        res=[i for i in cursor.fetchone()]

        return res[-1]

        pass

    def CriarTabela(self,**kwargs):

        for query in kwargs['kwargs'].values():

            self.Salvar(query)

            pass

        pass


    def GetDados(self,**kwargs):

        temp_df=dict()

        conecta=self.Conexao()

        for tabela,query in kwargs['kwargs'].items():

            temp_df[tabela]=pd.read_sql(query,conecta)

            pass

        return temp_df

        pass

    def Excel(self,caminho):

        df=pd.read_excel(caminho)

        return df

        pass

    pass