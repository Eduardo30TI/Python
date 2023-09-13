from Acesso import Login
from Query import  Query
import pandas as pd
from datetime import datetime
import os

pd.set_option('display.max_columns',None)

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'Vendas':
    
    """
    
    DECLARE @DTBASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME,@DIAS SMALLINT

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS date),101)

    SET @DIAS=DAY(@DTBASE)

    SET @DTFIM=@DTBASE

    SET @DTINICIO=DATEADD(MONTH,-1,DATEADD(DAY,1,DATEADD(DAY,@DIAS*-1,@DTFIM)))

    SELECT * FROM netfeira.vw_venda_estatico
    WHERE [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM AND [Tipo de Operação]='VENDAS'
    ORDER BY [Data de Faturamento]  
    
    """,
    
    'Meta':
    
    """
    
    SELECT * FROM netfeira.vw_metas
    WHERE [Meta R$]>0
    
    """,
    
    'Vendedor':
    
    """

    SELECT v.[ID Vendedor],v.[Nome Resumido],s.Equipe,s.[ID Sup],s.Supervisor,s.[DDD Sup],s.[Telefone Sup],
    s.[ID Gerente],s.Gerente,s.[DDD Gerente],s.[Telefone Gerente]
    FROM netfeira.vw_vendedor v
    INNER JOIN netfeira.vw_supervisor s ON v.[ID Equipe]=s.[ID Equipe]
    WHERE v.[Status do Vendedor]='ATIVO'

    """,
    
    'Cliente':
    
    """
    
    SELECT * FROM netfeira.vw_cliente
    
    """,
    
    'Calendario':
    
    """
    
    DECLARE @DTBASE DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS date),101)

    SELECT COUNT(Data) AS [Útil],COUNT([Data Trabalhada])-1 AS [Trabalhado],COUNT(Data)-(COUNT([Data Trabalhada])-1) AS [Restante]
    FROM netfeira.vw_calend
    WHERE YEAR(Data)=YEAR(@DTBASE) AND MONTH(Data)=MONTH(@DTBASE) AND [Dia Útil]=1    

    """
    
}

