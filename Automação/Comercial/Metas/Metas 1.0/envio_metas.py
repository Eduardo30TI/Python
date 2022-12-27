import pandas as pd
import pyodbc
import os
import win32com.client as win32
import datetime
import glob
import sched
import time

usuario='Netfeira'
senha='sqlserver'
driver='{SQL Server}'
database='MOINHO'
server='192.168.0.252'

str_conexao=(f'Driver={driver};Server={server};Database={database};UID={usuario};PWD={senha}')

ano_atual=datetime.datetime.now().year

mes_atual=datetime.datetime.now().month

dia_atual=datetime.datetime.now().day

hora_atual=datetime.datetime.now().hour

minuto_atual=datetime.datetime.now().minute

segundo_atual=datetime.datetime.now().second

dias_analise=120

querys={'Metas':"""

--Metas

WITH TabTpMeta(mes_ref,ano,mes,cd_prev_vda,cd_tp_prev,descricao) AS (

SELECT mes_ref,YEAR(mes_ref) AS  ano,MONTH(mes_ref) AS mes,cd_prev_vda,
tp_prev.cd_tp_prev,tp_prev.descricao
FROM prev_vda
INNER JOIN tp_prev ON prev_vda.cd_tp_prev=tp_prev.cd_tp_prev
WHERE tp_prev.descricao='VALOR'
)

SELECT ano AS 'Ano',mes AS 'ID Mês',it_prev_vda.cd_vend AS 'ID Vendedor',
valor AS 'Meta R$'
FROM it_prev_vda
INNER JOIN TabTpMeta ON TabTpMeta.cd_prev_vda=it_prev_vda.cd_prev_vda
INNER JOIN vendedor ON it_prev_vda.cd_vend=vendedor.cd_vend
AND TabTpMeta.cd_tp_prev=it_prev_vda.cd_tp_prev_det
WHERE ano=YEAR(GETDATE()) AND mes=MONTH(GETDATE())


""",'Vendas':
"""

WITH TabEvento (cd_emp,nu_ped,cd_clien,dt_criacao,cd_fila) AS (
SELECT cd_emp,nu_ped,cd_clien,CONVERT(DATETIME,CAST(dt_criacao AS date),101) AS dt_criacao,
cd_fila
FROM evento),

TabDatas (cd_emp,nu_ped,cd_clien,dt_ped,dt_fat) AS (

SELECT cd_emp,nu_ped,cd_clien,CAPV,FATU FROM (
SELECT cd_emp,nu_ped,cd_clien,dt_criacao,
fila.cd_fila
FROM TabEvento
INNER JOIN fila ON TabEvento.cd_fila=fila.cd_fila
AND fila.cd_fila IN('CAPV','FATU'))L
PIVOT(MAX(dt_criacao) FOR cd_fila IN ([CAPV],[FATU]))C
),

TabEmissao (cd_emp,nu_ped,cd_clien,dt_ped,dt_fat) AS (

SELECT cd_emp,nu_ped,cd_clien,dt_ped,
CASE WHEN dt_fat IS NULL THEN dt_ped ELSE dt_fat END AS dt_fat
FROM TabDatas),

TabItem (cd_emp,nu_ped,cd_prod,qtde,qtde_unid_vda,vl_unit_vda,vl_total,
peso_brt,peso_liq,situacao) AS (

SELECT it_pedv.cd_emp,nu_ped,it_pedv.cd_prod,qtde,qtde_unid_vda,vl_unit_vda,
ROUND(qtde_unid_vda*vl_unit_vda,2) AS vl_total,
qtde*peso_brt AS peso_brt,qtde*peso_liq AS peso_liq,
situacao
FROM it_pedv
INNER JOIN produto ON it_pedv.cd_prod=produto.cd_prod
WHERE NOT situacao IN ('CA','DV')
),

TabTipo (tp_ped,descricao,st_ped) AS (

SELECT tp_ped,descricao,
CASE WHEN bonificacao=1 THEN 'BONIFICAÇÃO' WHEN estat_com=1 
THEN 'VENDA' ELSE 'OUTROS' END AS st_ped
FROM tp_ped
WHERE bonificacao=1 OR estat_com=1
)

SELECT ped_vda.cd_emp AS 'ID Empresa',
ped_vda.nu_ped AS 'Pedido',cd_vend AS 'ID Vendedor',ped_vda.cd_clien AS 'ID Cliente',
TabEmissao.dt_ped AS 'Data do Pedido',TabEmissao.dt_fat AS 'Data do Faturamento',
TabItem.cd_prod AS 'SKU',qtde AS 'Qtde',qtde_unid_vda AS 'Qtde VDA',
vl_unit_vda AS 'Valor Unitário',vl_total AS 'Total do Pedido',
peso_brt AS 'Peso Bruto',peso_liq AS 'Peso Líquido',TabItem.situacao AS 'Situação'
FROM ped_vda
INNER JOIN TabTipo ON ped_vda.tp_ped=TabTipo.tp_ped
INNER JOIN TabEmissao ON ped_vda.nu_ped=TabEmissao.nu_ped
INNER JOIN TabItem ON ped_vda.nu_ped=TabItem.nu_ped
WHERE YEAR(TabEmissao.dt_fat)=YEAR(GETDATE())
AND MONTH(TabEmissao.dt_fat)=MONTH(GETDATE())
ORDER BY [Pedido]
        
""",'Feriado':
"""

DECLARE @DateInicial AS DATETIME,@DateFinal AS DATETIME

SET @DateInicial='2018-01-01'
SET @DateFinal=CONCAT(YEAR(GETDATE())+1,'-01-01')

;WITH TabDatas(dt_calend) AS (
SELECT @DateInicial
UNION ALL
SELECT dt_calend+1 FROM TabDatas WHERE dt_calend+1<@DateFinal),

TabCalendario (dt_calend,mes_base) AS(

SELECT CONVERT(DATETIME,CAST(dt_calend AS DATE),101),CONVERT(VARCHAR,DAY(dt_calend))+'/'+CONVERT(VARCHAR,MONTH(dt_calend)) AS mes_base
FROM TabDatas 
),

TabFeriado (dt_calend,mes_base,dias_feriado) AS (

SELECT dt_calend,mes_base,
CASE WHEN mes_base IN ('1/1','10/4','21/4','1/5','11/6','7/9','12/10','2/11','15/11','25/12','8/4') THEN 0 ELSE 1 END 
FROM TabCalendario)

SELECT DISTINCT mes_base AS 'Mês Base'
FROM TabFeriado
WHERE dias_feriado=0
ORDER BY 1
OPTION(MAXRECURSION 10000)

""",'Datas':
"""

DECLARE @DTInicial AS DATETIME,@DTFinal AS DATETIME

SET @DTInicial='2018-01-01'
SET @DTFinal= CONCAT(YEAR(GETDATE())+1,'-01-','01')

;WITH Calendario (Datas) AS(

SELECT @DTInicial
UNION ALL
SELECT Datas+1
FROM Calendario WHERE  Datas+1<@DTFinal
)

SELECT CONVERT(DATETIME,CAST(Datas AS DATE),101) AS 'Data',YEAR(Datas) AS 'Ano',MONTH(Datas) AS 'Cód. Mês',
CHOOSE(MONTH(Datas),'JANEIRO','FEVEREIRO','MARÇO','ABRIL','MAIO','JUNHO','JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO') AS 'Mês',
CHOOSE(MONTH(Datas),'JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ') AS 'Mês Resumido',
DAY(Datas) AS 'Dia',CONVERT(VARCHAR(7),Datas,120) AS 'Mês Meta',
DATEPART(DW,Datas) AS 'Cód. Semana',CHOOSE(DATEPART(DW,Datas),'DOM','SEG','TER','QUAR','QUI','SEX','SÁB') AS 'Semana',
CASE WHEN DATEPART(DW,Datas) IN (7,1) THEN 0 ELSE 1 END AS 'Dias Úteis',
CASE WHEN MONTH(Datas)<=3 THEN '1º TRIM' WHEN MONTH(Datas)<=6 THEN '2º TRIM' WHEN MONTH(Datas)<=9 THEN '3º TRIM' WHEN MONTH(Datas)<=12 THEN '4º TRIM' END AS 'Trimestre Ano',
CASE WHEN MONTH(Datas)<=6 THEN '1º SEM' ELSE '2º SEM' END AS 'Semestre Ano',DATEPART(WEEK,Datas) AS 'Semana Ano',
CONVERT(VARCHAR,DAY(Datas))+'/'+CONVERT(VARCHAR,MONTH(Datas)) AS 'Mês Base'
FROM Calendario OPTION(MAXRECURSION 10000)

""",'Vendedores':
"""

WITH TabSupervisor (cd_equipe,descricao,nome_resumido) AS (

SELECT equipe.cd_equipe,descricao,
CASE WHEN CHARINDEX(' ',LTRIM(RTRIM(nome)))=0 THEN nome ELSE
RTRIM(LEFT(nome,(CHARINDEX(' ',LTRIM(RTRIM(nome)))))) + ' ' + 
LTRIM(RIGHT(nome,(CHARINDEX(' ',REVERSE(LTRIM(RTRIM(nome))))))) END AS nome_resumido
FROM equipe
INNER JOIN vendedor ON equipe.cd_vend_sup=vendedor.cd_vend
WHERE equipe.ativo=1
)

SELECT cd_vend AS 'ID Vendedor',nome_gue AS 'Vendedor',
--categ.descricao AS 'Categoria',
TabSupervisor.descricao AS 'Equipe',
CASE WHEN TabSupervisor.descricao='EQUIPE 9 (ATIVO)' THEN 'PEDIDOS'
WHEN TabSupervisor.nome_resumido='JULIO DELFINO' THEN 'ROGERIO FELIPIM' ELSE
TabSupervisor.nome_resumido END AS 'Supervisor'
FROM vendedor
INNER JOIN categ ON vendedor.categ=categ.categ
INNER JOIN TabSupervisor ON vendedor.cd_equipe=TabSupervisor.cd_equipe
WHERE vendedor.ativo=1

""",'Carteira':
"""

SELECT vend_cli.cd_vend AS 'ID Vendedor',vend_cli.cd_clien AS 'ID Cliente'
FROM vend_cli
INNER JOIN cliente ON vend_cli.cd_clien=cliente.cd_clien AND cliente.ativo=1

""",'Vendas_Cliente':
"""

WITH TabEvento (cd_emp,nu_ped,cd_clien,dt_criacao,cd_fila) AS (
SELECT cd_emp,nu_ped,cd_clien,CONVERT(DATETIME,CAST(dt_criacao AS date),101) AS dt_criacao,
cd_fila
FROM evento),

TabDatas (cd_emp,nu_ped,cd_clien,dt_ped,dt_fat) AS (

SELECT cd_emp,nu_ped,cd_clien,CAPV,FATU FROM (
SELECT cd_emp,nu_ped,cd_clien,dt_criacao,
fila.cd_fila
FROM TabEvento
INNER JOIN fila ON TabEvento.cd_fila=fila.cd_fila
AND fila.cd_fila IN('CAPV','FATU'))L
PIVOT(MAX(dt_criacao) FOR cd_fila IN ([CAPV],[FATU]))C
),

TabEmissao (cd_emp,nu_ped,cd_clien,dt_ped,dt_fat) AS (

SELECT cd_emp,nu_ped,cd_clien,dt_ped,
CASE WHEN dt_fat IS NULL THEN dt_ped ELSE dt_fat END AS dt_fat
FROM TabDatas),

TabItem (cd_emp,nu_ped,cd_prod,qtde,qtde_unid_vda,vl_unit_vda,vl_total,
peso_brt,peso_liq,situacao) AS (

SELECT it_pedv.cd_emp,nu_ped,it_pedv.cd_prod,qtde,qtde_unid_vda,vl_unit_vda,
ROUND(qtde_unid_vda*vl_unit_vda,2) AS vl_total,
qtde*peso_brt AS peso_brt,qtde*peso_liq AS peso_liq,
situacao
FROM it_pedv
INNER JOIN produto ON it_pedv.cd_prod=produto.cd_prod
WHERE NOT situacao IN ('CA','DV')
),

TabTipo (tp_ped,descricao,st_ped) AS (

SELECT tp_ped,descricao,
CASE WHEN bonificacao=1 THEN 'BONIFICAÇÃO' WHEN estat_com=1 
THEN 'VENDA' ELSE 'OUTROS' END AS st_ped
FROM tp_ped
WHERE bonificacao=1 OR estat_com=1
),

TabCarteira (cd_clien,cd_vend,prioritario,cd_equipe) AS (

SELECT cd_clien,vend_cli.cd_vend,prioritario,vendedor.cd_equipe
FROM vend_cli
INNER JOIN vendedor ON vend_cli.cd_vend=vendedor.cd_vend
),

TabPedido (cd_emp,tp_ped,nu_ped,cd_clien,cd_vend,cd_equipe) AS (

SELECT ped_vda.cd_emp,tp_ped,nu_ped,ped_vda.cd_clien,ped_vda.cd_vend,
vendedor.cd_equipe
FROM ped_vda
INNER JOIN vendedor ON ped_vda.cd_vend=vendedor.cd_vend
),

TabVendCad (cd_emp,tp_ped,nu_ped,cd_clien,cd_vend,cd_equipe,vend_cad) AS (

SELECT cd_emp,tp_ped,nu_ped,cd_clien,cd_vend,cd_equipe,
CASE WHEN (
CASE WHEN (
(SELECT MAX(Tab01.cd_vend) FROM TabCarteira AS Tab01
WHERE Tab01.cd_clien=TabPedido.cd_clien AND Tab01.cd_vend=TabPedido.cd_vend
AND Tab01.cd_equipe=TabPedido.cd_equipe)) IS NOT NULL THEN
(SELECT MAX(Tab01.cd_vend) FROM TabCarteira AS Tab01
WHERE Tab01.cd_clien=TabPedido.cd_clien AND Tab01.cd_vend=TabPedido.cd_vend
AND Tab01.cd_equipe=TabPedido.cd_equipe) ELSE
(SELECT MAX(Tab01.cd_vend) FROM TabCarteira AS Tab01
WHERE Tab01.cd_clien=TabPedido.cd_clien AND Tab01.cd_equipe=TabPedido.cd_equipe)
END) IS NOT NULL THEN
CASE WHEN (
(SELECT MAX(Tab01.cd_vend) FROM TabCarteira AS Tab01
WHERE Tab01.cd_clien=TabPedido.cd_clien AND Tab01.cd_vend=TabPedido.cd_vend
AND Tab01.cd_equipe=TabPedido.cd_equipe)) IS NOT NULL THEN
(SELECT MAX(Tab01.cd_vend) FROM TabCarteira AS Tab01
WHERE Tab01.cd_clien=TabPedido.cd_clien AND Tab01.cd_vend=TabPedido.cd_vend
AND Tab01.cd_equipe=TabPedido.cd_equipe) ELSE
(SELECT MAX(Tab01.cd_vend) FROM TabCarteira AS Tab01
WHERE Tab01.cd_clien=TabPedido.cd_clien AND Tab01.cd_equipe=TabPedido.cd_equipe)
END ELSE
(SELECT MAX(Tab01.cd_vend) FROM TabCarteira AS Tab01
WHERE Tab01.cd_clien=TabPedido.cd_clien AND Tab01.prioritario=1) END
AS vend_cad
FROM TabPedido
)

SELECT TabVendCad.cd_emp AS 'ID Empresa',
TabVendCad.nu_ped AS 'Pedido',vend_cad AS 'ID Vendedor',TabVendCad.cd_clien AS 'ID Cliente',
TabEmissao.dt_ped AS 'Data do Pedido',TabEmissao.dt_fat AS 'Data do Faturamento',
TabItem.cd_prod AS 'SKU',qtde AS 'Qtde',qtde_unid_vda AS 'Qtde VDA',
vl_unit_vda AS 'Valor Unitário',vl_total AS 'Total do Pedido',
peso_brt AS 'Peso Bruto',peso_liq AS 'Peso Líquido',TabItem.situacao AS 'Situação'
FROM TabVendCad
INNER JOIN TabTipo ON TabVendCad.tp_ped=TabTipo.tp_ped
INNER JOIN TabEmissao ON TabVendCad.nu_ped=TabEmissao.nu_ped
INNER JOIN TabItem ON TabVendCad.nu_ped=TabItem.nu_ped
ORDER BY [Pedido]

""",'Cliente':
"""

WITH TabLista (cd_clien,ce,co) AS (

SELECT * FROM (
SELECT cd_clien,tp_tel
FROM tel_cli
WHERE tp_tel IN ('CE','CO')
)L
PIVOT(COUNT(tp_tel) FOR tp_tel IN ([CE],[CO]))C),

TabListaContato (cd_clien,tp_tel) AS (

SELECT cd_clien,
CASE WHEN (ce=co) OR (ce>co) then 'CE' WHEN ce<co THEN 'CO'
END AS tp_tel
FROM TabLista),

TabContato (cd_clien,ddd,numero) AS (

SELECT TabListaContato.cd_clien,ddd,numero
FROM TabListaContato
INNER JOIN tel_cli ON TabListaContato.cd_clien=tel_cli.cd_clien
AND TabListaContato.tp_tel=tel_cli.tp_tel and tel_cli.seq=1)

SELECT cliente.cd_clien AS 'ID Cliente',nome_res AS 'Nome Fantasia',cgc_cpf AS 'CNPJ',
CASE WHEN LEN(cgc_cpf)=14 THEN 'CNPJ' ELSE 'CPF' END AS 'Tipo de Cliente',
ddd AS 'DDD',CONVERT(VARCHAR,numero) AS 'Número'
FROM cliente
LEFT JOIN TabContato ON cliente.cd_clien=TabContato.cd_clien
WHERE ativo=1

"""
}

