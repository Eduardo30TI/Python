from Query import Query
import pandas as pd
from Tempo import DataHora
import os
from glob import glob
from Email import Email
from Moeda import Moeda

sql=Query('Netfeira','sqlserver','MOINHO','192.168.0.252')

data=DataHora()

def Base(tabelas_df,ano,mes):
    
    tabelas_df['SELL IN']=tabelas_df['SELL IN'].loc[(~tabelas_df['SELL IN']['Tipo de Entrada'].isnull())&(tabelas_df['SELL IN']['Tipo de Entrada'].str.contains('BONIFI'))|(tabelas_df['SELL IN']['Tipo de Entrada'].str.contains('PADRAO'))]

    consolidado_df=tabelas_df['SELL IN'][['Fornecedor','NFe','Data de Emissão', 'Data de Recebimento','Total NFe']].loc[(tabelas_df['SELL IN']['Data de Recebimento'].dt.year==ano)&(tabelas_df['SELL IN']['Data de Recebimento'].dt.month==mes)].groupby(['Fornecedor','NFe','Data de Emissão', 'Data de Recebimento'],as_index=False).agg({'Total NFe':'sum'})

    return consolidado_df

    pass

def Analise(tabelas):

    data_atual=data.HoraAtual()

    ano=data_atual.year

    hora=data_atual.hour

    mes=data_atual.month

    dia=data_atual.day

    if(dia==1):

        mes-=1

        if(mes<=0):

            mes=12

            ano-=1

            pass

        pass

    if(dia==15 or dia==1):
    
        consolidado_df=Base(tabelas,ano,mes)

        nfe=len(consolidado_df['NFe'].unique().tolist())

        total=consolidado_df['Total NFe'].sum()

        total=Moeda.FormatarMoeda(total)

        if(hora<=11):

            msg='Bom dia'

            pass

        else:

            msg='Boa tarde'

            pass

        nome='Bruna'

        mensagem=f"""
        
        <p>{msg};</p>

        <p>{str(nome).title()}</p>

        <p>Tudo bem, estou encaminhando uma relação com {nfe} nota(s) e a soma das notas é de R$ {total}</p>

        <P>Por favor não responder mensagem automática</P>

        <p>Atenciosamente</p>

        <p>BOT TI</p>
            
        """

        consolidado_df.to_excel('Consolidado.xlsx',index=False,encoding='ISO-8859-1')

        email_to=['fiscal.nfe@demarchibrasil.com.br']

        email_cc=['EDSON.JUNIOR@DEMARCHIBRASIL.COM.BR','COMPRAS@DEMARCHIBRASIL.COM.BR']
        
        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        anexo=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

        assunto=f'Notas de {data.Mes(mes).title()} de {ano}'

        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

        RemoverArquivo('.xlsx')

        pass

    pass

def RemoverArquivo(filtro):

    filtro=(f'*{filtro}')

    temp_path=os.path.join(os.getcwd(),filtro)

    dados=glob(temp_path)

    for arq in dados:
        
        os.remove(arq)

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela()

    Analise(tabelas)

    pass