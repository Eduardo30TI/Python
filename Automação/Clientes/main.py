import pandas as pd
from Query import Query
from Acesso import Login
from CNPJ import CNPJ
from Email import Email
from RemoverArquivo import Remover
import os
from glob import glob
import RemoverArquivo
from Tempo import DataHora

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={
    
    'Carteira':
    
    """
    
    SELECT * FROM netfeira.vw_carteira
    WHERE [Status do Cliente]='ATIVO' AND [Caracter CNPJ]=14 AND Principal='SIM'
    
    """,
    
    'Segmento':
    
    """
    
    SELECT * FROM netfeira.vw_segmento
    
    """
    
}

def Base(tabela_df):

    tabela_df['Carteira']=tabela_df['Carteira'].merge(tabela_df['Segmento'],on='ID Segmento',how='inner')[['ID Cliente', 'CNPJ', 'Caracter CNPJ', 'Razão Social', 'Nome Fantasia',
        'Status do Cliente', 'Matriz', 'Segmento','Canal', 'Tabela',
        'Condição de Pagto', 'Prazo', 'Forma Pagto', 'Crédito', 'Tributação',
        'CEP', 'Endereço', 'Bairro', 'Cidade', 'UF', 'Numero', 'Complemento',
        'Latitude', 'Longitude', 'Região', 'DDD', 'Contato', 'ID Vendedor',
        'Nome', 'Nome Resumido', 'E-mail', 'Categoria', 'Equipe', 'Supervisor',
        'Email Sup', 'Gerente', 'Email Gerente', 'Principal', 'Primeira Compra',
        'Última Compra', 'Seq', 'Dias']]

    tabela_df['Carteira']=tabela_df['Carteira'].loc[~tabela_df['Carteira']['Equipe'].str.contains('120')]

    temp_path=os.path.join(os.getcwd(),'*.csv')

    base_csv=glob(temp_path)

    if(len(base_csv)>0):

        base_df=pd.read_csv(base_csv[-1],encoding='utf-8')

        base_df['CNPJ']=base_df['CNPJ'].astype('str')

        lista_cnpj=base_df['CNPJ'].unique().tolist()

        tabela_df['Carteira']=tabela_df['Carteira'].loc[~tabela_df['Carteira']['CNPJ'].isin(lista_cnpj)]

        pass
    
    temp_df=pd.DataFrame()

    codigos=tabela_df['Carteira']['ID Vendedor'].unique().tolist()

    for c in codigos:
        
        carteira_df=tabela_df['Carteira'].loc[tabela_df['Carteira']['ID Vendedor']==c].reset_index()
            
        for indice,linha in carteira_df.iterrows():
            
            try:
            
                info=CNPJ(linha['CNPJ'])
                
                dados=info.GetDados()
                
                dados=pd.json_normalize(dados)
                
                temp_df=pd.concat([temp_df,dados],axis=0,ignore_index=True)
                            
                if(indice>=20):
                    
                    break
                
                pass
            
            except:
                
                continue
            
            pass
            
        #break
        
        pass
    
    temp_df.rename(columns={'cnpj':'CNPJ','descricao_situacao_cadastral':'Situação Cadastral'},inplace=True)

    tabela_df['Carteira']=tabela_df['Carteira'].merge(temp_df,on='CNPJ',how='inner')[['ID Cliente', 'CNPJ', 'Caracter CNPJ', 'Razão Social', 'Nome Fantasia',
        'Status do Cliente', 'Matriz', 'Segmento', 'Canal', 'Tabela',
        'Condição de Pagto', 'Prazo', 'Forma Pagto', 'Crédito', 'Tributação',
        'CEP', 'Endereço', 'Bairro', 'Cidade', 'UF', 'Numero', 'Complemento',
        'Latitude', 'Longitude', 'Região', 'DDD', 'Contato', 'ID Vendedor',
        'Nome', 'Nome Resumido', 'E-mail', 'Categoria', 'Equipe', 'Supervisor',
        'Email Sup', 'Gerente', 'Email Gerente', 'Principal', 'Primeira Compra',
        'Última Compra', 'Seq', 'Dias','Situação Cadastral']]

    cliente_df=pd.DataFrame()

    cliente_df=pd.concat([cliente_df,tabela_df['Carteira']],axis=0,ignore_index=True)

    cliente_df=tabela_df['Carteira'][['CNPJ','ID Vendedor']].groupby(['CNPJ'],as_index=False).count()

    cliente_df.to_csv('Lista Base.csv',index=False,encoding='utf-8')    

    if(len(tabela_df['Carteira'])<=0):

        Remover.RemoverArquivo('.csv')

        pass
    
    Analise(tabela_df['Carteira'])
                
    pass

def Analise(carteira_df):

    carteira_df=carteira_df.loc[~carteira_df['Situação Cadastral'].str.contains('ATIVA')]

    col_email={'E-mail':'Email Sup','Email Sup':'Email Gerente'}

    colunas={'E-mail':'Nome Resumido','Email Sup':'Supervisor','Email Gerente':'Gerente'}

    for to,cc in col_email.items():
    
        emails=carteira_df[to].loc[(carteira_df[to]!='')&(~carteira_df[to].isnull())].unique().tolist()

        for email in emails:

            email_to=[]

            email_cc=[]

            col=colunas[to]

            temp_df=carteira_df.loc[carteira_df[to]==email]
            
            nome=temp_df[col].unique().tolist()

            temp_df[['ID Cliente','CNPJ','Razão Social','Nome Fantasia','ID Vendedor','Nome','Situação Cadastral','DDD','Contato']].to_excel(f'Clientes {str(nome[-1]).title()}.xlsx',index=False)

            data_atual=data.HoraAtual()

            hora=data_atual.hour
            
            if(hora<=11):

                msg='Bom dia'

                pass

            else:

                msg='Boa tarde'

                pass

            assunto='Situação cadastral'
            
            mensagem=f"""
                        
            <p>{msg};</p>

            <p>{str(nome[-1]).title()}</p>

            <p>Tudo bem, estou encaminhando uma relação com {len(temp_df)} cliente(s) que estão com situação cadastral na receita federal diferente de ativa. Por favor verificar se o mesmo permanecerá ativo na carteira ou será inativado. Caso seja inativado encaminhar os clientes para o e-mail: cobranca@demarchibrasil.com.br.</p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>BOT TI</p>                
            
            
            """

            email_to.append(email)
            
            #email_cc=temp_df[cc].unique().tolist()

            if(email_to[-1]==email_cc[-1]):

                email_cc=[]

                pass

            temp_path=os.path.join(os.getcwd(),'*.xlsx')

            anexo=glob(temp_path)

            temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

            Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

            Remover.RemoverArquivo('.xlsx')

            pass

        pass
    
    pass

if __name__=='__main__':

    tabela=sql.CriarTabela(kwargs=querys)

    Base(tabela)
    
    pass