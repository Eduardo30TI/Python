import pandas as pd
from Acesso import Login
from Query import Query
from datetime import datetime,timedelta
from Moeda import Moeda
from Email import Email
from RemoverArquivo import Remover
from Tempo import DataHora
from glob import glob
import os

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data_inicio=datetime.now()-timedelta(days=30)

data_atual=datetime.now()

querys={
    
    'Vendas':
    
    """
    
    SELECT * FROM netfeira.vw_targetestatistico
    
    """,
    
    'Estoque':
    
    """
    
    SELECT * FROM netfeira.vw_estoque
    WHERE Tipo='CENTRAL'    
    
    """
    
}

def Main(tabelas_df):

    vendas_df=pd.DataFrame()

    vendas_df=tabelas_df['Vendas']

    vendas_df=vendas_df.loc[(vendas_df['Tipo de Operação']!='OUTROS')&(vendas_df['ID Situação'].isin(['FA','AB']))]

    vendas_df=vendas_df.loc[vendas_df['Data de Emissão'].between(data_inicio,data_atual)]

    vendas_df=vendas_df[['SKU','Total Venda']].groupby(['SKU'],as_index=False).sum()

    codigos=vendas_df['SKU'].unique().tolist()

    estoque_df=pd.DataFrame()

    estoque_df=tabelas_df['Estoque']

    estoque_df=estoque_df.loc[(~estoque_df['SKU'].isin(codigos))&(estoque_df['Qtde Disponível']>0)]

    Analise(estoque_df)

    pass

def Analise(df):

    data=DataHora()

    data_now=data.HoraAtual()

    hora=data_now.hour

    total=Moeda.FormatarMoeda(df['Custo Total'].sum())

    mix=Moeda.Numero(len(df['SKU'].unique().tolist()))

    df.sort_values('Qtde Disponível',ascending=False,inplace=True)

    msg='Bom dia' if hora<12 else 'Boa tarde'

    assunto='Produtos sem venda'

    email_to=['edson.junior@demarchibrasil.com.br']

    email_cc=['julio@demarchibrasil.com.br','rogerio.felipim@demarchibrasil.com.br','compras@demarchibrasil.com.br','athos.alcantara@demarchisaopaulo.com.br']

    nome='Edson Almeida'

    mensagem=f"""
    
    <p>{msg};</p>

    <p>{str(nome).title()}</p>

    <p>Foram identificados cerca de {mix} itens que ainda não foram comercializados. Totalizando R$ {total}</p>

    <P>Por favor não responder mensagem automática</P>

    <p>Atenciosamente</p>

    <p>BOT TI</p>    
        
    """

    if(data_now.day==1):

        Remover.RemoverArquivo('.csv')

        pass

    temp_path=os.path.join(os.getcwd(),'*.csv')

    arq=glob(temp_path)

    if(len(arq)>0):

        temp_df=pd.read_csv(arq[-1],encoding='UTF-8')

        df['Contagem']=df['SKU'].apply(lambda info: len(temp_df['SKU'].loc[temp_df['SKU']==info].unique().tolist()))

        df=df.loc[df['Contagem']==0]

        df.drop(columns=['Contagem'],inplace=True)

        pass

    if(len(df)>0):
        
        df.to_excel('Produtos.xlsx',encoding='ISO-8859-1',index=False)

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        anexo=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

        Remover.RemoverArquivo('.xlsx')

        df=pd.concat([df,temp_df],axis=1,ignore_index=True)

        df.to_csv('Produtos.csv',encoding='UTF-8',index=False)
        
        pass

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass