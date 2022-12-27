from datetime import datetime,timedelta
import pandas as pd


class Calendario:

    def DataAtual(self):

        temp_dict=dict()

        temp_dict['Ano']=datetime.now().year

        temp_dict['Mês']=datetime.now().month

        temp_dict['Dia']=datetime.now().day

        temp_dict['Hora']=datetime.now().hour

        temp_dict['Minuto']=datetime.now().minute

        temp_dict['Segundo']=datetime.now().second

        return datetime(year=temp_dict['Ano'],month=temp_dict['Mês'],day=temp_dict['Dia'],hour=temp_dict['Hora'],minute=temp_dict['Minuto'],second=temp_dict['Segundo'])

        pass

    def DataAgendada(self):

        temp={'s':True,'n':False}

        while True:

            resp=input('Deseja escolher o dia?[s/n]: ').lower()

            if(resp in temp.keys()):

                break

            pass

        resp=temp[resp]

        temp_dict=dict()

        opc=['Hora','Minuto','Segundo'] if resp==False else ['Dia','Hora','Minuto','Segundo']

        temp_dict['Ano']=datetime.now().year

        temp_dict['Mês']=datetime.now().month

        if(not resp):

            temp_dict['Dia']=datetime.now().day

            pass
        
        for op in opc:

            num=''

            while not num.isnumeric():

                num=input(f'{op}: ')

                if(num.isnumeric()):

                    num=int(num)

                    temp_dict[op]=num

                    break

                    pass

                pass

            pass

        return datetime(year=temp_dict['Ano'],month=temp_dict['Mês'],day=temp_dict['Dia'],hour=temp_dict['Hora'],minute=temp_dict['Minuto'],second=temp_dict['Segundo'])

        pass

    def DataMensal(self,data: datetime):

        temp=[]

        for i in range(0,366):

            dt_prox=data+timedelta(days=i)

            temp.append(dt_prox)

            pass

        df=pd.DataFrame(data=temp,columns=['Data'])

        mes=data.month+1
        
        ano=data.year if mes<=12 else data.year+1

        mes=mes if mes<=12 else 1

        dia=data.day

        dt_prox=df['Data'].loc[(df['Data'].dt.year==ano)&(df['Data'].dt.month==mes)&(df['Data'].dt.day==dia)].tolist()

        return dt_prox[-1]

        pass

    def DateStrTime(self,data: str):

        return datetime.strptime(data,'%Y-%m-%d %H:%M:%S')

        pass

    def GetSegundo(self):

        opc={'Dia':(60*60)*24,'Hora':60*60,'Minuto':60,'Segundo':1}

        temp_dict=dict()

        for i,op in enumerate(opc.keys()):
            
            i+=1

            print(f'{i}) {op}')

            temp_dict[i]=op

            pass
        
        while True:

            resp=input('Escolha uma das opções: ')
            
            if(resp.isnumeric()):

                resp=int(resp)

                if(resp in temp_dict.keys()):

                    break

                pass

            pass
        
        while True:

            val=input('Informe um valor inteiro: ')

            if(val.isnumeric()):

                val=int(val)

                break

                pass

            pass

        num=opc[temp_dict[resp]]
        
        val*=num

        return val
        
        pass

    def ProximaData(self,data: datetime, tipo: bool,valor: int):

        data+=timedelta(seconds=valor) if tipo==False else timedelta(days=valor)

        return data

        pass

    pass