def Main(df):

    dt_atu=datetime.now().date()

    dia_util=df['Calendario']['Útil'].values[-1]

    dia_trab=df['Calendario']['Trabalhado'].values[-1]

    dia_restante=df['Calendario']['Restante'].values[-1]

    #criar base de dados

    df['Temp']=df['Vendas'].loc[(df['Vendas']['Data de Faturamento'].dt.year==dt_atu.year)&(df['Vendas']['Data de Faturamento'].dt.month==dt_atu.month)]

    df['Temp']=df['Temp'].groupby(['ID Vendedor'],as_index=False).agg({'Total Venda':'sum'})

    df['Temp']=df['Temp'].merge(df['Meta'],on='ID Vendedor',how='inner')

    df['Temp']=df['Temp'].merge(df['Vendedor'],on='ID Vendedor',how='inner')

    df['Temp']=df['Temp'].groupby(['Equipe'],as_index=False).agg({'Total Venda':'sum','Meta R$':'sum'})

    df['Temp']['Projeção']=round((df['Temp']['Total Venda']/dia_trab)*dia_util,2)

    df['Temp']['Status']=df['Temp'].apply(lambda info: 1 if info['Projeção']>=info['Meta R$'] else 0,axis=1)

    df['Temp']=df['Temp'].loc[df['Temp']['Status']==0]

    equipes=df['Temp']['Equipe'].tolist()

    codigos=df['Vendedor']['ID Vendedor'].loc[df['Vendedor']['Equipe'].isin(equipes)].tolist()

    #consolidado dados

    df['Temp']=df['Vendas'].loc[(df['Vendas']['Data de Faturamento'].dt.year==dt_atu.year)&(df['Vendas']['Data de Faturamento'].dt.month==dt_atu.month)&(df['Vendas']['ID Vendedor'].isin(codigos))]

    df['Temp']=df['Temp'].groupby(['ID Vendedor'],as_index=False).agg({'Total Venda':'sum'})

    df['Temp']=df['Temp'].merge(df['Meta'],on='ID Vendedor',how='inner')

    df['Temp']=df['Temp'].merge(df['Vendedor'],on='ID Vendedor',how='inner')[['ID Vendedor', 'Nome Resumido', 'Equipe', 'ID Sup', 'Supervisor',
        'DDD Sup', 'Telefone Sup', 'ID Gerente', 'Gerente', 'DDD Gerente',
        'Telefone Gerente','Total Venda','Meta R$']]

    df['Temp']['Projeção']=round((df['Temp']['Total Venda']/dia_trab)*dia_util,2)

    df['Temp']['Status']=df['Temp'].apply(lambda info: 1 if info['Projeção']>=info['Meta R$'] else 0,axis=1)

    df['Temp']=df['Temp'].loc[df['Temp']['Status']==0]

    df['Temp'].sort_values('Total Venda',ascending=False,inplace=True)

    codigos=df['Temp']['ID Vendedor'].tolist()

    #Dados analisados

    valores=[]

    diferenca=[]

    for c in codigos:
        
        df['Diario']=df['Vendas'].loc[(df['Vendas']['Data de Faturamento'].dt.year==dt_atu.year)&(df['Vendas']['Data de Faturamento'].dt.month==dt_atu.month)&(df['Vendas']['ID Vendedor']==c)]
        
        meta=df['Temp']['Meta R$'].loc[df['Temp']['ID Vendedor']==c].values[-1]
        
        meta=round(meta/dia_util,2)
        
        df['Diario']=df['Diario'].groupby(['Data de Faturamento'],as_index=False).agg({'Total Venda':'sum'})
        
        df['Diario'].sort_values('Data de Faturamento',ascending=True,inplace=True)
        
        df['Diario']['Meta']=meta
        
        df['Diario']['Dif']=round(df['Diario']['Total Venda']-df['Diario']['Meta'],2)
            
        dif=df['Diario']['Dif'].sum()
        
        total=round(abs(dif)+meta if dif<0 else meta-dif,2)
        
        diferenca.append(dif)
        
        valores.append(total)
        
        pass

    df['Temp']['Meta Diária']=round(df['Temp']['Meta R$']/dia_util,2)

    df['Temp']['Débito Diário']=diferenca

    df['Temp']['Á Realizar']=valores

    df['Temp']['Á Realizar']=round(df['Temp']['Á Realizar']/dia_restante,2)

    df['Temp'].sort_values('Débito Diário',ascending=True,inplace=True,ignore_index=True)

    df['Temp'].loc[df['Temp']['Débito Diário']>0,'Meta Diária']=df['Temp'].loc[df['Temp']['Débito Diário']>0].apply(lambda info: round((info['Meta R$']-info['Total Venda'])/dia_restante,2),axis=1)

    df['Temp'].loc[df['Temp']['Débito Diário']>0,'Á Realizar']=df['Temp'].loc[df['Temp']['Débito Diário']>0,'Meta Diária']

    codigos=df['Temp']['ID Vendedor'].tolist()

    df['Vendas']['Mês']=df['Vendas']['Data de Faturamento'].dt.month

    #relação de clientes

    df['Lista']=df['Vendas'].loc[df['Vendas']['ID Vendedor'].isin(codigos)].groupby(['ID Cliente','ID Vendedor','Mês'],as_index=False).agg({'Total Venda':'sum'})

    df['Lista']=df['Lista'].pivot(index=['ID Cliente','ID Vendedor'],columns='Mês',values='Total Venda').reset_index()

    colunas=[l for l in df['Lista'].columns if str(l).isnumeric()]

    meses={1:'JAN',2:'FEV',3:'MAR',4:'ABR',5:'MAI',6:'JUN',7:'JUL',8:'AGOS',9:'SET',10:'OUT',11:'NOV',12:'DEZ'}

    for i,c in enumerate(colunas):
        
        if(i==0):
            
            df['Lista']=df['Lista'].loc[df['Lista'][c]>0]
            
            pass
        
        df['Lista'].loc[df['Lista'][c].isnull(),c]=0
        
        df['Lista'].rename(columns={c:meses[c]},inplace=True)
        
        pass

    df['Lista'].loc[df['Lista'][df['Lista'].columns[-1]]<=0,'Positivado']='N'

    df['Lista'].loc[df['Lista']['Positivado'].isnull(),'Positivado']='S'

    df['Lista']=df['Cliente'].merge(df['Lista'],on='ID Cliente',how='inner')

    df['Lista']=df['Vendedor'].merge(df['Lista'],on='ID Vendedor',how='inner')

    #arquivo whatsapp

    colunas={'ID Sup':'ID Gerente','ID Gerente':'ID Gerente'}

    nomes={'ID Sup':'Supervisor','ID Gerente':'Gerente'}

    tel_ddd={'ID Sup':'DDD Sup','ID Gerente':'DDD Gerente'}

    tel_num={'ID Sup':'Telefone Sup','ID Gerente':'Telefone Gerente'}

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    for col1,col2 in colunas.items():
        
        codigos=df['Temp'][col1].unique().tolist()

        if(len(codigos)<=0):

            continue
                
        for c in codigos:
            
            cod=df['Temp'][col2].loc[df['Temp'][col1]==c].unique().tolist()[-1]
            
            if(c==cod and col1=='ID Sup'):
                
                continue

            nome=str(df['Vendedor'].loc[df['Vendedor'][col1]==c,nomes[col1]].values[-1]).title()

            ddd=df['Vendedor'].loc[df['Vendedor'][col1]==c,tel_ddd[col1]].values[-1]

            telefone=df['Vendedor'].loc[df['Vendedor'][col1]==c,tel_num[col1]].values[-1]

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            mensagem=f"""
            
            {msg};

            {nome} tudo bem, estou te enviando a relação de vendedores que estão com a projeção abaixo da meta. Por favor analisar junto ao time. Lembrando que nessa relação em anexo tem os clientes que não compraram ainda este mês comparando com mês anterior.

            Atenciosamente BOT TI
            
            """
                                
            writer=pd.ExcelWriter(f'{nome}.xlsx',engine='xlsxwriter')

            sheets={'Lista':'Cliente','Temp':'Equipe'}
            
            for s in sheets.keys():

                temp_df=pd.DataFrame()

                temp_df=df[s].loc[df[s][col1]==c]

                temp_df.to_excel(writer,sheet_name=sheets[s],index=False)
                
                pass

            writer.close()

            temp_path=os.path.join(os.getcwd(),f'{nome}.xlsx')

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,str(mensagem).strip(),temp_path]
            
            pass
                
        pass

    if(len(df['Temp'])>0):

        whatsapp_df.to_excel('whatsapp.xlsx',index=False)

        pass

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass