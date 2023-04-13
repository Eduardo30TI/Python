from Query import Query
from Acesso import Login
import os
from glob import glob
import pandas as pd
from Email import Email
from Tempo import DataHora
from Moeda import Moeda
from datetime import timedelta

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

def Base(tabelas_df):

    tabelas_df['Vendedor'].rename(columns={'Categoria':'Categoria Vendedor'},inplace=True)

    tabelas_df['Vendedor']=tabelas_df['Vendedor'].merge(tabelas_df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria Vendedor','ID Sup','Supervisor', 'Email Sup','ID Gerente',
        'Gerente', 'Email Gerente']] 

    tabelas_df['Cliente']=tabelas_df['Cliente'].merge(tabelas_df['Segmento'],on='ID Segmento',how='inner')[['ID Cliente', 'CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'Segmento', 'Canal', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato']]

    tabelas_df['Devolucao']=tabelas_df['Devolucao'].merge(tabelas_df['Cliente'],on='ID Cliente',how='inner')[['Data de Entrada', 'Motivo', 'Situação do Pedido', 'Tipo de Pedido',
        'Tipo de Operação', 'Tabelas', 'Pedido', 'NFe', 'ID Cliente','CNPJ', 'Razão Social', 'Nome Fantasia',
        'Segmento', 'Canal', 'Matriz',    
        'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato',
        'ID Vendedor', 'SKU', 'Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor Unitário',
        'Total Geral']]    

    tabelas_df['Devolucao']=tabelas_df['Devolucao'].merge(tabelas_df['Produto'],on='SKU',how='inner')[['Data de Entrada', 'Motivo', 'Situação do Pedido', 'Tipo de Pedido',
        'Tipo de Operação', 'Tabelas', 'Pedido', 'NFe', 'ID Cliente', 'CNPJ',
        'Razão Social', 'Nome Fantasia', 'Segmento', 'Canal', 'Matriz', 'CEP',
        'Endereço', 'Bairro', 'Município', 'Numero', 'Complemento', 'Região',
        'UF', 'DDD', 'Contato', 'ID Vendedor', 'SKU','Produto', 'Fabricante', 'Departamento', 'Seção', 'Categoria',
        'Linha', 'Qtde', 'Unid. VDA',
        'Qtde VDA', 'Valor Unitário', 'Total Geral']]
        
    tabelas_df['Devolucao']=tabelas_df['Devolucao'].merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['Data de Entrada', 'Motivo', 'Situação do Pedido', 'Tipo de Pedido',
        'Tipo de Operação', 'Tabelas', 'Pedido', 'NFe', 'ID Cliente', 'CNPJ',
        'Razão Social', 'Nome Fantasia', 'Segmento', 'Canal', 'Matriz', 'CEP',
        'Endereço', 'Bairro', 'Município', 'Numero', 'Complemento', 'Região',
        'UF', 'DDD', 'Contato', 'ID Vendedor','Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria Vendedor', 'ID Sup','Supervisor', 'Email Sup','ID Gerente', 'Gerente',
        'Email Gerente', 'SKU', 'Produto', 'Fabricante',
        'Departamento', 'Seção', 'Categoria', 'Linha', 'Qtde', 'Unid. VDA',
        'Qtde VDA', 'Valor Unitário', 'Total Geral']]

    return tabelas_df['Devolucao']

    pass

def Equipes(df):

    colunas={'ID Vendedor':'Email Sup','ID Sup':'Email Gerente','ID Gerente':'Email Gerente'}

    col_nome={'ID Vendedor':'Nome Resumido','ID Sup':'Supervisor','ID Gerente':'Gerente'}

    for c,d in colunas.items():

        codigos=df[c].loc[(~df['E-mail'].isnull())].unique().tolist()

        if(len(codigos)<=0):

            continue

        for cod in codigos:

            email_cc=[]

            email_to=[]

            data_atual=data.HoraAtual()

            hora=data_atual.hour

            dia=data_atual.day

            ano=data_atual.year

            id_mes=data_atual.month

            data_ant=data_atual.date()-timedelta(days=1)
            
            temp_df=df.loc[df[c]==cod]

            motivos_df=temp_df[['Motivo','Total Geral']].groupby(['Motivo'],as_index=False).sum()

            motivos_df.sort_values('Total Geral',ascending=False,ignore_index=True,inplace=True)

            total=round(motivos_df['Total Geral'].sum(),2)

            motivos_df['Rep %']=motivos_df.apply(lambda info: round(info['Total Geral']/total,4)*100,axis=1)

            motivos_df['Pedido']=motivos_df.apply(lambda info: len(temp_df['Pedido'].loc[temp_df['Motivo']==info['Motivo']].unique().tolist()),axis=1)

            motivos_df['Cliente']=motivos_df.apply(lambda info: len(temp_df['ID Cliente'].loc[temp_df['Motivo']==info['Motivo']].unique().tolist()),axis=1)

            temp_df.to_excel('Lista de Pedidos.xlsx',index=False)

            motivos_df.to_excel('Motivos.xlsx',index=False)

            if(hora<=11):

                msg='Bom dia'


                pass


            else:

                msg='Boa tarde'

                pass

            temp_path=os.path.join(os.getcwd(),'*.xlsx')

            anexo=glob(temp_path)
                       
            nome=temp_df[col_nome[c]].unique().tolist()

            pedido=Moeda.Numero(len(temp_df['Pedido'].unique().tolist()))

            total=temp_df['Total Geral'].sum()

            total=Moeda.FormatarMoeda(total)

            nome=nome[-1]

            if(c=='ID Vendedor'):

                email_to=temp_df['E-mail'].unique().tolist()

                #email_cc=temp_df[d].unique().tolist()

                pass

            elif(c=='ID Sup'):

                email_to=temp_df['Email Sup'].unique().tolist()

                #email_cc=temp_df[d].unique().tolist()

                pass            

            else:

                email_to=temp_df[d].unique().tolist()

                #email_cc=temp_df[d].unique().tolist()


                pass
            
            if(email_to[-1]==email_cc[-1]):

                email_cc=[]

                pass             

            if((id_mes-1)==0):

                ano-=1

                mes=data.Mes(12)

                pass

            else:

                id_mes-=1

                pass

            mes=data.Mes(id_mes)

            if(dia==1):

                assunto='Geral devoluções e cancelamento'

                mensagem=f"""
                
                <p>{msg}</p>

                <p>{str(nome).title()}</p>

                <p>Estou encaminhando uma relação referente a {mes.title()} de {ano}, com cerca de {pedido} pedido(s) devolvidos ou cancelado. Totalizando R$ {total}</p>

                <P>Por favor não responder mensagem automática</P>

                <p>Atenciosamente</p>

                <p>BOT TI</p>                
                            
                """                

                pass

            else:

                assunto='Relação de devolução e cancelamento'

                mensagem=f"""
                
                <p>{msg}</p>

                <p>{str(nome).title()}</p>

                <p>Foram identificados cerca de {pedido} pedido(s) devolvidos ou cancelado referente ao dia {data_ant.strftime('%d/%m/%Y')}. Totalizando R$ {total}</p>

                <P>Por favor não responder mensagem automática</P>

                <p>Atenciosamente</p>

                <p>BOT TI</p>                
                            
                """                

                pass
            
            temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

            Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

            RemoverArquivo('.xlsx')

            pass

        pass

    pass

def RemoverArquivo(filtro):

    filtro=(f'*{filtro}')

    temp_path=os.path.join(os.getcwd(),filtro)

    dados=glob(temp_path)

    for arq in dados:
        
        os.remove(arq)

    pass

if __name__=='__main__':

    tabela=sql.CriarTabela()

    df=Base(tabela)

    Equipes(df)

    pass