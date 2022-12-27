from datetime import date, datetime,timedelta
import pandas as pd


class Calendario:

    def CriarCalendario(self,ano,mes,dia,hora,minuto,segundo):

        datas=[]

        for i in range(0,365):

            dt_calend=datetime(year=ano,month=mes,day=dia,hour=hora,minute=minuto,second=segundo)+timedelta(days=i)
            
            datas.append(dt_calend)

            pass

        df=pd.DataFrame(data=datas,columns=['Datas'])

        return df

        pass

    def Segundos(self,dias,opc):

        tipo={'Dia':(60*60)*24,'Hora':60*60,'Minuto':60,'Segundo':1}

        valor=tipo[opc]

        return valor*dias

        pass


    def DataAtual(self):

        ano=datetime.now().year

        mes=datetime.now().month

        dia=datetime.now().day

        hora=datetime.now().hour

        minuto=datetime.now().minute

        segundo=datetime.now().second

        return datetime(year=ano,month=mes,day=dia,hour=hora,minute=minuto,second=segundo)

        pass

    def DataAgenda(self):

        ano=datetime.now().year

        mes=datetime.now().month

        info={'Dia':0,'Hora':0,'Minuto':0,'Segundo':0}

        for c in info.keys():

            res=''

            while not res.isnumeric():

                res=input(f'Informe {c}: ')

                if(res.isnumeric()):

                    res=int(res)

                    info[c]=res

                    break

                pass

            pass

        return datetime(year=ano,month=mes,day=info['Dia'],hour=info['Hora'],minute=info['Minuto'],second=info['Segundo'])

        pass

    def ProxData(self,data,valor):

        data=data+timedelta(seconds=valor)

        return data

        pass

    def MesDate(self,data):

        df=self.CriarCalendario(data.year,data.month,data.day,data.hour,data.minute,data.second)

        mes=1 if (data.month+1)==13 else data.month+1

        ano=(data.year+1) if (data.month+1)==13 else data.year
        
        data=df['Datas'].loc[(df['Datas'].dt.year==ano)&(df['Datas'].dt.month==mes)&(df['Datas'].dt.day==data.day)].max()

        return data

        pass


    def Tempo(self):

        opc=['Dia','Hora','Minuto','Segundo']

        temp_dict=dict()

        for i,v in enumerate(opc):

            i+=1
            
            print(f'{i}) {v}')

            temp_dict[i]=v

            pass
        
        resp=''

        print('-'*50)

        while not resp in temp_dict.keys():

            resp=input('Escolha uma das opções acima: ')

            if(resp.isnumeric()):

                resp=int(resp)

                if(resp in temp_dict.keys()):

                    break

                    pass

                pass

            pass

        val=''

        while not val.isnumeric():

            val=input('Informe um valor inteiro: ')

            if(val.isnumeric()):

                val=int(val)

                break

            pass

        segundo=self.Segundos(dias=val,opc=temp_dict[resp])

        return segundo

        pass

    def DateStrTime(self,data: str):

        return datetime.strptime(data,'%Y-%m-%d %H:%M:%S')

        pass

    def ProximaData(self,data: datetime, tipo: bool,valor: int):

        data+=timedelta(seconds=valor) if tipo==False else timedelta(days=valor)

        return data

        pass    

    pass