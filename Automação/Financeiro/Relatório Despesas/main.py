from Acesso import Login
from Email import Email
from Moeda import Moeda
from RemoverArquivo import Remover
from Tempo import DataHora
import os
from glob import glob
from Query import Query
import pandas as pd

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={

    'Pagar':

    """

    DECLARE @DTBASE DATETIME,@DTINICIO DATETIME,@DTFIM DATETIME,@DIAS SMALLINT

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DIAS=DAY(@DTBASE)

    SET @DTFIM=DATEADD(DAY,@DIAS*-1,@DTBASE)

    SET @DTINICIO=DATEADD(DAY,(DAY(DATEADD(MM,-1,@DTFIM))-1)*-1,DATEADD(MM,-1,@DTFIM))

    SELECT *
    FROM netfeira.vw_contapagar
    WHERE [Data de Pagamento] BETWEEN @DTINICIO AND @DTFIM AND [ID Situação]='LQ'


    """,

    'Contas':

    """
    
    SELECT * FROM netfeira.vw_planocontas
    ORDER BY 1    
        
    """

}


def Main(tabelas_df):

    listagem=['CAIXA-CONSORCIO','FORNECEDORES','DISTRIBUICAO DE LUCRO','RECIFE','SALVADOR','BELEM','CAMBIO','CONSORCIO','LITORAL','NUMERARIO','PARANA']

    tabelas_df['Contas']['Plano de Contas']=tabelas_df['Contas']['Plano de Contas'].apply(lambda info: str(info).strip())

    tabelas_df['Contas']=tabelas_df['Contas'].loc[~tabelas_df['Contas']['Plano de Contas'].isin(listagem)]

    tabelas_df['Pagar']['Contas']=tabelas_df['Pagar']['Contas'].apply(lambda info: str(info).strip())

    tabelas_df['Pagar']=tabelas_df['Pagar'].loc[~tabelas_df['Pagar']['Contas'].isin(listagem)]

    tabelas_df['Pagar']['ID Mês']=tabelas_df['Pagar']['Data de Pagamento'].dt.month

    tabelas_df['Pagar']['Mês']=tabelas_df['Pagar']['ID Mês'].apply(data.Mes)

    pagos_df=pd.DataFrame()

    pagos_df=tabelas_df['Pagar']

    colunas=[l for l in pagos_df.columns.tolist() if l=='ID Conta']

    temp_df=pd.DataFrame()

    for coluna in colunas:
        
        df=pagos_df[[coluna,'ID Mês','Valor Pago R$']].groupby([coluna,'ID Mês'],as_index=False).sum()
        
        df.rename(columns={coluna:'ID Contas'},inplace=True)
        
        temp_df=pd.concat([temp_df,df],axis=0,ignore_index=True)
                
        #break
        
        pass

    temp_df.sort_values('ID Contas',ascending=True,inplace=True)

    temp_df['Mês']=temp_df['ID Mês'].apply(data.Mes)

    temp_df['Mês']=temp_df.apply(lambda info: str(info['ID Mês'])+' - '+info['Mês'],axis=1)

    if(temp_df['ID Mês'].max()==12):
        
        temp_df.sort_values('Mês',ascending=False,inplace=True)
        
        pass

    else:
        
        temp_df.sort_values('Mês',ascending=True,inplace=True)
        
        pass

    temp_df=temp_df[['ID Contas','Mês','Valor Pago R$']].pivot(index='ID Contas',columns='Mês',values='Valor Pago R$').reset_index()

    tabelas_df['Contas']=tabelas_df['Contas'].merge(temp_df,on='ID Contas',how='inner')

    tabelas_df['Contas'].loc[tabelas_df['Contas'].iloc[:,-1].isnull(),tabelas_df['Contas'].columns[-1]]=0

    tabelas_df['Contas'].loc[tabelas_df['Contas'].iloc[:,-2].isnull(),tabelas_df['Contas'].columns[-2]]=0

    tabelas_df['Contas'].loc[tabelas_df['Contas'].iloc[:,-1]==0,'Rep %']=0

    tabelas_df['Contas'].loc[tabelas_df['Contas'].iloc[:,-2]==0,'Rep %']=0

    tabelas_df['Contas'].loc[tabelas_df['Contas']['Rep %'].isnull(),'Rep %']=tabelas_df['Contas'].loc[tabelas_df['Contas']['Rep %'].isnull()].apply(lambda info: round((info[-2]/info[-3])-1,4)*100 if info[-2]>0 and info[-3]>0 else 0,axis=1)

    tabelas_df['Contas']['Diferença R$']=tabelas_df['Contas'].iloc[:,-2]-tabelas_df['Contas'].iloc[:,-3]

    tabelas_df['Contas'].loc[tabelas_df['Contas']['Rep %'].isnull(),'Rep %']=0

    tabelas_df['Contas'].to_excel('Plano de Contas.xlsx',index=False)

    Enviar()

    pass

def Enviar():

    data_atual=data.HoraAtual()

    hora=data_atual.hour
    
    id_ant=data_atual.month-2 if (data_atual.month-1)!=0 else 12

    id_atu=data_atual.month-1 if (data_atual.month-1)!=0 else 12

    mes_ant=data.Mes(id_ant)

    mes_atu=data.Mes(id_atu)

    ano=data_atual.year if (data_atual.month-1)!=0 else data_atual.year-1

    msg='Bom dia' if hora<12 else 'Boa tarde'

    assunto='Despesas Mês x Mês'

    nome='beatriz'

    temp_path=os.path.join(os.getcwd(),'*.xlsx')

    anexo=glob(temp_path)

    email_to=['beatriz@demarchibrasil.com.br']

    email_cc=[]

    mensagem=f"""
    
    <p>{msg};</p>

    <p>{str(nome).title()}</p>

    <p>Estou encaminhando o comparativo das despesas de {mes_ant.title()} com {mes_atu.title()}.</p>

    <P>Por favor não responder mensagem automática</P>

    <p>Atenciosamente</p>

    <p>BOT TI</p>    
    
    """

    temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

    Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

    Remover.RemoverArquivo('.xlsx')

    pass

if __name__=='__main__':

    data_atual=data.HoraAtual()
    
    dia=data_atual.day

    if(dia==1):

        tabelas_df=sql.CriarTabela(kwargs=querys)

        Main(tabelas_df)

        pass

    pass