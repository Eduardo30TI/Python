import pandas as pd
from Acesso import Login
from Query import Query
from Tempo import DataHora
from Email import Email
import os
from glob import glob
from RemoverArquivo import Remover
from Tempo import DataHora

data=DataHora()

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'TargetEstatico':
    
    """
    
    IF MONTH(GETDATE())=1

        SELECT * FROM netfeira.vw_targetestatico
        WHERE YEAR([Data de Faturamento])=YEAR(GETDATE())-1 AND MONTH([Data de Faturamento])=12

    ELSE

        SELECT * FROM netfeira.vw_targetestatico
        WHERE YEAR([Data de Faturamento])=YEAR(GETDATE()) AND MONTH([Data de Faturamento])=MONTH(GETDATE())-1    
    
    """,
    
    'Produto':
    
    
    """
    
    SELECT * FROM netfeira.vw_produto
    
    """
    
}

def Base(tabelas_df):

    consolidado_df=pd.DataFrame()

    tabelas_df['TargetEstatico']=tabelas_df['TargetEstatico'].loc[tabelas_df['TargetEstatico']['Tipo de Operação']!='OUTROS']

    consolidado_df=tabelas_df['TargetEstatico'][['SKU','Peso Líquido KG','Total Geral']].groupby(['SKU'],as_index=False).sum()

    tabelas_df['Produto']=tabelas_df['Produto'].loc[tabelas_df['Produto']['Fabricante'].str.contains('MCCAIN')]

    consolidado_df=consolidado_df.merge(tabelas_df['Produto'],on='SKU',how='inner')[['SKU','Produto','Peso Líquido KG','Total Geral']]

    consolidado_df.rename(columns={'SKU':'Code','Produto':'Nome','Peso Líquido KG':'Total Kg (LIQUIDO)','Total Geral':'Total preço'},inplace=True)

    Main(consolidado_df)

    pass


def Main(consolidado_df):

    data_atual=data.HoraAtual()

    ano=data_atual.year

    id_mes=data_atual.month-1

    hora=data_atual.hour

    if(hora<12):

        msg='Bom dia'

        pass


    else:

        msg='Boa tarde'

        pass


    if(id_mes<=0):

        id_mes=12

        ano=ano-1

        pass

    mes=data.Mes(id_mes)

    mes=mes.title()

    assunto=f'Fechamento de {mes} de {ano}'

    nome='maicon leme'

    mensagem=f"""
        
    <p>{msg};</p>

    <p>{str(nome).title()}</p>

    <p>Segue o relatório de fechamento da MCCAIN.</p>

    <P>Por favor não responder mensagem automática</P>

    <p>Atenciosamente</p>

    <p>BOT TI</p>        
    
    
    """

    arq=f'Fechamento {ano}{id_mes}.xlsx'

    consolidado_df.to_excel(arq,index=False)

    temp_path=os.path.join(os.getcwd(),'*.xlsx')

    anexo=glob(temp_path)

    email_to=['maicon.leme@thalamuscorp.com']

    email_cc=['eduardo.marfim@demarchibrasil.com.br','renato.nogueira@demarchisaopaulo.com.br']

    temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

    Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

    Remover.RemoverArquivo('.xlsx')

    pass


if __name__=='__main__':

    data_atual=data.HoraAtual()

    if(data_atual.day==1):

        tabelas=sql.CriarTabela(kwargs=querys)
        
        Base(tabelas)

        pass

    pass