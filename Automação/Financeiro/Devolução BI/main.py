from Acesso import Login
from Query import Query
import requests

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'Devolução':
    
    """
    
    SELECT d.[Data de Entrada],d.Motivo,d.[Situação do Pedido],d.[Tipo de Operação],d.Pedido,d.NFe,
    d.[ID Cliente],c.[Nome Fantasia],COALESCE(c.Matriz,'AVULSO') AS [Matriz],s.Segmento,s.Canal,
    d.[ID Vendedor],v.[Nome Resumido],su.Equipe,su.Supervisor,
    d.SKU,p.Produto,p.Fabricante,p.Linha,
    d.Qtde,d.[Unid. VDA],d.[Qtde VDA],d.[Valor Unitário],
    d.[Total Geral]
    FROM netfeira.vw_devolucao d
    INNER JOIN netfeira.vw_cliente c ON d.[ID Cliente]=c.[ID Cliente]
    INNER JOIN netfeira.vw_segmento s ON c.[ID Segmento]=s.[ID Segmento]
    INNER JOIN netfeira.vw_vendedor v ON d.[ID Vendedor]=v.[ID Vendedor]
    INNER JOIN netfeira.vw_supervisor su ON v.[ID Equipe]=su.[ID Equipe]
    INNER JOIN netfeira.vw_produto p ON d.SKU=p.SKU
    WHERE [Tipo de Operação]='VENDAS' AND YEAR(d.[Data de Entrada])=YEAR(GETDATE())
    ORDER BY d.[Data de Entrada]    
    
    """,
    
    'Data':
    
    """
    
    DECLARE @DTBASE DATETIME, @DTFIM DATETIME, @DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=DATEADD(DAY,(DAY(@DTFIM)-1)*-1,@DTFIM)

    SELECT @DTINICIO AS [Data Mín],@DTFIM AS [Data Máx]    
    
    
    """,
    
    'Calendario':
    
    """
    
    SELECT * FROM netfeira.vw_calend
    
    """,
    
    'Vendas':
    
    """
    
    DECLARE @DTBASE DATETIME, @DTFIM DATETIME, @DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=DATEADD(DAY,(DAY(@DTFIM)-1)*-1,@DTFIM)

    SELECT SUM([Total Venda]) AS [Total Venda]
    FROM netfeira.vw_venda_estatico
    WHERE [Tipo de Operação]='VENDAS' AND [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM AND [Situação]='FATURADO'
    
    """
    
}

def Main(df):

    apis={

        'Mensal':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/fca3ccbf-8f44-46d7-b9d6-1b1e444c1a4c/rows?key=x7I8Om6uyfmzknv%2BaCtmS0ozkzNE0%2BMeU3rfQWNiuCWYkwg0Nci75hg1U1j7oLOKGyYamI4s1wdY1BBs7J8Eyg%3D%3D',

        'Motivo':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/205e82d5-a50f-4dcd-9c56-996348f07033/rows?key=xd1MleqLmSXyllvn3c%2Ba%2FMxUg8ZNniG7yLnMgxxvL3zsRxrj8HwACFsx%2BPIV9vqli9OEEUpL%2BBaKRI8zoTL%2FCQ%3D%3D',

        'Matriz':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/6939cce9-2cfc-4013-9a2c-a20d4dd90826/rows?key=eYyo%2F7UDfz9hLFPbs2e8k3%2B1xDystFHA6jOho2tU%2BuMDuRorYDF%2FsZDWPy1RwfbgD2XP1fzt9c%2FnX2VSPnOiug%3D%3D',

        'Consolidado':'https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/4952998c-d1ea-4be9-a517-46c80a30bb91/rows?key=s3CGmG0T8hscwnnH%2F%2FRW2xHeOiWAuEGnK2t6%2FYm%2BLQp1pGAs5NzwgONwpYeW9u3zk1NbMLxXOwmnHBaP8I8efw%3D%3D'


    }

    df['Devolução']=df['Devolução'].merge(df['Calendario'],left_on='Data de Entrada',right_on='Data',how='inner')

    dt_min=df['Data'].loc[0,'Data Mín']

    dt_max=df['Data'].loc[0,'Data Máx']

    df['Consolidado']=df['Devolução'].loc[df['Devolução']['Data de Entrada'].between(dt_min,dt_max)]

    df['Situacao']=df['Consolidado'].groupby(['Situação do Pedido'],as_index=False).agg({'Total Geral':'sum'})

    total=df['Vendas']['Total Venda'].sum()

    cancelado=df['Situacao'].loc[df['Situacao']['Situação do Pedido'].str.contains('CA'),'Total Geral'].sum()

    devolucao=df['Situacao'].loc[df['Situacao']['Situação do Pedido'].str.contains('DEV'),'Total Geral'].sum()

    perc_dev=round(devolucao/total,4)*100

    perc_can=round(cancelado/total,4)*100

    df['Motivo']=df['Consolidado'].loc[df['Consolidado']['Situação do Pedido'].str.contains('DEV')].groupby(['Motivo'],as_index=False).agg({'Total Geral':'sum'})

    df['Motivo'].sort_values('Total Geral',ascending=False,ignore_index=True,inplace=True)

    df['Mensal']=df['Devolução'].loc[df['Devolução']['Situação do Pedido'].str.contains('DEV')].groupby(['ID Mês','Mês'],as_index=False).agg({'Total Geral':'sum'})

    df['Mensal'].sort_values('ID Mês',ascending=True,ignore_index=True,inplace=True)

    df['Matriz']=df['Consolidado'].loc[df['Consolidado']['Situação do Pedido'].str.contains('DEV')].groupby(['Matriz'],as_index=False).agg({'Total Geral':'sum'})

    df['Matriz'].sort_values('Total Geral',ascending=False,ignore_index=True,inplace=True)

    requests.post(url=apis['Mensal'],json=df['Mensal'].to_dict('records'))

    requests.post(url=apis['Motivo'],json=df['Motivo'].to_dict('records'))

    requests.post(url=apis['Matriz'],json=df['Matriz'].to_dict('records'))

    temp_dict={
        
        'Venda':float(total),
        'Cancelado':float(cancelado),
        'Devolução':float(devolucao),
        'Devolução %':float(perc_dev),
        'Cancelado %':float(perc_can),
        'Min':float(0),
        'Max':float(100)

    }

    requests.post(url=apis['Consolidado'],json=temp_dict)

    pass

if __name__=='__main__':

    df=sql.CriarTabela(kwargs=querys)

    Main(df)

    pass