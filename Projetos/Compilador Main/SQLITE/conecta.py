import sqlite3


class SQLConexao:

    def __init__(self,database):

        self.database=database

        pass


    def Conexao(self):

        try:

            conectando=sqlite3.connect(self.database)

            return conectando

            pass


        except:

            print('Sem conexão com o banco de dados')

            pass

        pass

    def Salvar(self,conectando,query):

        try:

            cursor=conectando.cursor()

            cursor.execute(query)

            conectando.commit()
            
            pass


        except Exception as erro:

            print('Erro: {}'.format(erro))

            pass

        pass


    def Codigo(self,conectando,query):

        try:

            cursor=conectando.cursor()

            cursor.execute(query)

            codigo=cursor.fetchone()

            for c in codigo:
                
                codigo=c

                break
            
            return codigo

            pass


        except Exception as erro:

            print('Erro: {}'.format(erro))

            pass

        pass

    def Dados(self,conectando,query):

        try:

            cursor=conectando.cursor()

            cursor.execute(query)

            info=cursor.fetchall()

            return info

            pass


        except Exception as erro:

            print('Erro: {}'.format(erro))

            pass        

        pass


    pass