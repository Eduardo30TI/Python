from Acesso import Login
from Query import Query
import pandas as pd
import requests

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'Estatico':
    
    """
    
    DECLARE @DTBASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=CONCAT(YEAR(@DTFIM),'-',MONTH(@DTFIM),'-01')

    SELECT * FROM netfeira.vw_estatistico
    WHERE [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM AND [Tipo de Operação]<>'OUTROS'
    ORDER BY [Data de Faturamento]
    
    """,
    
    'Aberto':
    
    """
    
    SELECT * FROM netfeira.vw_aberto
    WHERE [Data do Pedido]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)  
    
    """,
    
    'Produto':
    
    """
    
    SELECT * FROM netfeira.vw_produto
    WHERE Fabricante LIKE '%MCCAIN%'
    
    """,
    
    'Calendario':
    
    """

    SELECT * FROM netfeira.vw_calend
    WHERE YEAR([Data])=YEAR(GETDATE()) AND MONTH([Data])=MONTH(GETDATE()) AND [Dia Útil]=1
    
    """
    
}

def Main(tabelas_df):

    calend_df=pd.DataFrame()

    calend_df=tabelas_df['Calendario']

    util=len(calend_df['Data'].unique().tolist())

    trabalhado=len(calend_df['Data Trabalhada'].loc[~calend_df['Data Trabalhada'].isnull()].unique().tolist())-1

    restante=util-trabalhado

    #Meta

    metas_df=pd.DataFrame()

    metas_df=tabelas_df['Produto'][['Grupo MCCAIN','Produto']].groupby(['Grupo MCCAIN'],as_index=False).count()

    metas_df.loc[metas_df['Grupo MCCAIN'].str.contains('FOOD'),'Meta KG']=(80*1000)

    metas_df.loc[metas_df['Grupo MCCAIN'].str.contains('VAREJO'),'Meta KG']=(40*1000)

    #Vendas

    vendas_df=pd.DataFrame()

    vendas_df=tabelas_df['Estatico']    

    vendas_df=vendas_df[['SKU','Total Venda','Peso Líquido KG','Peso Bruto KG']].groupby(['SKU'],as_index=False).sum()

    vendas_df=vendas_df.merge(tabelas_df['Produto'],on='SKU',how='inner')[['SKU','Produto','Fabricante','Grupo MCCAIN','Categoria','Linha','Total Venda', 'Peso Líquido KG', 'Peso Bruto KG']]

    aberto_df=pd.DataFrame()

    aberto_df=tabelas_df['Aberto'].loc[tabelas_df['Aberto']['Situação']=='AB']

    aberto_df=aberto_df[['SKU','Total Venda','Peso Líquido KG','Peso Bruto KG']].groupby(['SKU'],as_index=False).sum()

    aberto_df=aberto_df.merge(tabelas_df['Produto'],on='SKU',how='inner')[['SKU','Produto','Fabricante','Grupo MCCAIN','Categoria','Linha','Total Venda', 'Peso Líquido KG', 'Peso Bruto KG']]

    dia_df=pd.DataFrame()

    dia_df=tabelas_df['Aberto']

    dia_df=dia_df[['SKU','Total Venda','Peso Líquido KG','Peso Bruto KG']].groupby(['SKU'],as_index=False).sum()

    dia_df=dia_df.merge(tabelas_df['Produto'],on='SKU',how='inner')[['SKU','Produto','Fabricante','Grupo MCCAIN','Categoria','Linha','Total Venda', 'Peso Líquido KG', 'Peso Bruto KG']]

    #Meta

    metas_df['Faturado KG']=metas_df['Grupo MCCAIN'].apply(lambda info: vendas_df['Peso Líquido KG'].loc[vendas_df['Grupo MCCAIN']==info].sum())

    metas_df['Total KG']=metas_df['Grupo MCCAIN'].apply(lambda info: dia_df['Peso Líquido KG'].loc[dia_df['Grupo MCCAIN']==info].sum())

    metas_df['Aberto KG']=metas_df['Grupo MCCAIN'].apply(lambda info: aberto_df['Peso Líquido KG'].loc[aberto_df['Grupo MCCAIN']==info].sum())

    metas_df['Realizado KG']=metas_df['Faturado KG']+metas_df['Aberto KG']

    metas_df['Projeção KG']=metas_df['Realizado KG'].apply(lambda info: round((info/trabalhado)*util,2))

    metas_df['Meta %']=round(metas_df['Realizado KG']/metas_df['Meta KG'],4)*100

    metas_df['Projeção %']=round(metas_df['Projeção KG']/metas_df['Meta KG'],4)*100

    metas_df['Diário KG']=round(metas_df['Meta KG']/util,2)

    metas_df['Diário %']=round(metas_df['Total KG']/metas_df['Diário KG'],4)*100

    metas_df['Meta (-)']=metas_df['Realizado KG']-metas_df['Meta KG']

    metas_df['Diário (-)']=metas_df['Total KG']-metas_df['Diário KG']

    metas_df['Projeção (-)']=metas_df['Projeção KG']-metas_df['Meta KG']

    return metas_df

    pass

