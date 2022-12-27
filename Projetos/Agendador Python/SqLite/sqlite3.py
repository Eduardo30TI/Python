import sqlite3

class SQL:

    def __init__(self,banco):

        self.banco=banco

        pass


    def Conexao(self):

        try:

            conectando=sqlite3.connect(self.banco)

            return conectando

            pass


        except Exception as erro:

            print('Erro: {0}'.format(erro))

            pass

        pass


    def Salvar(self,query,connection):

        try:

            cursor=connection.cursor()

            cursor.execute(query)

            connection.commit()

            pass


        except Exception as erro:

            print(f'Erro: {erro}')

            pass

        pass


    def GetCodigo(self,query,connection):

        try:

            cursor=connection.cursor()

            cursor.execute(query)

            dados=cursor.fetchone()

            for d in dados:

                codigo=d

                pass


            return codigo

            pass


        except Exception as erro:

            print(f'Erro: {erro}')

            pass

        pass

    def GetDados(self,query,connection):

        try:

            cursor=connection.cursor()

            cursor.execute(query)

            dados=cursor.fetchall()

            return dados

            pass


        except Exception as erro:

            print(f'Erro: {erro}')

            pass

        pass

    pass