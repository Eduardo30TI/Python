from Acesso import Login
from Query import Query
import pandas as pd
from datetime import datetime,timedelta
import os

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

pd.set_option('display.max_columns',None)

querys={
    
    'Vendas':
    
    """
    
    SELECT ped.[Data de Emissão],cli.[Data de Cadastro],
    CASE WHEN ped.[Data de Emissão]=cli.[Data de Cadastro] THEN 'S' ELSE 'N' END AS [Positivado],
    ped.Pedido,ped.[ID Cliente],cli.[Razão Social],cli.[Nome Fantasia],
    ped.[ID Vendedor],vend.[Nome Resumido],vend.DDD,vend.Telefone,sup.Equipe,
    sup.[ID Sup],sup.Supervisor,sup.[DDD Sup],sup.[Telefone Sup],
    sup.[ID Gerente],sup.Gerente,sup.[DDD Gerente],sup.[Telefone Gerente],
    SUM(ped.[Total Venda]) AS [Total Venda]
    FROM netfeira.vw_venda_estatico ped
    INNER JOIN netfeira.vw_cliente cli ON ped.[ID Cliente]=cli.[ID Cliente]
    INNER JOIN netfeira.vw_vendedor vend ON ped.[ID Vendedor]=vend.[ID Vendedor] --AND vend.Categoria='CLT'
    INNER JOIN netfeira.vw_supervisor sup ON vend.[ID Equipe]=sup.[ID Equipe]
    WHERE [Data de Emissão] BETWEEN DATEADD(DAY,1,
    DATEADD(DAY,DAY(DATEADD(DAY,DAY(GETDATE())*-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)))*-1,
    DATEADD(DAY,DAY(GETDATE())*-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)))) AND
    DATEADD(DAY,DAY(GETDATE())*-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101))
    AND [Tipo de Operação]='VENDAS'
    GROUP BY ped.[Data de Emissão],cli.[Data de Cadastro],ped.Pedido,ped.[ID Cliente],cli.[Razão Social],cli.[Nome Fantasia],
    ped.[ID Vendedor],vend.[Nome Resumido],vend.DDD,vend.Telefone,sup.Equipe,
    sup.[ID Sup],sup.Supervisor,sup.[DDD Sup],sup.[Telefone Sup],
    sup.[ID Gerente],sup.Gerente,sup.[DDD Gerente],sup.[Telefone Gerente]    
    
    """
}

def Main(df):

    df['Lista']=df['Vendas'].groupby(['ID Cliente'],as_index=False).agg({'Total Venda':'sum'})

    codigos=df['Lista'].loc[df['Lista']['Total Venda']>0,'ID Cliente'].unique().tolist()

    df['Consolidado']=df['Vendas'].loc[(df['Vendas']['ID Cliente'].isin(codigos))&(df['Vendas']['Positivado']=='S')].groupby(['ID Cliente', 'Razão Social', 'Nome Fantasia','Data de Cadastro', 'ID Vendedor',
        'Nome Resumido', 'DDD', 'Telefone', 'Equipe', 'ID Sup', 'Supervisor',
        'DDD Sup', 'Telefone Sup', 'ID Gerente', 'Gerente', 'DDD Gerente',
        'Telefone Gerente'],as_index=False).agg({'Total Venda':'sum'})

    df['Consolidado']['Data Mín']=df['Consolidado']['ID Cliente'].apply(lambda info: df['Vendas'].loc[df['Vendas']['ID Cliente']==info,'Data de Emissão'].min())

    df['Consolidado']['Pedido']=df['Consolidado']['ID Cliente'].apply(lambda info: df['Vendas'].loc[df['Vendas']['ID Cliente']==info,'Pedido'].min())

    df['Temp']=df['Consolidado'].groupby(['ID Vendedor',
        'Nome Resumido', 'DDD', 'Telefone', 'Equipe', 'ID Sup', 'Supervisor',
        'DDD Sup', 'Telefone Sup', 'ID Gerente', 'Gerente', 'DDD Gerente',
        'Telefone Gerente'],as_index=False).agg({'ID Cliente':'count'}).sort_values('ID Cliente',ascending=False)

    df['Temp'].rename(columns={'ID Cliente':'Cliente'},inplace=True)

    colunas={'ID Sup':'ID Gerente','ID Gerente':'ID Gerente'}

    nomes={'ID Sup':'Supervisor','ID Gerente':'Gerente'}

    tel_ddd={'ID Sup':'DDD Sup','ID Gerente':'DDD Gerente'}

    tel_num={'ID Sup':'Telefone Sup','ID Gerente':'Telefone Gerente'}

    meses={1:'JANEIRO',2:'FEVEREIRO',3:'MARÇO',4:'ABRIL',5:'MAIO',6:'JUNHO',7:'JULHO',8:'AGOSTO',9:'SETEMBRO',10:'OUTUBRO',11:'NOVEMBRO',12:'DEZEMBRO'}

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    for col1,col2 in colunas.items():
        
        codigos=df['Temp'][col1].unique().tolist()
        
        if(len(codigos)<=0):
            
            continue
        
        for c in codigos:
            
            temp_df=pd.DataFrame()
            
            cod=df['Temp'].loc[df['Temp'][col1]==c,col2].values[-1]
            
            if(cod==c and col1=='ID Sup'):
                
                continue        
            
            nome=str(df['Temp'].loc[df['Temp'][col1]==c,nomes[col1]].values[-1]).title()
            
            ddd=df['Temp'].loc[df['Temp'][col1]==c,tel_ddd[col1]].values[-1]
            
            telefone=df['Temp'].loc[df['Temp'][col1]==c,tel_num[col1]].values[-1]
            
            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'
            
            dt_ant=datetime.now()-timedelta(days=datetime.now().date().day)
            
            temp_df=df['Temp'].loc[df['Temp'][col1]==c]
            
            clientes=temp_df['Cliente'].sum()
                
            mensagem=f"""

            Abertura de Clientes
            
            {msg};
            
            {nome} identificamos referente ao mês de {str(meses[dt_ant.month]).title()} de {dt_ant.year}, um total de {clientes} cliente(s) novo(s) na base de dados da empresa.
            
            """

            sheets={'Temp':'Equipe','Consolidado':'Clientes'}

            writer=pd.ExcelWriter(f'{nome}.xlsx',engine='xlsxwriter')

            for key,value in sheets.items():

                df[key].loc[df[key][col1]==c].to_excel(writer,sheet_name=value,index=False,encoding='UTF-8')

                pass

            writer.close()

            temp_path=os.path.join(os.getcwd(),f'{nome}.xlsx')
            
            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,str(mensagem).strip(),temp_path]
        
            pass
        
        
        pass

    whatsapp_df.to_excel('whatsapp.xlsx',index=False,encoding='UTF-8')

    pass

if __name__=='__main__':

    df=sql.CriarTabela(kwargs=querys)

    Main(df)


    pass