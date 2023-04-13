from h11 import Data
from Acesso import Login
from Query import Query
from Email import Email
from RemoverArquivo import Remover
from Moeda import Moeda
from Tempo import DataHora
import os
from glob import glob
import pandas as pd

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={

    'Receber':

    """

    SELECT * FROM netfeira.vw_contareceber
    ORDER BY [Data de Vencimento]    
        
    """,

    'Segmento':

    """

    SELECT * FROM netfeira.vw_segmento
    
    """,

    'Cliente':

    """

    SELECT * FROM netfeira.vw_cliente
    
    """

}


def Main(tabelas_df):


    tabelas_df['Cliente']=tabelas_df['Cliente'].merge(tabelas_df['Segmento'],on='ID Segmento',how='inner')[['ID Cliente', 'CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'Segmento','Canal', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato', 'Limite de Crédito',
        'Principal']]

    
    tabelas_df['Receber']=tabelas_df['Receber'][['Data de Emissão', 'Data de Vencimento', 'Data de Pagamento', 'Título',
        'Serie', 'Tipo de Pagamento', 'ID Cliente', 'Situação', 'Valor',
        'Desconto R$', 'Multa R$', 'Juros R$', 'Abatimento R$', 'Taxa R$',
        'Valor Líquido', 'Pago R$', 'Status do Título', 'Dias', 'Alerta']]

    
    tabelas_df['Receber']=tabelas_df['Receber'].merge(tabelas_df['Cliente'],on='ID Cliente',how='inner')[['Data de Emissão', 'Data de Vencimento', 'Data de Pagamento', 'Título',
        'Serie', 'Tipo de Pagamento', 'ID Cliente','CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'Segmento', 'Canal', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato', 'Limite de Crédito',
        'Principal', 'Situação', 'Valor',
        'Desconto R$', 'Multa R$', 'Juros R$', 'Abatimento R$', 'Taxa R$',
        'Valor Líquido', 'Pago R$', 'Status do Título', 'Dias', 'Alerta']]

    titulos_df=pd.DataFrame()

    titulos_df=tabelas_df['Receber']

    titulos_df['Saldo R$']=titulos_df.apply(lambda info: info['Valor Líquido']-info['Pago R$'],axis=1)

    titulos_df=titulos_df.loc[titulos_df['Status do Título']=='VENCIDO']

    grupo_df=pd.DataFrame()

    grupo_df=titulos_df[['Alerta','Saldo R$']].groupby(['Alerta'],as_index=False).sum()

    grupo_df['Título']=grupo_df['Alerta'].apply(lambda info: len(titulos_df['Título'].loc[titulos_df['Alerta']==info].unique().tolist()))

    grupo_df.sort_values('Saldo R$',ascending=False,ignore_index=True,inplace=True)

    titulos_df.to_excel('Relação de Título.xlsx',index=False)

    grupo_df.to_excel('Alerta.xlsx',index=False)

    Enviar(titulos_df)

    pass


def Enviar(titulos_df):

    data_atual=data.HoraAtual()

    hora=data_atual.hour

    msg='Bom dia' if hora<12 else 'Boa tarde'

    email_to=['beatriz@demarchibrasil.com.br']

    email_cc=[]

    temp_path=os.path.join(os.getcwd(),'*.xlsx')

    anexo=glob(temp_path)

    temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

    tit_venc=Moeda.Numero(len(titulos_df['Título'].unique().tolist()))

    tot_venc=Moeda.FormatarMoeda(titulos_df['Saldo R$'].sum())

    nome='beatriz'

    mensagem=f"""
    
    <p>{msg};</p>

    <p>{str(nome).title()}</p>

    <p>Estou encaminhando uma relação no anexo com {tit_venc} título(s). Totalizando R$ {tot_venc}.</p>

    <P>Por favor não responder mensagem automática</P>

    <p>Atenciosamente</p>

    <p>BOT TI</p>      
    
    """

    assunto='Inadimplência'

    Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

    Remover.RemoverArquivo('.xlsx')

    pass

if __name__=='__main__':

    tabelas_df=sql.CriarTabela(kwargs=querys)

    Main(tabelas_df)

    pass