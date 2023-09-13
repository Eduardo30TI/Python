import sqlite3
import pandas as pd

class SQL:

    def __init__(self):

        self.database='MOINHO.db'

        pass


    def Connect(self):

        try:

            connecting=sqlite3.connect(self.database)

            return connecting

            pass

        except Exception as erro:

            print(erro)

            pass

        pass

    def Save(self,query: str):

        with self.Connect() as connecting:

            cursor=connecting.cursor()
            cursor.execute(query)

            connecting.commit()

            pass

        pass

    def Code(self,query: str):

        with self.Connect() as connecting:
        
            cursor=connecting.cursor()
            cursor.execute(query)

            id=[l for l in cursor.fetchone()]

            pass

        return id[-1]

        pass

    def GetDataframe(self,query: str):

        with self.Connect() as connecting:

            df=pd.read_sql(query,connecting)

            pass

        return df

        pass

    def GetDados(self,querys: dict):

        temp_dict=dict()

        with self.Connect() as connecting:

            for tab,query in querys.items():

                temp_dict[tab]=pd.read_sql(query,connecting)

                pass

            pass

        return temp_dict

        pass


    def CreateTable(self,querys: list):

        with self.Connect() as connecting:

            for query in querys:

                self.Save(query)

                pass

            pass

        pass


    pass