def Analise(tabelas):

    metas_df=Main(tabelas)

    #meta geral

    meta_geral=metas_df['Meta KG'].sum()

    total_geral=metas_df['Realizado KG'].sum()

    geral_perc=round(total_geral/meta_geral,4)*100

    dif_geral=total_geral-meta_geral

    #meta grupo varejo

    tipo='VAREJO'

    meta_varejo=metas_df['Meta KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    fat_varejo=metas_df['Faturado KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    total_varejo=metas_df['Total KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    aberto_varejo=metas_df['Aberto KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    real_varejo=metas_df['Realizado KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    proj_varejo=metas_df['Projeção KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    percmeta_varejo=metas_df['Meta %'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    percproj_varejo=metas_df['Projeção %'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    dia_varejo=metas_df['Diário KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    percdia_varejo=metas_df['Diário %'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    difmeta_varejo=metas_df['Meta (-)'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    difdia_varejo=metas_df['Diário (-)'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    difproc_varejo=metas_df['Projeção (-)'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    #meta grupo food

    tipo='FOOD'

    meta_food=metas_df['Meta KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    fat_food=metas_df['Faturado KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    total_food=metas_df['Total KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    aberto_food=metas_df['Aberto KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    real_food=metas_df['Realizado KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    proj_food=metas_df['Projeção KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    percmeta_food=metas_df['Meta %'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    percproj_food=metas_df['Projeção %'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    dia_food=metas_df['Diário KG'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    percdia_food=metas_df['Diário %'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    difmeta_food=metas_df['Meta (-)'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    difdia_food=metas_df['Diário (-)'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    difproc_food=metas_df['Projeção (-)'].loc[metas_df['Grupo MCCAIN'].str.contains(tipo)].sum()

    proj_geral=proj_varejo+proj_food
    
    dia_geral=total_food+total_varejo

    diameta_geral=dia_food+dia_varejo

    percproj_geral=percproj_varejo+percproj_food

    percdia_geral=round(dia_geral/diameta_geral,4)*100

    difdia_geral=difdia_food+difdia_varejo
    
    temp_dict=[{

        "Meta Geral KG" :float(meta_geral),
        "Total Geral KG" :float(total_geral),
        "Geral %" :float(geral_perc),
        "Á Realizar KG" :float(dif_geral),
        "Meta Varejo KG" :float(meta_varejo),
        "Faturamento Varejo KG" :float(fat_varejo),
        "Total Varejo KG" :float(total_varejo),
        "Aberto Varejo KG" :float(aberto_varejo),
        "Realizado Varejo KG" :float(real_varejo),
        "Projeção Varejo KG" :float(proj_varejo),
        "Meta Varejo %" :float(percmeta_varejo),
        "Projeção Varejo %" :float(percproj_varejo),
        "Diário Varejo" :float(dia_varejo),
        "Diário Varejo %" :float(percdia_varejo),
        "Meta Varejo (-)" :float(difmeta_varejo),
        "Diário Varejo (-)" :float(difdia_varejo),
        "Projeção Varejo (-)" :float(difproc_varejo),
        "Meta Food KG" :float(meta_food),
        "Faturamento Food KG" :float(fat_food),
        "Total Food KG" :float(total_food),
        "Aberto Food KG" :float(aberto_food),
        "Realizado Food KG" :float(real_food),
        "Projeção Food KG" :float(proj_food),
        "Meta Food %" :float(percmeta_food),
        "Projeção Food %" :float(percproj_food),
        "Diário Food" :float(dia_food),
        "Diário Food %" :float(percdia_food),
        "Meta Food (-)" :float(difmeta_food),
        "Diário Food (-)" :float(difdia_food),
        "Projeção Food (-)" :float(difproc_food),
        'Máximo':float(100),
        'Mínimo':float(0),
        'Projeção Geral KG':float(proj_geral),
        'Diário Geral KG':float(dia_geral),
        'Meta Diário KG':float(diameta_geral),
        'Projeção Geral %':float(percproj_geral),
        'Percentual Geral %':float(percdia_geral),
        'Á Realizar Diário KG':float(difdia_geral)

        }]

    requests.post(url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/7892abfa-8816-480a-8976-e1c4ca27ed13/rows?key=%2FZnSyfUtOCoNmfyQDkbzn7%2FJJzmEJrWQCI7rrJBtBWvWUAh53TjenLpqkAGrwK9WYHj8yjJsCku4cvlmv%2BgbWQ%3D%3D',json=temp_dict)

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Analise(tabelas)

    pass