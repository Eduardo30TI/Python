 Acesso import Login
from Query import Query
from datetime import datetime
import pandas as pd
import urllib
import os
import shutil
from glob import glob
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Cliente':

    """

    DECLARE @DTBASE DATETIME, @DTFIM DATETIME, @DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=DATEADD(DAY,1,DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))

    SELECT  [ID Cliente],[Nome Fantasia],[Última Compra],[Principal] AS [ID Vendedor]
    FROM netfeira.vw_cliente
    WHERE [Status do Cliente]='ATIVO' AND [Tipo de Cliente]='J' AND Crédito='NORMAL'
    AND NOT [Última Compra] BETWEEN @DTINICIO AND @DTFIM
    ORDER BY COALESCE([Limite de Crédito],0) DESC

    """,

    'Telefones':

    """

    SELECT * FROM (

        SELECT a.cd_clien AS [ID Cliente],a.ddd AS [DDD Cli],a.numero AS [Numero Cli],
        COUNT(a.numero)OVER(PARTITION BY a.numero) AS seq
        FROM (

        SELECT a.cd_clien,LEFT(a.ddd,2) AS ddd,a.numero
        FROM tel_cli a
        INNER JOIN tp_tel b ON a.tp_tel=b.tp_tel
        WHERE b.descricao='CELULAR' AND LEN(a.numero)=9
        )a

    )a
    WHERE a.seq=1
    ORDER BY 1

    """,

    'Vendedor':


    """

    SELECT v.[ID Vendedor],v.[Nome Resumido],v.[Status do Vendedor],V.Categoria,
    CONCAT(v.DDD,v.Telefone) AS [Contato Vendedor]
    FROM netfeira.vw_vendedor v
    WHERE v.[Status do Vendedor]='ATIVO' AND v.Telefone IS NOT NULL

    """


}

def Main():

    df=sql.CriarTabela(kwargs=querys)

    id='CLISEMCO'
    
    codigos=df['Vendedor'].loc[df['Vendedor']['Categoria']=='CLT','ID Vendedor'].unique().tolist()

    temp=[]

    while True:

        temp_df=df['Cliente'].loc[df['Cliente']['ID Vendedor']==id]

        cont=len(temp_df)

        if cont==0:

            break

        if len(temp)==len(codigos):

            temp.clear()

            pass
        
        for i in temp_df.index.tolist():
            
            for c in codigos:

                if c in temp:

                    continue

                else:

                    temp.append(c)
                   
                    df['Cliente'].loc[i,'ID Vendedor']=c
                    
                    break

                pass

            break

            pass

        #break

        pass

    df['Cliente']=df['Cliente'].merge(df['Telefones'],on='ID Cliente')
    df['Cliente']=df['Cliente'].merge(df['Vendedor'][['ID Vendedor','Nome Resumido','Contato Vendedor']],on='ID Vendedor')

    temp_path=os.path.join(os.getcwd(),'Consolidado.csv')
    arq=glob(temp_path)

    temp_df=pd.DataFrame()

    if len(arq)>0:

        temp_df=pd.read_csv(arq[-1],encoding='UTF-8')
        codigos=temp_df['ID Cliente'].unique().tolist()

        df['Cliente']=df['Cliente'].loc[~df['Cliente']['ID Cliente'].isin(codigos)]
        df['Cliente']=df['Cliente'].head(50)

        pass

    else:

        df['Cliente']=df['Cliente'].head(50)

        pass

    if len(df['Cliente'])>0:

        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        for i in df['Cliente'].index.tolist():

            nome=df['Cliente'].loc[i,'Nome Fantasia']

            ddd=df['Cliente'].loc[i,'DDD Cli']

            numero=df['Cliente'].loc[i,'Numero Cli']

            tel_vend=df['Cliente'].loc[i,'Contato Vendedor']

            vendedor=str(df['Cliente'].loc[i,'Nome Resumido']).title()
            texto=f'Olá {vendedor} tudo bem?'
            texto=urllib.parse.quote(texto)

            ul_compra=df['Cliente'].loc[i,'Última Compra']
            ul_compra=datetime.strftime(ul_compra,'%d/%m/%Y')

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            mensagem=f'{msg} *{nome}* tudo bem? meu nome é Iris, sou uma assistente virtual em desenvolvimento pela DE MARCHI SÃO PAULO. Identifiquei em nosso sistema que sua última compra foi *{ul_compra}*. Por esse motivo a DE MARCHI SÃO PAULO, está com novidades que acredito ser o ideal para seu estabelecimento, estamos entrando em contato para restabelecer nossa parceria. Se preferir você pode entrar em contato através dos nossos canais de atendimento: Telefone (11) 4673-2000 / Whatsapp (11) 94298-7434.\n\nou também clicando no link abaixo que será direcionado para um de nossos consultores de venda:\n\nhttps://wa.me/55{tel_vend}?text={texto}'

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,numero,mensagem,'']
            
            pass

        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)
        
        temp_df=pd.concat([temp_df,df['Cliente']],axis=0,ignore_index=True)
        temp_df.to_csv(temp_path)

        pass

    pass



if __name__=='__main__':

    if datetime.now().day==1:

        temp_path=os.path.join(os.getcwd(),'Consolidado.csv')
        os.remove(temp_path)

        pass

    elif datetime.now().day>=15 and datetime.now().hour>=8 and datetime.now().hour<17 and datetime.now().isoweekday() in [1,2,3,4,5]:

        Main()

        pass

    pass