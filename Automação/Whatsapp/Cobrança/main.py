from Acesso import Login
from Query import Query
from Email import Email
from RemoverArquivo import Remover
from Moeda import Moeda
from datetime import datetime
import pandas as pd
import os
from glob import glob

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'cobranca':

    """

    WITH TabBoleto AS (

        SELECT * FROM (

            SELECT  b.NuTitEmpFat,b.Serie,b.LinhaDigitavel,b.BeneficiarioNome,b.PagadorNome,b.ValorTitulo,b.BoletoID,
            MAX(b.BoletoID)OVER(PARTITION BY b.NuTitEmpFat,b.Serie ORDER BY b.NuTitEmpFat,b.Serie) AS ID_MAX
            FROM Boleto b
            --WHERE NuTitEmpFat=1028725

        )a
        WHERE a.BoletoID=a.ID_MAX

    )

    SELECT a.[Data de Vencimento],a.[Data Alerta],
    CASE WHEN a.[Data de Vencimento]=a.[Data Alerta] THEN 1 ELSE 0 END [Alerta],
    a.Título,a.Serie,a.[ID Cliente],a.[Nome Fantasia],a.[E-mail Cliente],
    a.[Valor Líquido],a.Emitente,a.Destinatário,a.[Código de Barra],a.[Chave NFe]
    FROM (

        SELECT a.[Data de Vencimento],
        CASE WHEN a.[Data de Vencimento]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)
        THEN a.[Data de Vencimento]
        ELSE
            CASE WHEN DATEPART(DW,DATEADD(DAY,3,a.[Data de Vencimento])) IN(6,7) THEN
            DATEADD(DAY,
            (DATEPART(DW,DATEADD(DAY,3,a.[Data de Vencimento]))-5),
            DATEADD(DAY,3,a.[Data de Vencimento]))
            ELSE
            DATEADD(DAY,3,a.[Data de Vencimento])
            END
        END AS [Data Alerta],
        a.Título,a.Serie,a.[ID Cliente],a.[Nome Fantasia],c.[E-mail Cliente],a.[Condição de Pagamento],a.Situação,
        a.[Valor Líquido],
        b.BeneficiarioNome AS [Emitente],b.PagadorNome AS [Destinatário],b.LinhaDigitavel AS [Código de Barra],a.[Chave NFe]
        FROM netfeira.vw_contareceber a
        INNER JOIN netfeira.vw_cliente c ON a.[ID Cliente]=c.[ID Cliente]
        LEFT JOIN TabBoleto b ON a.Título=b.NuTitEmpFat AND a.Serie=b.Serie
        WHERE a.[ID Situação] IN('AB','PL') AND a.[Chave NFe] IS NOT NULL

    )a
    WHERE a.[Data Alerta]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)
    AND a.[Código de Barra] IS NOT NULL

    """,

    'telefone':

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

    """
}

def main():
    
    df=sql.CriarTabela(kwargs=querys)

    lista=df['telefone']['ID Cliente'].unique().tolist()
    df['whatsapp']=df['cobranca'].loc[df['cobranca']['ID Cliente'].isin(lista)]
    df['whatsapp']=df['whatsapp'].merge(df['telefone'],on='ID Cliente',how='inner')

    if len(df['whatsapp'])>0:

        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        for i in df['whatsapp'].index.tolist():

            nota=df['whatsapp'].loc[i,'Título']
            emitente=df['whatsapp'].loc[i,'Emitente']
            destinatario=df['whatsapp'].loc[i,'Nome Fantasia']
            dt_venc=datetime.strftime(df['whatsapp'].loc[i,'Data de Vencimento'],'%d/%m/%Y')
            chave=df['whatsapp'].loc[i,'Chave NFe']
            cd_barra=df['whatsapp'].loc[i,'Código de Barra']
            valor=Moeda.FormatarMoeda(df['whatsapp'].loc[i,'Valor Líquido'])
            alerta=df['whatsapp'].loc[i,'Alerta']

            ddd=df['whatsapp'].loc[i,'DDD Cli']
            telefone=df['whatsapp'].loc[i,'Numero Cli']

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            if alerta==1:

                mensagem=f'{msg} *{destinatario}* tudo bem? Me chamo Iris estou aqui para avisa-lo de que o boleto da NF-e *{nota}* vencerá hoje, dia {dt_venc}.\n\nSegue informações abaixo:\n\n\t.Emitente: *{emitente}*\n\t.Nota Fiscal: *{nota}*\n\t.Chave de Acesso da NF-e: *{chave}*\n\t.Valor: *{valor}*\n\n\tCódigo de Barra: {cd_barra}\n\n*Caso tenha efetuado o pagto, por favor desconsiderar. Ou para mais informações você pode entrar em contato pelo nosso canal de atendimento de Segunda à Sexta das 08:00 às 17:00 no telefone: (11) 4673-2000 e no Whatsapp: (11) 94298-6681.*\n\n{emitente} - Financeiro'

                pass

            else:


                mensagem=f'{msg} *{destinatario}* tudo bem? Sou a Iris e identifiquei em nosso sistema que o boleto da NF-e *{nota}* venceu no dia {dt_venc}.\n\nSegue informações abaixo:\n\n\t.Emitente: *{emitente}*\n\t.Nota Fiscal: *{nota}*\n\t.Chave de Acesso da NF-e: *{chave}*\n\t.Valor: *{valor}*\n\n\tCódigo de Barra: {cd_barra}\n\n*Caso tenha efetuado o pagto, por favor desconsiderar. Ou para mais informações você pode entrar em contato pelo nosso canal de atendimento de Segunda à Sexta das 08:00 às 17:00 no telefone: (11) 4673-2000 e no Whatsapp: (11) 94298-6681.*\n\n{emitente} - Financeiro'
                pass

            whatsapp_df.loc[len(whatsapp_df)]=[destinatario,ddd,telefone,mensagem,'']

            #break

            pass

        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)

        pass

    pass


if __name__=='__main__':

    main()

    pass