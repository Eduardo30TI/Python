import sqlite3


class SQL:

    def __init__(self,database):

        self.database=database

        pass

    def Connection(self):

        try:

            conectando=sqlite3.connect(self.database)

            return conectando

            pass


        except Exception as erro:

            print(f'Erro: {erro}')

            pass

        pass


    def Save(self,query,connection):

        try:

            cursor=connection.cursor()

            cursor.execute(query)

            connection.commit()

            pass


        except Exception as erro:

            print(f'Erro: {erro}')

            pass        


        pass


    def Code(self,query,connection):


        try:

            cursor=connection.cursor()

            cursor.execute(query)

            dados=[codigo for codigo in cursor.fetchone()]

            return dados[-1]

            pass


        except Exception as erro:

            print(f'Erro: {erro}')

            pass 


        pass

    pass