def ConexaoSQL():
    
    try:
        
        conecta=pyodbc.connect(str_conexao)
        
        return conecta
        
        pass
    
    except Exception as erro:
        
        print('Erro: {0}'.format(erro))
        
        pass
    
    pass

def GetDias():

    conectando=ConexaoSQL()
   
    feriado_df=pd.read_sql(querys['Feriado'],conectando)

    calend_df=pd.read_sql(querys['Datas'],conectando)
    
    calend_df['Base']=calend_df.apply(lambda x: feriado_df.loc[feriado_df['Mês Base']==x['Mês Base']].count(),axis=1)

    calend_df['Dias Úteis']=calend_df[['Dias Úteis','Base']].apply(lambda x: 0 if x['Base']==x['Dias Úteis'] else x['Dias Úteis'],axis=1)

    calend_df.drop(columns=['Base'],inplace=True)
    
    contagem=calend_df['Dias Úteis'].loc[(calend_df['Ano']==ano_atual)&(calend_df['Cód. Mês']==mes_atual)].sum()
    
    return contagem

    pass

def GetTrabalhados(dia):

    conectando=ConexaoSQL()
   
    feriado_df=pd.read_sql(querys['Feriado'],conectando)

    calend_df=pd.read_sql(querys['Datas'],conectando)
    
    calend_df['Base']=calend_df.apply(lambda x: feriado_df.loc[feriado_df['Mês Base']==x['Mês Base']].count(),axis=1)

    calend_df['Dias Úteis']=calend_df[['Dias Úteis','Base']].apply(lambda x: 0 if x['Base']==x['Dias Úteis'] else x['Dias Úteis'],axis=1)

    calend_df.drop(columns=['Base'],inplace=True)
    
    contagem=calend_df['Dias Úteis'].loc[(calend_df['Ano']==ano_atual)&(calend_df['Cód. Mês']==mes_atual)&(calend_df['Dia'].between(1,dia))].sum()
    
    return contagem

    pass

def MetaDiaria(valor):

    util=GetDias()

    return round(valor/util,2)

    pass

def Tempo(hora,minuto,segundo):

    hora=str(hora)

    minuto=str(minuto)

    segundo=str(segundo)

    if(len(hora)==1):

        hora=(f'0{hora}')

        pass

    if(len(minuto)==1):

        minuto=(f'0{minuto}')

        pass

    if(len(segundo)==1):

        segundo=(f'0{segundo}')

        pass

    temp_hora=(f'{hora}:{minuto}:{segundo}')

    return temp_hora

    pass

def Projecao(valor):

    util=GetDias()

    trab=GetTrabalhados(dia_atual)

    horario=Tempo(hora_atual,minuto_atual,segundo_atual)

    if(horario!='17:30:00'):

        trab=trab-1

        pass

    projecao=(valor/trab)*util

    return round(projecao,2)

    pass

def RelatorioVendas():

    conectando=ConexaoSQL()

    metas_df=pd.read_sql(querys['Metas'],conectando)

    vendas_df=pd.read_sql(querys['Vendas'],conectando)

    vendedor_df=pd.read_sql(querys['Vendedores'],conectando)

    carteira_df=pd.read_sql(querys['Carteira'],conectando)

    vendas_df['Ano']=vendas_df['Data do Faturamento'].dt.year

    vendas_df['ID Mês']=vendas_df['Data do Faturamento'].dt.month

    vendas_df['Dia']=vendas_df['Data do Faturamento'].dt.day

    vendedor_df['Meta R$']=vendedor_df.apply(lambda info: metas_df['Meta R$'].loc[metas_df['ID Vendedor']==info['ID Vendedor']].sum(),axis=1)

    vendedor_df['Venda R$']=vendedor_df.apply(lambda info: vendas_df['Total do Pedido'].loc[(vendas_df['ID Vendedor']==info['ID Vendedor'])&(vendas_df['Situação']=='FA')].sum(),axis=1)

    vendedor_df['Meta %']=vendedor_df.apply(lambda info: round(info['Venda R$']/info['Meta R$'],4)*100 if info['Venda R$']!=0 and info['Meta R$']!=0 else 0,axis=1)

    vendedor_df['Diferença R$']=vendedor_df.apply(lambda info: round(info['Venda R$']-info['Meta R$'],2),axis=1)

    vendedor_df['Projeção R$']=vendedor_df['Venda R$'].apply(Projecao)

    vendedor_df['Meta Diária R$']=vendedor_df['Meta R$'].apply(MetaDiaria)

    vendedor_df['Realizado R$']=vendedor_df.apply(lambda info: vendas_df['Total do Pedido'].loc[(vendas_df['ID Vendedor']==info['ID Vendedor'])&(vendas_df['Situação']=='AB')&(vendas_df['Dia']==dia_atual)].sum(),axis=1)

    vendedor_df['Meta Diária %']=vendedor_df.apply(lambda info: round(info['Realizado R$']/info['Meta Diária R$'],4)*100 if info['Realizado R$']!=0 and info['Meta Diária R$']!=0 else 0,axis=1)

    vendedor_df['Dif. Diária R$']=vendedor_df.apply(lambda info: round(info['Realizado R$']-info['Meta Diária R$'],2),axis=1)

    vendedor_df['Pedido Realizado']=vendedor_df.apply(lambda info: len(vendas_df['Pedido'].loc[(vendas_df['ID Vendedor']==info['ID Vendedor'])&(vendas_df['Dia']==dia_atual)&(vendas_df['Situação']=='AB')].unique().tolist()),axis=1)

    vendedor_df['Atendimento Realizado']=vendedor_df.apply(lambda info: len(vendas_df['ID Cliente'].loc[(vendas_df['ID Vendedor']==info['ID Vendedor'])&(vendas_df['Dia']==dia_atual)&(vendas_df['Situação']=='AB')].unique().tolist()),axis=1)    
        
    return vendedor_df

    pass

def RelatorioCliente():

    conectando=ConexaoSQL()

    temp_df=pd.DataFrame()

    vda_df=pd.DataFrame()

    vendas_df=pd.read_sql(querys['Vendas_Cliente'],conectando)

    cliente_df=pd.read_sql(querys['Cliente'],conectando)

    vendedor_df=pd.read_sql(querys['Vendedores'],conectando)

    vendas_df['Ano']=vendas_df['Data do Faturamento'].dt.year

    vendas_df['ID Mês']=vendas_df['Data do Faturamento'].dt.month

    vendas_df['Dia']=vendas_df['Data do Faturamento'].dt.day

    data_max=vendas_df['Data do Faturamento'].loc[(vendas_df['Ano']==ano_atual)&~(vendas_df['ID Mês']==mes_atual)].max()

    data_min=data_max-datetime.timedelta(days=dias_analise)

    temp_df=vendas_df[['ID Cliente','ID Vendedor','Total do Pedido']].loc[vendas_df['Data do Faturamento'].between(data_min,data_max)].groupby(['ID Cliente','ID Vendedor']).sum(['Total do Pedido']).reset_index()

    vda_df=vendas_df[['ID Cliente','ID Vendedor','Total do Pedido']].loc[(vendas_df['Ano']==ano_atual)&(vendas_df['ID Mês']==mes_atual)].groupby(['ID Cliente','ID Vendedor']).sum().reset_index()

    temp_df['Realizado R$']=temp_df.apply(lambda info: vda_df['Total do Pedido'].loc[(vda_df['ID Cliente']==info['ID Cliente'])&(vda_df['ID Vendedor']==info['ID Vendedor'])].sum(),axis=1)

    temp_df['Status']=temp_df.apply(lambda info: 'SEM COMPRA' if info['Realizado R$']==0 else 'COMPROU',axis=1)

    temp_df=temp_df.loc[temp_df['Status']=='SEM COMPRA']

    dados_df=cliente_df.merge(temp_df,on='ID Cliente',how='inner')

    info_df=dados_df.merge(vendedor_df,on='ID Vendedor',how='inner')

    info_df=info_df[['ID Cliente', 'Nome Fantasia', 'CNPJ', 'Tipo de Cliente', 'DDD','Número','ID Vendedor','Vendedor', 'Equipe', 'Supervisor','Total do Pedido', 'Realizado R$', 'Status']]

    return info_df

    pass

