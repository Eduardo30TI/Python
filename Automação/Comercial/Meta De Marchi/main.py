from Acesso import Login
from Query import Query
from Moeda import Moeda
from RemoverArquivo import Remover
from Email import Email
from glob import glob
import os
import pandas as pd
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Vendas':

    """
    
    DECLARE @DTBASE DATETIME, @DTFIM DATETIME, @DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=DATEADD(DAY,(DAY(@DTFIM)-1)*-1,@DTFIM)

    SELECT LTRIM(RTRIM(b.[ID Vendedor])) AS [ID Vendedor],
    b.Fabricante,SUM(b.[Total Venda]) AS [Total Venda] 
    FROM (

        SELECT a.[ID Vendedor],
        CASE WHEN p.Fabricante='DE MARCHI' THEN 'DE MARCHI' ELSE 'OUTROS' END AS Fabricante,
        a.[Total Venda]
        FROM netfeira.vw_venda_estatico a
        INNER JOIN netfeira.vw_produto p ON a.SKU=p.SKU
        WHERE [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM AND [Tipo de Operação]='VENDAS'

    )b
    GROUP BY b.[ID Vendedor],b.Fabricante
        
    """,

    'Calendario':

    """
    
    DECLARE @DTBASE DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SELECT *
    FROM netfeira.vw_calend
    WHERE YEAR(Data)=YEAR(@DTBASE) AND MONTH(Data)=MONTH(@DTBASE)
    AND [Dia Útil]=1
    
    """,

    'Supervisor':

    """
    
    SELECT LTRIM(RTRIM(v.[ID Vendedor])) AS [ID Vendedor],s.[Email Sup]
    FROM netfeira.vw_vendedor v
    INNER JOIN netfeira.vw_supervisor s ON v.[ID Equipe]=s.[ID Equipe]
    
    """


}

def Main(df):

    dia_util=df['Calendario']['Data'].count()

    dia_trab=df['Calendario'].loc[df['Calendario']['Data Trabalhada'].notnull(),'Data'].count()-1

    temp_path=os.path.join(os.getcwd(),'Metas','*.xlsx')

    arquivos=glob(temp_path)

    excel_df=pd.read_excel(arquivos[-1])

    excel_df=excel_df.merge(df['Supervisor'],on='ID Vendedor',how='inner')

    colunas=[l for l in excel_df.columns if str(l).find('Meta')>=0]

    for c in colunas:
        
        excel_df[c]=excel_df[c].astype(float)
        
        excel_df[f'{c} Diária']=round(excel_df[c]/dia_util,2)
        
        pass

    df['Consolidado']=df['Vendas'].pivot(index='ID Vendedor',columns='Fabricante',values='Total Venda').reset_index()

    for c in ['DE MARCHI','OUTROS']:

        df['Consolidado'].loc[df['Consolidado'][c].isnull(),c]=0
            
        pass

    df['Consolidado']['Total Geral']=df['Consolidado']['DE MARCHI']+df['Consolidado']['OUTROS']

    for c in ['DE MARCHI','OUTROS','Total Geral']:

        df['Consolidado'][f'Projeção {c}']=round(((df['Consolidado'][c]/dia_trab)*dia_util),2)
            
        pass

    excel_df=excel_df.merge(df['Consolidado'],on='ID Vendedor',how='left')
    
    excel_df['DE MARCHI %']=excel_df.apply(lambda info: round(info['DE MARCHI']/info['Meta DeMarchi'],4)*100 if info['Meta DeMarchi']>0 else 0,axis=1)

    excel_df['OUTROS %']=excel_df.apply(lambda info: round(info['OUTROS']/info['Meta Outros'],4)*100 if info['Meta Outros']>0 else 0,axis=1)

    excel_df['Meta %']=excel_df.apply(lambda info: round(info['Total Geral']/info['Meta R$'],4)*100 if info['Meta R$']>0 else 0,axis=1)

    excel_df=excel_df[['ID Vendedor', 'Vendedor', 'Equipe', 'Supervisor','Email Sup', 'Meta DeMarchi',
        'Meta Outros', 'Meta R$', 'Meta DeMarchi Diária', 'Meta Outros Diária',
        'Meta R$ Diária', 'DE MARCHI', 'OUTROS', 'Total Geral',
        'Projeção DE MARCHI', 'Projeção OUTROS', 'Projeção Total Geral',
        'DE MARCHI %', 'OUTROS %', 'Meta %']]
   
    emails=excel_df['Email Sup'].unique().tolist()

    df['Vendas']=df['Vendas'].merge(df['Supervisor'],on='ID Vendedor',how='inner')

    for e in emails:

        if len(df['Vendas'].loc[df['Vendas']['Email Sup']==e])<=0:

            continue
        
        temp_df=excel_df.loc[excel_df['Email Sup']==e]

        demarchi=Moeda.FormatarMoeda(temp_df['DE MARCHI'].sum())

        outros=Moeda.FormatarMoeda(temp_df['OUTROS'].sum())

        msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

        nome=str(temp_df['Supervisor'].unique().tolist()[-1]).title()

        email_to=[e]

        email_cc=[]

        assunto='Atenção - Metas por fabricante'

        path_img=os.path.join(os.getcwd(),'Email','*.png')

        img=glob(path_img)

        messagem=f"""
                    
        <p>{msg};</p>

        <p>{nome}</p>

        <p>Segue a meta dos vendedores por fabricante você vendeu da marca DE MARCHI R$ {demarchi} e de OUTROS R$ {outros}.</p>

        <P>Por favor não responder mensagem automática</P>
        
        <img src="{img[-1]}" height=195 with=326>
        
        """

        temp_df.to_excel(f'{nome}.xlsx',index=False)

        temp_path=os.path.join(os.getcwd(),f'{nome}.xlsx')

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':[temp_path]}

        Email.EnviarEmail(corpo=messagem,assunto=assunto,kwargs=temp_dict)

        Remover.RemoverArquivo('.xlsx')

        #break

        pass

    pass


if __name__=='__main__':

    df=sql.CriarTabela(kwargs=querys)

    Main(df)

    pass