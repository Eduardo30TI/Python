from Acesso import Login
from Query import Query
from Email import Email
from Moeda import Moeda
from RemoverArquivo import Remover
from Tempo import DataHora
import pandas as pd
from datetime import datetime,timedelta
import os
from glob import glob

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Separação':
    
    """
       
    SELECT * FROM netfeira.vw_mov_saida m
    WHERE m.[Data de Movimentação]=DATEADD(DAY,-1,CONVERT(DATETIME,CAST(GETDATE() AS date),101))
    ORDER BY SKU
    
    """
}

data=DataHora()

def Main(df):

    if(len(df['Separação'])>0):

        dt_atu=data.HoraAtual()

        msg='Bom dia' if dt_atu.hour<12 else 'Boa tarde'

        nome='Edson Almeida'

        assunto='Relatório de Separação'

        email_to=['edson.junior@demarchibrasil.com.br']

        email_cc=['']

        mensagem=f"""
        
        <p>{msg};</p>

        <p>{str(nome).title()}</p>

        <p>Segue a relação do que foi vendido no dia {datetime.strftime(dt_atu-timedelta(days=1),'%d/%m/%Y')}.</p>

        <P>Por favor não responder mensagem automática</P>

        <p>Atenciosamente</p>

        <p>BOT TI</p>  
        
        """

        df['Separação'].to_excel('Relatório de Separação.xlsx',index=False,encoding='UTF-8')

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        anexo=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

        Remover.RemoverArquivo('.xlsx')

        pass

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)


    pass