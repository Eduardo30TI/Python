from Acesso import Login
from Query import Query
import pandas as pd
import os
from glob import glob
from datetime import datetime
from Moeda import Moeda
import urllib

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Cliente':

    """

    SELECT c.[ID Cliente],c.[Nome Fantasia],c.Principal AS [ID Vendedor]
    FROM netfeira.vw_cliente c
    WHERE c.[Status do Cliente]='ATIVO' AND c.[Tipo de Cliente]='J'
    AND c.[Dias Compra]<=365

    
    """,

    'Telefone':

    """

    SELECT b.cd_clien AS [ID Cliente],b.ddd AS [DDD],
    CASE WHEN b.ddd=LEFT(b.numero,2) THEN RIGHT(b.numero,9) ELSE b.numero END AS [Contato Cliente]
    FROM (

        SELECT a.cd_clien,a.tp_tel,a.ddd,a.numero,
        COUNT(a.numero)OVER(PARTITION BY a.numero) AS seq
        FROM tel_cli a

    )b
    INNER JOIN tp_tel c ON b.tp_tel=c.tp_tel
    WHERE b.seq=1 AND LEN(LEFT(b.numero,9))=9
    AND c.descricao='CELULAR'

    """,

    'Vendedor':

    """

    SELECT v.[ID Vendedor],v.[Nome Resumido],v.DDD AS [DDD Vendedor],v.Telefone AS [Contato Vendedor]
    FROM netfeira.vw_vendedor v
    WHERE v.[Status do Vendedor]='ATIVO' AND v.Telefone IS NOT NULL

    """,

    'Frequencia':

    """

    SELECT * FROM netfeira.vw_frequencia
    WHERE [Status de Atendimento] IN('LIGAR')
    AND YEAR([Data Agendada])=YEAR(GETDATE())

    """
}

def Main():

    df=sql.CriarTabela(kwargs=querys)

    temp_path=os.path.join(os.getcwd(),'Consolidado.csv')
    arq=glob(temp_path)

    temp_df=pd.DataFrame()

    df['Cliente']=df['Cliente'].merge(df['Telefone'],on='ID Cliente',how='inner')
    df['Cliente']=df['Cliente'].merge(df['Vendedor'],on='ID Vendedor',how='inner')
    df['Cliente']=df['Cliente'].merge(df['Frequencia'],on='ID Cliente',how='inner')
    
    if len(arq)>0:

        temp_df=pd.read_csv(temp_path,encoding='UTF-8')
        
        codigos=temp_df['ID Cliente'].unique().tolist()
        df['Cliente']=df['Cliente'].loc[~df['Cliente']['ID Cliente'].isin(codigos)]

        pass

    if len(df['Cliente'])>0:

        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        df['Cliente']=df['Cliente'].head(10)

        for i in df['Cliente'].index.tolist():

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            nome=df['Cliente'].loc[i,'Nome Fantasia']
            ddd=df['Cliente'].loc[i,'DDD']
            telefone=df['Cliente'].loc[i,'Contato Cliente']
            tipo=df['Cliente'].loc[i,'Status de Atendimento']

            vendedor=df['Cliente'].loc[i,'Nome Resumido']
            ddd_vend=df['Cliente'].loc[i,'DDD Vendedor']
            tel_vend=df['Cliente'].loc[i,'Contato Vendedor']
            tel_vend=f'{ddd_vend}{tel_vend}'

            texto=f'Olá {vendedor} tudo bem?'
            texto=urllib.parse.quote(texto)

            mensagem=f'{msg} *{nome}* tudo bem? Eu sou a Iris estou passando aqui porque identifiquei em nosso sistema que ainda o sr(a) não comprou ainda com agente. Caso preferir pode entrar em contato conosco no telefone: (11) 4673-2000 de Segunda à Sexta das 08:00 até 17:00 ou pode clicar no link abaixo para conversar com um de nossos consultores de venda:\n\nhttps://wa.me/55{tel_vend}?text={texto}' if tipo=='ATRASADO' else f'{msg} *{nome}* tudo bem? Eu sou a Iris estou passando para lembrar que ainda da tempo para adquirir os melhores produtos do mercado. Caso preferir pode entrar em contato conosco no telefone: (11) 4673-2000 e whatsapp: (11) 94298-7434 de Segunda à Sexta das 08:00 até 17:00 ou pode clicar no link abaixo para conversar com um de nossos consultores de venda:\n\nhttps://wa.me/55{tel_vend}?text={texto}'

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,'']

            pass

        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)
        
        temp_df=pd.concat([temp_df,df['Cliente']],axis=0,ignore_index=True)
        temp_df.to_csv(temp_path)


        pass
    
    pass



if __name__=='__main__':

    if datetime.now().day==1:

        temp_path=os.path.join(os.getcwd(),'Consolidado.csv')
        arq=glob(temp_path)

        if len(arq)>0:

            os.remove(temp_path)

            pass

        pass

    elif datetime.now().day>=1 and datetime.now().hour>=8 and datetime.now().hour<13 and datetime.now().isoweekday() in [1,2,3,4,5]:

        Main()

        pass

    pass