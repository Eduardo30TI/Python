from datetime import datetime,timedelta
import pandas as pd

class DataHora:

    def __init__(self):

        self.ano=datetime.now().year

        self.mes=datetime.now().month

        self.dia=datetime.now().day

        pass

    def HoraAgendada(self,hora,minuto,segundo):

        hora_agendada=datetime(year=self.ano,month=self.mes,day=self.dia,hour=hora,minute=minuto,second=segundo)

        return hora_agendada

        pass

    def HoraAtual(self):

        hora=datetime.now().hour

        minuto=datetime.now().minute

        segundo=datetime.now().second

        hora_atual=datetime(year=self.ano,month=self.mes,day=self.dia,hour=hora,minute=minuto,second=segundo)

        return hora_atual

        pass

    def HoraFullTime(self,minuto,segundo):

        hora=datetime.now().hour

        hora_agendada=datetime(year=self.ano,month=self.mes,day=self.dia,hour=hora,minute=minuto,second=segundo)

        hora_full=hora_agendada+timedelta(hours=1)

        return hora_full

        pass

    def ProximaHora(self,data,valor):
      
        prox_data=data+timedelta(seconds=valor)

        return prox_data

        pass

    def FormatarData(self,ano='',mes='',dia=''):

        if(ano!=''):

            self.ano=ano

            self.mes=mes

            self.dia=dia

            pass

        data_atual=f'{self.ano}_{self.mes}_{self.dia}'

        return data_atual

        pass

    def Repetir(self,texto):

        try:

            resp=''

            while resp.isnumeric()==False:

                resp=input(texto)

                if(resp.isnumeric()):

                    resp=int(resp)

                    break

                pass

            return resp

            pass

        except Exception as erro:

            print('Erro: {0}'.format(erro))

            pass

        pass


    def ConverterValor(self,valor,tipo):

        try:

            if(tipo=='hora'):

                valor=valor*3600

                pass

            elif(tipo=='minuto'):

                valor=valor*60

                pass

            elif(tipo=='dia'):

                valor=valor*(3600*24)

                pass
            
            return valor

            pass


        except Exception as erro:

            print('Erro: {0}'.format(erro))

            pass

        pass

    def Calendario(self,ano,mes,dia):

        meses={1:'JANEIRO',2:'FEVEREIRO',3:'MARÇO',4:'ABRIL',5:'MAIO',6:'JUNHO',7:'JULHO',8:'AGOSTO',9:'SETEMBRO',10:'OUTUBRO',11:'NOVEMBRO',12:'DEZEMBRO'}

        semana={1:'DOMINGO',2:'SEGUNDA',3:'TERÇA',4:'QUARTA',5:'QUINTA',6:'SEXTA',7:'SÁBADO'}

        feriados=['1/1','1/5','10/4','11/6','12/10','15/11','2/11','21/4','25/12','7/9','8/4']

        uteis=[7,1]

        datainicio=datetime(year=ano,month=mes,day=dia)

        datafim=datetime(year=(datetime.now().year)+1,month=1,day=1)

        calend_df=pd.DataFrame(pd.date_range(datainicio,datafim),columns=['Datas'])

        data_max=calend_df['Datas'].max()
        
        calend_df=calend_df.loc[calend_df['Datas']<data_max]

        calend_df['Ano']=calend_df['Datas'].dt.year

        calend_df['ID Mês']=calend_df['Datas'].dt.month

        calend_df['Mês']=calend_df['ID Mês'].apply(lambda info: meses[info])

        calend_df['Dia']=calend_df['Datas'].dt.day

        calend_df['Semana Ano']=calend_df['Datas'].dt.week

        calend_df['ID Semana']=calend_df['Datas'].dt.weekday

        calend_df['ID Semana']=calend_df['ID Semana'].apply(lambda info: info+2 if (info+2)<8 else info-5)

        calend_df['Semana']=calend_df['ID Semana'].apply(lambda info: semana[info])

        calend_df['Dia']=calend_df[['Dia']].astype('str')

        calend_df['ID Mês']=calend_df[['ID Mês']].astype('str')

        calend_df['ID Feriado']=calend_df['Dia']+'/'+calend_df['ID Mês']

        calend_df.loc[calend_df['ID Feriado'].isin(feriados),'Dias Úteis']=calend_df['ID Feriado'].loc[calend_df['ID Feriado'].isin(feriados)].apply(lambda info: '0' if info in feriados else '1')

        calend_df.loc[calend_df['Dias Úteis']!='0','Dias Úteis']=calend_df['ID Semana'].loc[calend_df['Dias Úteis']!='0'].apply(lambda info: 0 if info in uteis else 1)

        return calend_df

        pass

    pass