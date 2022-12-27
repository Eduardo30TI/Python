from email.mime import base
from Acesso import Login
from Query import Query
from Email import Email
from RemoverArquivo import Remover
from Tempo import DataHora
import os
import pandas as pd
from glob import glob

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={

    'Cliente':

    """

    SELECT * FROM netfeira.vw_cliente
    
    """,

    'Vendas':

    """
    
    DECLARE @BASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME,@DIAS SMALLINT

    SET @BASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DIAS=DAY(@BASE)*-1

    SET @DTFIM=DATEADD(DAY,@DIAS,@BASE)

    SET @DTINICIO=CONCAT(YEAR(@DTFIM),'-',MONTH(@DTFIM),'-01')

    SELECT * FROM netfeira.vw_targetestatico
    WHERE [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM
    AND [Tipo de Operação]='VENDAS'
    ORDER BY [Data de Faturamento]    
    
    """,
    
    'Listagem':
    
    """
    
    DECLARE @BASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME,@DIAS SMALLINT

    SET @BASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DIAS=DAY(@BASE)*-1

    SET @DTFIM=DATEADD(DAY,@DIAS,@BASE)

    SET @DTINICIO=CONCAT(YEAR(@DTFIM),'-',MONTH(@DTFIM),'-01');

    SELECT * FROM (
    SELECT [ID Cliente],[ID Vendedor],[Pedido],[Data de Faturamento],SUM([Total Geral]) AS 'Total Geral'
    FROM netfeira.vw_targetestatico
    WHERE [Data de Faturamento]<=@DTFIM
    AND [Tipo de Operação]='VENDAS' AND Situação<>'EM ABERTO'
    GROUP BY [ID Cliente],[ID Vendedor],[Pedido],[Data de Faturamento])base
    WHERE [Total Geral]>0 
    
    """,
    
    'Vendedor':
    
    """
    
    SELECT * FROM netfeira.vw_vendedor
    WHERE [Status do Vendedor]='ATIVO'    
    
    """,
    
    'Supervisor':
    
    """
    
    SELECT * FROM netfeira.vw_supervisor
    
    """

}

def Abertura(tabelas_df):

    vendedor_df=pd.DataFrame()

    vendedor_df=tabelas_df['Vendedor'].merge(tabelas_df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria', 'Status do Vendedor', 'ID Sup', 'Supervisor', 'Email Sup',
        'ID Gerente', 'Gerente', 'Email Gerente']]

    vendedor_df=vendedor_df.loc[~vendedor_df['Equipe'].str.contains('120')]    

    vendas_df=pd.DataFrame()

    temp_df=pd.DataFrame()

    cliente_df=pd.DataFrame()

    abertura_df=pd.DataFrame()

    vendas_df=tabelas_df['Vendas'].merge(tabelas_df['Cliente'],on='ID Cliente',how='inner')[['Data de Emissão', 'Data de Faturamento', 'Pedido', 'Nfe', 'ID Empresa',
        'ID Cliente','Data de Cadastro', 'ID Vendedor', 'Tipo de Pedido', 'Tipo de Operação',
        'Tabelas', 'SKU', 'Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA',
        'Total Geral', 'Total Venda', 'Comissão R$', 'Margem Bruta R$',
        'Cad Vendedor', 'Situação', 'Peso Bruto KG', 'Peso Líquido KG']]

    vendas_df['Positivado']=vendas_df.apply(lambda info: 1 if info['Data de Emissão']==info['Data de Cadastro'] else 0,axis=1)

    dt_max=vendas_df['Data de Faturamento'].max()

    temp_df=vendas_df[['ID Cliente','Total Geral']].loc[(vendas_df['Data de Emissão'].dt.year==dt_max.year)&(vendas_df['Data de Emissão'].dt.month==dt_max.month)].groupby(['ID Cliente'],as_index=False).sum()

    codigos=temp_df['ID Cliente'].loc[temp_df['Total Geral']<=0].unique().tolist()

    vendas_df=vendas_df.loc[~vendas_df['ID Cliente'].isin(codigos)]

    vendas_df=vendas_df.loc[(vendas_df['Data de Emissão'].dt.year==dt_max.year)&(vendas_df['Data de Emissão'].dt.month==dt_max.month)]

    vendas_df=vendas_df.loc[vendas_df['Positivado']==1].groupby(['ID Cliente','ID Vendedor'],as_index=False).agg({'Total Geral':'sum','Data de Emissão':'min','Pedido':'min'})

    vendas_df=vendas_df.loc[vendas_df['Total Geral']>0]

    cliente_df=tabelas_df['Cliente'].drop(columns=tabelas_df['Cliente'].columns[-1])

    cliente_df=cliente_df.merge(vendas_df,on='ID Cliente',how='inner')

    abertura_df=cliente_df.merge(vendedor_df,on='ID Vendedor',how='inner')[['ID Cliente', 'CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'ID Segmento', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato', 'Limite de Crédito',
        'ID Vendedor','Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria', 'Status do Vendedor', 'ID Sup', 'Supervisor', 'Email Sup',
        'ID Gerente', 'Gerente', 'Email Gerente','Total Geral', 'Data de Emissão', 'Pedido']]

    abertura_df['Arquivo']='ABERTURA'

    print(abertura_df)

    pass

def Dias(info):
    
    res=info['Última Compra']-info['Penúltima Compra']
    
    res=str(res)
    
    lista=[l for l in res.split()]
    
    res=int(lista[0])
    
    return res
    
    pass

def Enviar(dt_max,base_df):

    data_atual=data.HoraAtual()

    hora=data_atual.hour

    msg='Bom dia' if hora<12 else 'Boa tarde'
    
    mes=data.Mes(dt_max.month)

    assunto='Abertura & Reativação'

    colunas=[l for l in base_df.columns.tolist() if str(l).find('mail')>0]

    nomes={'E-mail':'Nome Resumido','Email Sup':'Supervisor','Email Gerente':'Gerente'}

    for coluna in colunas:

        emails=[l for l in base_df[coluna].unique().tolist() if l!='']

        print(base_df.loc[base_df['Arquivo']=='ABERTURA'])

        pass
    
    pass

if __name__=='__main__':

    tabelas_df=sql.CriarTabela(kwargs=querys)

    Abertura(tabelas_df)

    pass