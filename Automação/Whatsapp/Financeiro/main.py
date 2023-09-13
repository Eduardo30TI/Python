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
    df['consolidado']=df['cobranca'].merge(df['telefone'],on='ID Cliente',how='left')
    df['consolidado']=df['consolidado'].loc[(df['consolidado']['E-mail Cliente']=='')|(df['consolidado']['Numero Cli'].isnull())]

    df['consolidado']=df['consolidado'][['ID Cliente','Nome Fantasia','E-mail Cliente','DDD Cli','Numero Cli']]
    df['consolidado'].drop_duplicates(inplace=True)
    
    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    if len(df['consolidado'])>0:

        temp_path=os.path.join(os.getcwd(),'Lista de clientes.xlsx')
        df['consolidado'].to_excel(temp_path,index=False)
                
        msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

        clientes=Moeda.Numero(len(df['consolidado']['ID Cliente'].unique().tolist()))

        mensagem=f'{msg} como você está? Aqui quem fala é a Iris estou te encaminhando uma relação de {clientes} cliente(s) que estão faltando informações para envio de cobrança, peço que verifique está relação e atualize no sistema para futuras cobranças. Agradeço desde já e tenha um excelente dia.'

        whatsapp_df.loc[len(whatsapp_df)]=['Financeiro','11','942986681',mensagem,temp_path]
        
        whatsapp_df.to_excel('whatsapp.xlsx',index=False)

        pass

    pass


if __name__=='__main__':

    main()

    pass