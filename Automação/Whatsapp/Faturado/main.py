from Acesso import Login
from Query import Query
import pandas as pd
import os
from glob import glob
from datetime import datetime
from Moeda import Moeda
import pandas as pd

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Vendas':

    """

    SELECT a.[Data de Emissão],a.[Data de Faturamento],a.[Data de Entrega],a.[Tipo de Operação],a.Situação,a.[ID Cliente],
    c.[Razão Social],c.[Nome Fantasia],a.Pedido,a.NFe,
    n.nfe_chave_acesso AS [Chave de Acesso],
    SUM(a.[Total Venda]) AS [Total Venda],COUNT(a.SKU) AS [MIX]
    FROM netfeira.vw_targetestatistico a
    INNER JOIN netfeira.vw_cliente c ON a.[ID Cliente]=c.[ID Cliente]
    INNER JOIN nota n ON a.NFe=n.nu_nf_emp_fat
    WHERE [Data de Faturamento]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)
    AND [Tipo de Operação]<>'OUTROS' AND [ID Situação]='FA' AND n.nfe_chave_acesso IS NOT NULL
    GROUP BY a.[Data de Emissão],a.[Data de Faturamento],a.[Tipo de Operação],a.Situação,a.[ID Cliente],
    a.Pedido,a.NFe,c.[Razão Social],c.[Nome Fantasia],a.[Data de Entrega],n.nfe_chave_acesso

    """,

    'Telefones':

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

    """
}

def Main():

    df=sql.CriarTabela(kwargs=querys)
    df['Vendas']=df['Vendas'].merge(df['Telefones'],on='ID Cliente',how='inner')

    if datetime.now().hour<12:

        msg='Bom dia'

        pass

    elif datetime.now().hour<18:

        msg='Boa tarde'

        pass


    else:

        msg='Boa noite'

        pass

    temp_path=os.path.join(os.getcwd(),'Consolidado.csv')
    arq=glob(temp_path)

    temp_df=pd.DataFrame()

    if len(arq)>0:

        temp_df=pd.read_csv(temp_path,encoding='UTF-8')
        lista=temp_df['NFe'].unique().tolist()

        df['Vendas']=df['Vendas'].loc[~df['Vendas']['NFe'].isin(lista)]

        pass

    if len(df['Vendas'])>0:

        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        for i in df['Vendas'].index.tolist():

            tipo=df['Vendas'].loc[i,'Tipo de Operação']
            nome=df['Vendas'].loc[i,'Nome Fantasia']
            situacao=df['Vendas'].loc[i,'Situação']
            pedido=df['Vendas'].loc[i,'Pedido']
            nfe=df['Vendas'].loc[i,'NFe']
            chave=df['Vendas'].loc[i,'Chave de Acesso']
            total=Moeda.FormatarMoeda(df['Vendas'].loc[i,'Total Venda'].sum())
            mix=Moeda.FormatarMoeda(df['Vendas'].loc[i,'MIX'].sum())
            ddd=df['Vendas'].loc[i,'DDD']
            telefone=df['Vendas'].loc[i,'Contato Cliente']

            mensagem=f'Tipo de nota: {str(tipo).capitalize()} - Status: {str(situacao).capitalize()}\n\n{msg} *{nome}* tudo bem? me chamo Iris estou passando para informar que seu pedido: *{pedido}* no valor de *R$ {total}* já foi emitida a nota fiscal. Dúvidas você pode entrar em contato com a nossa central no número: (11) 4673-2000 ou pelo whatsapp: (11) 94298-7434 para falar com uma de nossas consultoras de vendas. Nosso horário de atendimento é de Segunda à Sexta das 08:00 as 17:00.\n\nCaso precise segue o número da chave de acesso da nota fiscal: *{chave}*\n\nObs. A chave enviada não é uma chave PIX.' if msg!='Boa noite' else f'Tipo de nota: {str(tipo).capitalize()} - Status: {str(situacao).capitalize()}\n\n{msg} *{nome}* tudo bem? pesso desculpa pelo horário me chamo Iris estou passando para informar que seu pedido: *{pedido}* no valor de *R$ {total}* já foi emitida a nota fiscal. Dúvidas você pode entrar em contato com a nossa central no número: (11) 4673-2000 ou pelo whatsapp: (11) 94298-7434 para falar com uma de nossas consultoras de vendas. Nosso horário de atendimento é de Segunda à Sexta das 08:00 as 17:00.\n\nCaso precise segue o número da chave de acesso da nota fiscal: *{chave}*\n\nObs. A chave enviada não é uma chave PIX.'

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,'']

            #break

            pass

        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)
            
        temp_df=pd.concat([temp_df,df['Vendas']],axis=0,ignore_index=True)
        temp_df.to_csv(temp_path,index=False,encoding='UTF-8')

        pass

    pass


if __name__=='__main__':

    Main()

    pass