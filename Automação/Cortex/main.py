import pandas as pd
import gspread
from Query import Query
from Acesso import Login
from Email import Email
from Moeda import Moeda
from Tempo import DataHora
import os
from glob import glob
from RemoverArquivo import Remover

CODE='19ncwHi1IG0dddhm_vnUgmUrhqKAQngPzs-dPk04eYJs'

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={

    'Vendedor':

    """
    
    SELECT * FROM netfeira.vw_vendedor
    
    """,

    'Supervisor':

    """
    
    SELECT * FROM netfeira.vw_supervisor
    
    """,

    'Cliente':

    """

    SELECT * FROM netfeira.vw_cliente    
    
    """

}

def Main():

    gc = gspread.service_account(filename='.\JSON\keys.json')

    # Open a spreadsheet by title
    sh = gc.open_by_key(CODE)

    ws=sh.worksheet('LEADS')

    sheet_df=pd.DataFrame(ws.get_all_records())

    sheet_df['VENDEDOR']=sheet_df['VENDEDOR'].str.strip()

    return sheet_df

    pass

def Base(tabelas_df,sheet_df):

    tabelas_df['Vendedor']=tabelas_df['Vendedor'].merge(tabelas_df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria', 'Data de Cadastro','ID Sup', 'Supervisor', 'Email Sup',
        'ID Gerente', 'Gerente', 'Email Gerente']]

    tabelas_df['Vendedor']['ID Vendedor']=tabelas_df['Vendedor']['ID Vendedor'].str.strip()

    sheet_df['CNPJ']=sheet_df['CNPJ'].astype('str')

    sheet_df['CNPJ']=sheet_df['CNPJ'].apply(FormatarCNPJ)    

    sheet_df=sheet_df.merge(tabelas_df['Vendedor'],left_on='VENDEDOR',right_on='ID Vendedor',how='inner')[['CNPJ', 'RAZÃO SOCIAL', 'CEP', 'NOME FANTASIA', 'ENDEREÇO', 'BAIRRO',
        'CIDADE', 'NUMERO', 'UF', 'PORTE', 'TELEFONE', 'EMAIL', 'VENDEDOR','Nome Resumido', 'Equipe', 'E-mail',
        'Categoria', 'Data de Cadastro', 'ID Sup', 'Supervisor', 'Email Sup',
        'ID Gerente', 'Gerente', 'Email Gerente',
        'COMPROU', 'MOTIVO', 'DATA', 'OBSERVAÇÃO', 'ATENDIMENTO', 'FOTO']]

    sheet_df.loc[sheet_df['COMPROU']=='FALSE','COMPROU']='NÃO COMPROU'

    sheet_df.loc[sheet_df['COMPROU']=='TRUE','COMPROU']='COMPROU'

    sheet_df.loc[sheet_df['COMPROU']=='','COMPROU']='SEM ATENDIMENTO'

    sheet_df['Vendido']=sheet_df['CNPJ'].apply(lambda info: tabelas_df['Cliente']['CNPJ'][tabelas_df['Cliente']['CNPJ']==info].count())

    sheet_df['Vendido']=sheet_df.apply(lambda info: 'SIM' if info['COMPROU']=='COMPROU' else 'NÃO',axis=1)

    Analise(sheet_df)

    pass

def Analise(sheet_df):
    
    emails={'E-mail':'Email Sup','Email Sup':'Email Gerente','Email Gerente':'Email Gerente'}

    colunas={'E-mail':'Nome Resumido','Email Sup':'Supervisor','Email Gerente':'Gerente'}

    for to,cc in emails.items():

        to_list=[l for l in sheet_df[to].unique().tolist() if l!='']

        for email in to_list:

            email_to=[]

            email_cc=[]

            data_atual=data.HoraAtual()

            hora=data_atual.hour

            temp_df=sheet_df.loc[sheet_df[to]==email]

            nome=temp_df[colunas[to]].unique().tolist()

            nome=nome[-1]

            if(hora<=11):

                msg='Bom dia'

                pass

            else:

                msg='Boa tarde'

                pass

            email_to.append(email)

            #email_cc=sheet_df[cc].loc[sheet_df[to]==email].unique().tolist()

            if(to=='Email Gerente'):

                email_cc=['RENATO@DEMARCHIBRASIL.COM.BR','JULIO@DEMARCHIBRASIL.COM.BR','eduardo.marfim@demarchibrasil.com.br','renato.nogueira@demarchisaopaulo.com.br']

                pass

            assunto='Projeto CORTEX'
            
            contagem=Moeda.Numero(len(temp_df))

            comprou=Moeda.Numero(len(temp_df['CNPJ'].loc[(temp_df['Vendido']=='SIM')&(temp_df['COMPROU']=='COMPROU')].unique().tolist()))

            atendimento=Moeda.Numero(len(temp_df['CNPJ'].loc[temp_df['COMPROU']!='SEM ATENDIMENTO'].unique().tolist()))

            mensagem=f"""
            
            <p>{msg};</p>

            <p>{str(nome).title()}</p>

            <p>No anexo contém {contagem} leads que precisa ser atendida. No momento você já atendeu {atendimento} leads e desta relação {comprou} cliente(s) compraram.</p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>BOT TI</p>                
            
            """

            temp_df.columns=sheet_df.columns.str.title()

            temp_df.rename(columns={'Vendedor':'ID Vendedor'},inplace=True)

            grupo_df=temp_df[['ID Vendedor','Nome Resumido','Equipe','Cnpj']].groupby(['ID Vendedor','Nome Resumido','Equipe'],as_index=False).count()

            grupo_df['Atendimento']=grupo_df.apply(lambda info: len(temp_df['Cnpj'].loc[(temp_df['Comprou']!='SEM ATENDIMENTO')&(temp_df['ID Vendedor']==info['ID Vendedor'])].unique().tolist()),axis=1)

            grupo_df['Leads %']=grupo_df.apply(lambda info: round(info['Atendimento']/info['Cnpj'],4)*100,axis=1)

            grupo_df['Conversão']=grupo_df.apply(lambda info: len(temp_df['Cnpj'].loc[(temp_df['Comprou']=='COMPROU')&(temp_df['Vendido']=='SIM')&(temp_df['ID Vendedor']==info['ID Vendedor'])].unique().tolist()),axis=1)

            grupo_df['Convertido %']=grupo_df.apply(lambda info: round(info['Conversão']/info['Atendimento'],4)*100 if info['Atendimento']!=0 else 0,axis=1)

            grupo_df.rename(columns={'Cnpj':'Leads'},inplace=True)

            grupo_df.to_excel(f'Consolidado.xlsx',index=False,encoding='utf-8')
            
            temp_df.to_excel(f'Cortex {str(nome).title()}.xlsx',index=False,encoding='utf-8')

            temp_path=os.path.join(os.getcwd(),'*.xlsx')

            anexo=glob(temp_path)

            temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

            Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

            Remover.RemoverArquivo('.xlsx')

            pass

        pass

    pass

def FormatarCNPJ(cnpj):
    
    if(len(cnpj)>11 and len(cnpj)<14):
        
        cnpj=f'0{cnpj}'
        
        pass
    
    return cnpj
    
    pass

if __name__=='__main__':

    sheet=Main()

    tabelas_df=sql.CriarTabela(kwargs=querys)

    Base(tabelas_df,sheet)

    pass