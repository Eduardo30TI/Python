from h11 import Data
from Query import Query
from Acesso import Login
from Email import Email
from Tempo import DataHora
from RemoverArquivo import Remover
import os
from glob import glob
from Moeda import Moeda, moedas

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={

    'Carteira':

    """

    SELECT * FROM netfeira.vw_carteira
    WHERE [Status do Cliente]='ATIVO'    
    
    """,

    'Segmento':


    """
    
    SELECT * FROM netfeira.vw_segmento
    
    """,

    'Frequencia':


    """
    
    SELECT * FROM netfeira.vw_frequencia
    
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

    tabela_df['Carteira']=tabela_df['Carteira'].loc[tabela_df['Carteira']['Dias']<=365]

    tabela_df['Carteira']=tabela_df['Carteira'].merge(tabela_df['Frequencia'],on='ID Cliente',how='left')[['ID Cliente', 'CNPJ', 'Caracter CNPJ', 'Razão Social', 'Nome Fantasia',
        'Status do Cliente', 'Matriz', 'Segmento', 'Canal', 'Tabela',
        'Condição de Pagto', 'Prazo', 'Forma Pagto', 'Crédito', 'Tributação',
        'CEP', 'Endereço', 'Bairro', 'Cidade', 'UF', 'Numero', 'Complemento',
        'Latitude', 'Longitude', 'Região', 'DDD', 'Contato', 'ID Vendedor',
        'Nome', 'Nome Resumido', 'E-mail', 'Categoria', 'Equipe', 'Supervisor',
        'Email Sup', 'Gerente', 'Email Gerente', 'Principal', 'Primeira Compra',
        'Última Compra', 'Seq', 'Dias','Data Agendada','Intervalo','Qtde Vezes', 'Status de Atendimento']]

    tabela_df['Carteira'].loc[tabela_df['Carteira']['Status de Atendimento'].isnull(),'Status de Atendimento']='COMPROU UMA VEZ'

    tabela_df['Carteira']=tabela_df['Carteira'].loc[(~tabela_df['Carteira']['Status de Atendimento'].isin(['AGENDADO','INATIVO']))]

    Analise(tabela_df['Carteira'])

    pass

def Analise(carteira_df):

    emails={'E-mail':'Email Sup','Email Sup':'Email Gerente'}

    colunas={'E-mail':'Nome Resumido','Email Sup':'Supervisor','Email Gerente':'Gerente'}

    for to,cc in emails.items():

        to_list=[l for l in carteira_df[to].unique().tolist() if l!='']

        for email in to_list:

            email_to=[]

            email_cc=[]

            data_atual=data.HoraAtual()

            hora=data_atual.hour

            if(hora<=11):

                msg='Bom dia'

                pass

            else:

                msg='Boa tarde'

                pass

            temp_df=carteira_df.loc[carteira_df[to]==email]

            nome=temp_df[colunas[to]].unique().tolist()

            nome=str(nome[-1]).title()

            email_to.append(email)

            #email_cc=temp_df[cc].unique().tolist()

            if(email_to[-1]==email_cc[-1]):

                email_cc=[]

                pass

            temp_df.to_excel(f'Lista de Atendimento {nome}.xlsx',index=False,encoding='utf-8')
            
            grupo_df=temp_df[['Status de Atendimento','ID Cliente']].groupby(['Status de Atendimento'],as_index=False).count()

            grupo_df.rename(columns={'ID Cliente':'Contagem'},inplace=True)

            grupo_df.sort_values('Contagem',ascending=False,inplace=True)

            grupo_df.to_excel(f'Alerta {nome}.xlsx',index=False,encoding='utf-8')
            
            temp_path=os.path.join(os.getcwd(),'*.xlsx')

            anexo=glob(temp_path)

            temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

            assunto='Alerta de Atendimento'

            atrasado=Moeda.Numero(len(temp_df['ID Cliente'].loc[temp_df['Status de Atendimento']=='ATRASADO'].unique().tolist()))

            comprou=Moeda.Numero(len(temp_df['ID Cliente'].loc[temp_df['Status de Atendimento']=='COMPROU UMA VEZ'].unique().tolist()))

            ligar=Moeda.Numero(len(temp_df['ID Cliente'].loc[temp_df['Status de Atendimento']=='LIGAR'].unique().tolist()))

            contagem=Moeda.Numero(len(temp_df))

            mensagem=f"""
            
            <p>{msg};</p>

            <p>{nome}</p>

            <p>Tudo bem, no anexo tem uma relação de {contagem} cliente(s) que precisa de atendimento.</p>

            <p>Informações por status abaixo:</p>

                <p style:"font-weight: bold">.Atrasado: {atrasado}</p>

                <p style:"font-weight: bold">.Comprou uma vez: {comprou}</p>

                <p style:"font-weight: bold">.Ligar: {ligar}</p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>BOT TI</p>                       
            
            """

            Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

            Remover.RemoverArquivo('.xlsx')

            #break

            pass

        pass

    pass


if __name__=='__main__':

    tabela_df=sql.CriarTabela(kwargs=querys)

    Base(tabela_df)

    pass