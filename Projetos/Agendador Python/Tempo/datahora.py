from datetime import datetime,timedelta
import pandas as pd
from Interface import Interface

gui=Interface()

class DataHora:

    def __init__(self):

        self.ano=datetime.now().year

        self.mes=datetime.now().month

        self.dia=datetime.now().day

        self.hora=datetime.now().hour

        self.minuto=datetime.now().minute

        self.segundo=datetime.now().second

        pass

    
    def TempoAtual(self):

        data=datetime(year=self.ano,month=self.mes,day=self.dia,hour=self.hora,minute=self.minuto,second=self.segundo)

        return data

        pass


    def TempoAgendado(self,hora,minuto,segundo):

        data=datetime(year=self.ano,month=self.mes,day=self.dia,hour=hora,minute=minuto,second=segundo)

        return data

        pass

    def ProximoAgenda(self,tempo,segundo):

        data=tempo+timedelta(seconds=segundo)

        return data

        pass

    def DiaSemana(self,data):

        indice=data.weekday()

        return indice

        pass

    def OpcoesTempo(self):

        tipo={1:'dia',2:'hora',3:'minuto',4:'segundo'}

        resp=gui.Menu(kwargs=tipo)

        tempo={'dia':(3600*24),'hora':(3600),'minuto':(60),'segundo':1}

        num=''

        while not num.isnumeric():

            num=input('Informe um número inteiro: ')

            if(num.isnumeric()):

                num=int(num)

                break

            pass        

        segundo=num*tempo[resp]

        return segundo

        pass
    

    pass
