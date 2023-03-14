from datetime import datetime,timedelta
import pandas as pd

class Datas:

    def DataAtual(self):

        return datetime.strptime(datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

        pass

    def DataStr(self,data):

        return datetime.strftime(data,'%Y-%m-%d %H:%M:%S')

        pass

    def DataAgendada(self,hoje=False):

        opc={'Dia':0,'Hora':0,'Minuto':0,'Segundo':0} if hoje==False else {'Hora':0,'Minuto':0,'Segundo':0}

        for op in opc.keys():

            while True:

                num=input(f'Informe um número inteiro para {op.lower()}: ')

                if num.isnumeric():

                    num=int(num)

                    break

                pass

            opc[op]=num

            pass

        return datetime.strptime(datetime.strftime(datetime(year=datetime.now().year,month=datetime.now().month,day=opc['Dia'],hour=opc['Hora'],minute=opc['Minuto'],second=opc['Segundo']),'%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S') if hoje==False else datetime.strptime(datetime.strftime(datetime(year=datetime.now().year,month=datetime.now().month,day=datetime.now().day,hour=opc['Hora'],minute=opc['Minuto'],second=opc['Segundo']),'%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

        pass

    def ConverterData(self,data):

        return datetime.strptime(data,'%Y-%m-%d %H:%M:%S')

        pass


    def Calcular(self,data,tipo,valor=0):
        
        match tipo:

            case 'Mensal':

                calend_df=pd.DataFrame(columns=['Data','Dia'])
                
                for i in range(0,366):

                    dt_prox=data+timedelta(days=int(i))

                    if dt_prox.day!=data.day:

                        continue
                    
                    calend_df.loc[len(calend_df)]=[dt_prox,dt_prox.day]

                    pass

                dt_prox=calend_df.loc[1,'Data']

                return dt_prox

                pass

            case 'Semanal':

                calend_df=pd.DataFrame(columns=['Data','Semana'])

                for i in range(0,7):

                    i+=1

                    dt_prox=data+timedelta(days=int(i))

                    calend_df.loc[len(calend_df)]=[dt_prox,dt_prox.isoweekday()]

                    pass

                dt_prox=calend_df.loc[calend_df['Semana']==valor,'Data'].max()

                return dt_prox

                pass

            case 'Diário':

                dt_prox=data+timedelta(days=int(valor))

                return dt_prox

                pass

            case _:

                dt_prox=data+timedelta(seconds=int(valor))

                return dt_prox

                pass

        pass
    
    def Segundo(self,valor,tipo):

        match tipo:


            case 'Hora':

                res=valor*3600

                return res

                pass

            case 'Minuto':

                res=valor*60

                return res                

                pass

            case _:

                return valor

                pass

        pass


    pass