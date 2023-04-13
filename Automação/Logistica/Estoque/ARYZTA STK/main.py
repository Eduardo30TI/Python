from Query import Query
from Email import Email
from glob import glob
import os
from Tempo import DataHora
from Acesso import Login
import pandas as pd

data=DataHora()

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Estoque':
    
    """

    SELECT * FROM netfeira.vw_stkaryzta

    """,
    
    'TargetEstatico':
    
    """
    
    DECLARE @DTFIM DATETIME,@DTINICIO DATETIME

    SET @DTFIM=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    SET @DTINICIO=DATEADD(DAY,-31,@DTFIM)

    SELECT * FROM netfeira.vw_targetestatico
    WHERE [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM
    ORDER BY [Data de Faturamento]
    
    """,
    
    'Produto':
    
    """
    
    SELECT * FROM netfeira.vw_produto    
    
    """

}

def Base(tabela_df):

    tabela_df['TargetEstatico']=tabela_df['TargetEstatico'].loc[(tabela_df['TargetEstatico']['Tipo de Operação']=='VENDAS')]

    tabela_df['TargetEstatico']=tabela_df['TargetEstatico'].merge(tabela_df['Produto'],on='SKU',how='inner')[['Data de Emissão', 'Data de Faturamento', 'Pedido', 'Nfe', 'ID Empresa',
        'ID Cliente', 'ID Vendedor', 'Tipo de Pedido', 'Tipo de Operação',
        'Tabelas', 'SKU','Cód. Fabricante', 'Produto', 'Status', 'Fabricante','Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA',
        'Total Geral', 'Total Venda', 'Comissão R$', 'Margem Bruta R$',
        'Cad Vendedor', 'Situação', 'Peso Bruto KG', 'Peso Líquido KG','Unid. CMP','Fator CMP']]

    vendas_df=pd.DataFrame()

    vendas_df=tabela_df['TargetEstatico']

    vendas_df=vendas_df[['Data de Faturamento','SKU','Produto','Unid. CMP','Fator CMP','Qtde']].loc[vendas_df['Fabricante'].str.contains('ARYZTA')].groupby(['Data de Faturamento','SKU','Produto','Unid. CMP','Fator CMP'],as_index=False).sum()

    valores=[]

    for indice,linha in vendas_df.iterrows():
        
        if(linha['Unid. CMP']=='KG'):
        
            res=linha['Qtde']*linha['Fator CMP']
            
            pass
        
        else:
            
            res=int(linha['Qtde']/linha['Fator CMP'])
            
            pass
        
        valores.append(res)
        
        pass

    vendas_df['Convertido']=valores

    vendas_df=vendas_df[['SKU','Produto','Convertido']].groupby(['SKU','Produto'],as_index=False).mean()

    vendas_df['Convertido']=vendas_df.apply(lambda info: int(info['Convertido']),axis=1)

    vendas_df=vendas_df[['SKU','Convertido']].loc[vendas_df['Convertido']>0]

    return vendas_df

    pass

def Analise(tabelas_df):

    vendas_df=Base(tabelas_df)

    estoque_df=tabelas_df['Estoque']

    local=estoque_df['Tipo'].loc[~estoque_df['Local'].str.contains('SUL')].unique().tolist()

    data_atual=data.HoraAtual()

    if(data_atual.hour<=11):

        msg='Bom dia;'

        pass

    else:

        msg='Boa tarde;'

        pass

    nome='Rafael/Vanessa'

    mensagem=f"""
        
    <p>{msg}</p>

    <p>{str(nome).title()}</p>

    <p>Tudo bem, estou encaminhando a relação do estoque atualizado conforme anexo. Dúvidas entrar em contato com o setor de compras.</p>

    <P>Por favor não responder mensagem automática</P>

    <p>Atenciosamente</p>

    <p>BOT TI</p>    
    
    
    """

    email_to=['rafael.fabiano@grupobimbo.com','vanessa.lopes@grupobimbo.com']

    email_cc=['edson.junior@demarchibrasil.com.br','compras@demarchibrasil.com.br','julio@demarchibrasil.com.br']

    assunto='Estoque BIMBO'

    consolidado_df=estoque_df[['SKU','Cód. Fabricante','Produto','Fabricante','Fator CX','Caixa Disponível']].loc[estoque_df['Tipo'].isin(local)].groupby(['SKU','Cód. Fabricante','Produto','Fabricante','Fator CX'],as_index=False).sum()

    consolidado_df=consolidado_df.merge(vendas_df,on='SKU',how='left')

    consolidado_df.loc[consolidado_df['Convertido'].isnull(),'Convertido']=0

    consolidado_df['Dias']=consolidado_df.apply(lambda info: int(info['Caixa Disponível']/info['Convertido']) if info['Convertido']>0 else info['Caixa Disponível'],axis=1)

    consolidado_df.rename(columns={'Convertido':'Qtde Média'},inplace=True)

    consolidado_df.to_excel('Consolidado.xlsx',index=False)

    for l in local:

        arquivo=(f'{str(l).title()}.xlsx')

        temp_df=estoque_df[['SKU','Cód. Fabricante','Produto','Fabricante','Fator CX','Caixa Disponível']].loc[estoque_df['Tipo']==l]

        temp_df=temp_df.merge(vendas_df,on='SKU',how='left')

        temp_df.loc[temp_df['Convertido'].isnull(),'Convertido']=0

        temp_df['Dias']=temp_df.apply(lambda info: int(info['Caixa Disponível']/info['Convertido']) if info['Convertido']>0 else info['Caixa Disponível'],axis=1)

        temp_df.rename(columns={'Convertido':'Qtde Média'},inplace=True)

        temp_df.to_excel(arquivo,index=False)

        pass

    temp_path=os.path.join(os.getcwd(),'*.xlsx')

    anexo=glob(temp_path)

    temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

    Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

    RemoverArquivo('.xlsx')

    pass

def RemoverArquivo(filtro):

    filtro=(f'*{filtro}')

    temp_path=os.path.join(os.getcwd(),filtro)

    dados=glob(temp_path)

    for arq in dados:
        
        os.remove(arq)

    pass

if __name__=='__main__':

    tabelas_df=sql.CriarTabela(kwargs=querys)

    Analise(tabelas_df)

    pass