def EnviarEmail(corpo,email_dest,email_cc,assunto):

    olApp = win32.Dispatch('Outlook.Application')
    olNS = olApp.GetNameSpace('MAPI')

    envio_destino=[email_dest]

    copia_email=[email_cc]

    # construct email item object
    mailItem = olApp.CreateItem(0)
    mailItem.Subject = assunto
    mailItem.BodyFormat = 1
    #mailItem.Body = corpo
    mailItem.HTMLBody=corpo
    mailItem.To = ';'.join(env for env in envio_destino)
    mailItem.Cc=';'.join(env for env in copia_email)
    mailItem.Sensitivity  = 2

    arquivo=[os.path.join(os.getcwd(),arq) for arq in glob.glob('*.xlsx') if arq.find('E-mail')]
    
    for anexo in arquivo:
    
        mailItem.Attachments.Add(anexo)
        
        pass
    #optional (account you want to use to send the email)
    #mailItem._oleobj_.Invoke(*(64209, 0, 8, 0, olNS.Accounts.Item('<email@gmail.com')))
    #mailItem.Display()
    #mailItem.Save()
    mailItem.Send()

    RemoverArquivo()

    pass

def CorpoEmail():

    vendas_df=RelatorioVendas()

    cliente_df=RelatorioCliente()

    for path,dir,arq in os.walk(os.getcwd()):

        for arquivo in arq:

            if(arquivo.find('E-mail')<0):

                continue

            temp_path=os.path.join(path,arquivo)

            lista_email=pd.read_excel(temp_path)

            pass

        pass

    supervisores=lista_email['Supervisor'].tolist()
    
    for sup in supervisores:
        
        nome=str(sup)

        total=vendas_df['Venda R$'].loc[vendas_df['Supervisor']==sup].sum()

        meta=vendas_df['Meta R$'].loc[vendas_df['Supervisor']==sup].sum()

        projecao=vendas_df['Projeção R$'].loc[vendas_df['Supervisor']==sup].sum()

        comprou=len(cliente_df['ID Cliente'].loc[(cliente_df['Supervisor']==sup)&(cliente_df['Status']=='COMPROU')&(cliente_df['Tipo de Cliente']=='CNPJ')].unique().tolist())

        sem_compra=len(cliente_df['ID Cliente'].loc[(cliente_df['Supervisor']==sup)&(cliente_df['Status']=='SEM COMPRA')&(cliente_df['Tipo de Cliente']=='CNPJ')].unique().tolist())

        percentual=round(total/meta,4)*100

        total=FormatarMoeda(total)

        meta=FormatarMoeda(meta)

        projecao=FormatarMoeda(projecao)

        mensagem=f"""
        
        <p>Bom dia</p>

        <p>{nome.title()}</p>

        <p>Estou te encaminhando o resultado das vendas de hoje juntamente com as metas. De acordo com seu desempenho você tem faturado {total} e já atingiu de uma meta de {meta} cerca de {percentual}%, você tem projetado {projecao}. Além das metas e o realizado em anexo estou te mandando os clientes sem compra a {dias_analise} dias para que você possa ter um bom desempenho identificamos que você já atendeu dessa relação {comprou} clientes ficando pendente {sem_compra}.</p>

        <p>Essa mensagem é enviada de forma automática não é para responder</p>

        <p>Atenciosamente</p>
        
        """
        
        cargo=lista_email['Status'].loc[(lista_email['Supervisor']==sup)].tolist()

        email_to=lista_email['EMAIL'].loc[(lista_email['Supervisor']==sup)].tolist()

        email_to=email_to[0]

        if(str(cargo[0]).upper()=='SUPERVISOR'):

            email_cc=lista_email['EMAIL'].loc[(lista_email['Status']=='GERENTE')].tolist()

            email_cc=email_cc[0]

            pass

        else:

            email_cc=''

            pass

        vendas_df[vendas_df['Supervisor']==sup].to_excel('Vendas.xlsx',index=False,encoding='ISO-8859-1')

        cliente_df[cliente_df['Supervisor']==sup].to_excel('Clientes sem compra.xlsx',index=False,encoding='ISO-8859-1')

        EnviarEmail(mensagem,email_to,email_cc,'Relatório de Vendas')

        print('E-mail enviado com sucesso!')

        #break
        
        pass

    EmailGeral(vendas_df,cliente_df)

    pass

def EmailGeral(vd_df,cli_df):

    vendas_df=vd_df

    cliente_df=cli_df

    for path,dir,arq in os.walk(os.getcwd()):

        for arquivo in arq:

            if(arquivo.find('E-mail')<0):

                continue

            temp_path=os.path.join(path,arquivo)

            lista_email=pd.read_excel(temp_path,sheet_name='Geral')

            pass

        pass

    supervisores=lista_email['Supervisor'].tolist()
    
    for sup in supervisores:
        
        nome=str(sup)

        total=vendas_df['Venda R$'].sum()

        meta=vendas_df['Meta R$'].sum()

        projecao=vendas_df['Projeção R$'].sum()

        comprou=len(cliente_df['ID Cliente'].loc[(cliente_df['Status']=='COMPROU')&(cliente_df['Tipo de Cliente']=='CNPJ')].unique().tolist())

        sem_compra=len(cliente_df['ID Cliente'].loc[(cliente_df['Status']=='SEM COMPRA')&(cliente_df['Tipo de Cliente']=='CNPJ')].unique().tolist())

        percentual=round(total/meta,4)*100

        total=FormatarMoeda(total)

        meta=FormatarMoeda(meta)

        projecao=FormatarMoeda(projecao)

        mensagem=f"""
        
        <p>Bom dia</p>

        <p>{nome.title()}</p>

        <p>Estou te encaminhando o resultado das vendas de hoje juntamente com as metas. De acordo com seu desempenho você tem faturado {total} e já atingiu de uma meta de {meta} cerca de {percentual:2f}%, você tem projetado {projecao}. Além das metas e o realizado em anexo estou te mandando os clientes sem compra a {dias_analise} dias para que você possa ter um bom desempenho identificamos que você já atendeu dessa relação {comprou} clientes ficando pendente {sem_compra}.</p>

        <p>Essa mensagem é enviada de forma automática não é para responder</p>

        <p>Atenciosamente</p>
        
        """
        
        email_to=lista_email['EMAIL'].loc[lista_email['Supervisor']==sup].tolist()

        email_to=email_to[0]

        email_cc=''

        vendas_df.to_excel('Vendas.xlsx',index=False,encoding='ISO-8859-1')

        cliente_df.to_excel('Clientes sem compra.xlsx',index=False,encoding='ISO-8859-1')

        EnviarEmail(mensagem,email_to,email_cc,'Relatório de Vendas')

        #break
        
        pass

    pass

def FormatarMoeda(valor):
    
    valor=str(valor)
    
    inteiro=valor[:valor.find('.')]
    
    decimal=valor[valor.find('.'):]
    
    decimal=decimal[1:]
    
    if(len(decimal)==1):
        
        decimal=(f'0{decimal}')
        
        pass
    
    else:
        
        decimal=decimal[:2]
        
        pass
    
    moeda=('R$ {0},{1}'.format(inteiro,decimal))
    
    return moeda
    
    pass

def RemoverArquivo():

    for path,dir,arq in os.walk(os.getcwd()):

        for arquivo in arq:

            if(arquivo.find('.xlsx')<0 or not arquivo.find('E-mail')<0):

                continue
            
            temp_path=os.path.join(path,arquivo)

            os.remove(temp_path)

            pass

        pass

    pass

if __name__=='__main__':

    horas=Tempo(hora_atual,minuto_atual,segundo_atual)

    executador=sched.scheduler(time.time,time.sleep)

    if(horas=='07:00:03' or horas=='18:00:13'):

        executador.enter(1,0,CorpoEmail)
        executador.run()

        pass

    pass