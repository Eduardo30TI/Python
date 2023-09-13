from Acesso import Login
from Query import Query
from Moeda import Moeda
from Email import Email
from RemoverArquivo import Remover
from datetime import datetime
import os
from glob import glob

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'venda':

    """

    DECLARE @DTBASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=DATEADD(DAY,DAY(@DTBASE)*-1,@DTBASE)

    SET @DTINICIO=DATEADD(DAY,1,
        
        DATEADD(DAY,DAY(DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))*-1,DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))

    )

    SELECT c.Ano,c.[ID Mês],c.Mês,ped.SKU,p.Produto,p.Fabricante,p.[Fator CX],SUM(ped.Qtde) AS Qtde,
    CONVERT(INT,SUM(ped.Qtde)/NULLIF(p.[Fator CX],0)) AS Caixa,
    CONVERT(INT,
    ((SUM(ped.Qtde)/NULLIF(p.[Fator CX],0))-CONVERT(INT,SUM(ped.Qtde)/NULLIF(p.[Fator CX],0)))*p.[Fator CX]) AS Pacote,
    SUM(ped.[Total Venda]) AS [Total Venda],
    CONVERT(DECIMAL(15,4),SUM(ped.[Total Venda])/SUM(ped.Qtde)) AS [Preço Médio],
    SUM(ped.[Peso Bruto KG]) AS [Tonelada KG]
    FROM netfeira.vw_venda_estatico ped
    INNER JOIN netfeira.vw_produto p ON ped.SKU=p.SKU AND LTRIM(RTRIM(p.Fabricante))='FRAGOLE'
    INNER JOIN netfeira.vw_calend c ON ped.[Data de Faturamento]=c.Data
    WHERE [Tipo de Operação]<>'OUTROS'
    AND [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM
    GROUP BY c.Ano,c.[ID Mês],c.Mês,ped.SKU,p.Produto,p.Fabricante,p.[Fator CX]
    ORDER BY c.Ano,c.[ID Mês]

    """,

    'data':

    """

    DECLARE @DTBASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=DATEADD(DAY,DAY(@DTBASE)*-1,@DTBASE)

    SET @DTINICIO=DATEADD(DAY,1,
        
        DATEADD(DAY,DAY(DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))*-1,DATEADD(DAY,DAY(@DTFIM)*-1,@DTFIM))

    )

    SELECT @DTFIM AS[DTFIM],@DTINICIO AS [DTINICIO]

    """
}

def main():

    df=sql.CriarTabela(kwargs=querys)

    for c in ['ID Mês','Mês']:

        df['venda'][c]=df['venda'][c].astype(str)

        pass

    df['venda']['Mês']=df['venda']['ID Mês'] +' - '+df['venda']['Mês']

    df['venda']=df['venda'].pivot(index=['SKU','Produto','Fabricante','Fator CX'],columns=['Ano','Mês'],values=['Qtde','Caixa','Total Venda','Preço Médio','Tonelada KG'])

    temp_path=os.path.join(os.getcwd(),'SELL OUT FRAGOLE.xlsx')
    df['venda'].to_excel(temp_path)

    assunto='SELL OUT FRAGOLE'

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    nome='alisson schell'

    dt_inicio=datetime.strftime(df['data'].loc[0,'DTINICIO'],'%d/%m/%Y')
    dt_fim=datetime.strftime(df['data'].loc[0,'DTFIM'],'%d/%m/%Y')

    mensagem=f"""

    <p>{msg};</p>

    <p>{str(nome).title()}</p>

    <p>Segue o SELL OUT entre os dias {dt_inicio} até {dt_fim}.</p>

    <p>Por favor não responder mensagem automática</p>

    <p>Atenciosamente</p>

    <p>BOT TI</p>

    """
    
    anexo=glob(temp_path)
    
    temp_dict={'To':['alisson.schell@fragole.com.br'],'CC':['julio@demarchibrasil.com.br','rogerio.felipim@demarchibrasil.com.br','eduardo.marfim@demarchibrasil.com.br'],'Anexo':anexo}

    Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)
    Remover.RemoverArquivo('.xlsx')

    pass



if __name__=='__main__':

    main()

    pass