from email.mime import base
import pandas as pd
from Acesso import Login
from Query import Query
from Email import Email
from Moeda import Moeda
from RemoverArquivo import Remover
import os
from glob import glob
from Tempo import DataHora

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={

    'Alerta':

    """

    SELECT * FROM netfeira.vw_alertastk
    
    """,

    'Vendedor':

    """
    
    SELECT * FROM netfeira.vw_vendedor
    WHERE [Status do Vendedor]='ATIVO' AND [E-mail]<>'' AND Categoria IN('PJ','CLT')    
        
    """

}


def Main(tabela_df):

    base_df=pd.DataFrame()

    temp_df=pd.DataFrame()

    consolidado=pd.DataFrame()

    base_df=tabela_df['Alerta'][['SKU', 'Produto', 'Fabricante','Departamento', 'Seção', 'Categoria', 'Linha','Qtde Saldo','Alerta']].loc[tabela_df['Alerta']['Alerta']!='OK']

    temp_path=os.path.join(os.getcwd(),'*.csv')

    arquivos=glob(temp_path)

    if(len(arquivos)==0):

        base_df.to_excel('Estoque.xlsx',index=False)

        temp_df=base_df[['SKU','Alerta']]

        temp_df.rename(columns={'Alerta':'Histórico'},inplace=True)

        temp_df.to_csv('Memoria.csv',index=False,encoding='ISO-8859-1')

        pass

    else:

        temp_df=pd.read_csv(arquivos[-1],encoding='ISO-8859-1')

        base_df=base_df.merge(temp_df,on='SKU',how='left')

        base_df['Status']=base_df.apply(lambda info: 'OK' if info['Alerta']==info['Histórico'] else 'ALERTA',axis=1)

        base_df=base_df.loc[base_df['Status']!='OK']

        df=base_df[['SKU','Alerta']]

        prod=df['SKU'].unique().tolist()

        temp_df=temp_df.loc[~temp_df['SKU'].isin(prod)]

        df.rename(columns={'Alerta':'Histórico'},inplace=True)
        
        consolidado_df=pd.concat([df,temp_df],axis=0,ignore_index=True)

        consolidado_df.to_csv('Memoria.csv',index=False,encoding='ISO-8859-1')

        pass

    if(len(base_df)>0):

        base_df[['SKU', 'Produto', 'Fabricante','Departamento', 'Seção', 'Categoria', 'Linha','Qtde Saldo','Alerta']].to_excel('Estoque.xlsx',index=False)

        Enviar(tabela_df,base_df)

        pass

    Remover.RemoverArquivo('.xlsx')

    pass

def Enviar(tabelas_df,base_df):

    data_atual=data.HoraAtual()

    hora=data_atual.hour

    msg='Bom dia' if hora<12 else 'Boa tarde'

    email_to=tabelas_df['Vendedor']['E-mail'].unique().tolist()

    email_cc=['compras@demarchibrasil.com.br','edson.junior@demarchibrasil.com.br','athos.alcantara@demarchisaopaulo.com.br','edson.francisco@demarchisaopaulo.com.br','faturamento@demarchibrasil.com.br']

    assunto='Alerta de Estoque'

    temp_path=os.path.join(os.getcwd(),'*.xlsx')

    anexo=glob(temp_path)

    temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

    indisponivel=Moeda.Numero(len(base_df['SKU'].loc[base_df['Alerta']=='INDISPONÍVEL'].unique().tolist()))

    disponivel=Moeda.Numero(len(base_df['SKU'].loc[base_df['Alerta']=='DISPONÍVEL'].unique().tolist()))

    prod=Moeda.Numero(len(base_df['SKU'].unique().tolist()))

    mensagem=f"""
    
    <p>{msg};</p>

    <p>Caros</p>

    <p>Em anexo contém cerca de {prod} SKU's dentre eles {disponivel} disponível e {indisponivel} indisponível.</p>

    <P>Por favor não responder mensagem automática</P>

    <p>Atenciosamente</p>

    <p>BOT TI</p>    

    
    """

    Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)
    
    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)
    
    Main(tabelas)

    pass