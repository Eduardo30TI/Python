import pyodbc

class SQL:

    def __init__(self,usuario,senha,database,server):

        self.usuario=usuario

        self.senha=senha

        self.driver='{SQL Server}'

        self.database=database

        self.server=server

        pass

    def ConexaoSQL(self):

        try:

            str_conexao=(f'Driver={self.driver};Server={self.server};Databas={self.database};UID={self.usuario};PWD={self.senha}')

            conecta=pyodbc.connect(str_conexao)

            return conecta

            pass

        except:

            print('Sem conexão com a base de dados!')

            pass

        pass

    pass