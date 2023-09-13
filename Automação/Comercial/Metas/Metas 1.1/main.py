import pandas as pd
from Email import Email
from Tempo import DataHora
from Query import Query
import os
from glob import glob
from datetime import datetime,timedelta
from Moeda import Moeda

sql=Query('Netfeira','sqlserver','MOINHO','192.168.0.252')

data=DataHora()

conectando=sql.ConexaoSQL()

pd.set_option('float_format','{:.2f}'.format)

def Clientes(tabela_dict):

    data_atual=data.HoraAtual()

    vendas_df=tabela_dict['Venda'].loc[(tabela_dict['Venda']['Tipo de Operação']=='VENDAS')]

    data_max=vendas_df['Data de Faturamento'].max()

    data_inicial=data_max-timedelta(days=365)    

    tabela_dict['Carteira']=tabela_dict['Carteira'].merge(tabela_dict['Segmento'],on='ID Segmento',how='inner')[['ID Cliente', 'CNPJ', 'Caracter CNPJ', 'Razão Social', 'Nome Fantasia',
        'Status do Cliente', 'Matriz', 'Segmento', 'Canal', 'Tabela',
        'Condição de Pagto', 'Prazo', 'Forma Pagto', 'Crédito', 'Tributação',
        'CEP', 'Endereço', 'Bairro', 'Cidade', 'UF', 'Numero', 'Complemento',
        'Latitude', 'Longitude', 'Região', 'DDD', 'Contato', 'ID Vendedor',
        'Nome', 'Nome Resumido','Equipe', 'E-mail', 'Categoria', 'Supervisor',
        'Email Sup', 'Gerente', 'Email Gerente', 'Principal', 'Primeira Compra',
        'Última Compra', 'Seq', 'Dias']]

    tabela_dict['Carteira']=tabela_dict['Carteira'].loc[(tabela_dict['Carteira']['Dias']<=365)&(tabela_dict['Carteira']['Status do Cliente']=='ATIVO')&(~tabela_dict['Carteira']['E-mail'].isnull())]

    grpcliente_df=vendas_df[['ID Cliente','ID Vendedor','Total Geral','Numero do Pedido']].loc[(vendas_df['Data de Faturamento'].between(data_inicial,data_max))].groupby(['ID Cliente','ID Vendedor'],as_index=False).agg({'Total Geral':'sum','Numero do Pedido':'count'})

    tabela_dict['Carteira']['Total Geral']=tabela_dict['Carteira'].apply(lambda info: grpcliente_df['Total Geral'].loc[(grpcliente_df['ID Cliente']==info['ID Cliente'])&((grpcliente_df['ID Vendedor']==info['ID Vendedor']))].sum(),axis=1)

    tabela_dict['Carteira']['Pedido']=tabela_dict['Carteira'].apply(lambda info: grpcliente_df['Numero do Pedido'].loc[(grpcliente_df['ID Cliente']==info['ID Cliente'])&(grpcliente_df['ID Vendedor']==info['ID Vendedor'])].sum(),axis=1)

    tabela_dict['Carteira'].loc[(tabela_dict['Carteira']['Última Compra'].dt.year==data_atual.year)&(tabela_dict['Carteira']['Última Compra'].dt.month==data_atual.month),'Comprou']='SIM'

    tabela_dict['Carteira'].loc[(tabela_dict['Carteira']['Comprou'].isnull()),'Comprou']='NÃO'
    
    return tabela_dict['Carteira']

    pass

def Vendas(tabela_dict):

    data_atual=data.HoraAtual()

    vendas_df=tabela_dict['Venda'].loc[(tabela_dict['Venda']['Tipo de Operação']=='VENDAS')]

    tabela_dict['Vendedor']=tabela_dict['Vendedor'].merge(tabela_dict['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria','Supervisor', 'Email Sup','Gerente', 'Email Gerente']]    

    tabela_dict['Meta']=tabela_dict['Meta'].loc[(tabela_dict['Meta']['mes_ref'].dt.year==data_atual.year)&(tabela_dict['Meta']['mes_ref'].dt.month==data_atual.month)]

    tabela_dict['Vendedor']=tabela_dict['Vendedor'].merge(tabela_dict['Meta'],left_on='ID Vendedor',right_on='cd_vend',how='left')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria','Supervisor', 'Email Sup','Gerente', 'Email Gerente','FATUVL']]

    tabela_dict['Vendedor'].rename(columns={'FATUVL':'Meta R$'},inplace=True)

    grpvenda_df=vendas_df[['ID Vendedor','Total Geral']].loc[(vendas_df['Data de Faturamento'].dt.year==data_atual.year)&(vendas_df['Data de Faturamento'].dt.month==data_atual.month)].groupby(['ID Vendedor'],as_index=False).agg({'Total Geral':'sum'})

    #pedido
    grppedido_df=vendas_df[['ID Vendedor','Status do Pedido','Numero do Pedido']].loc[(vendas_df['Data de Faturamento'].dt.year==data_atual.year)&((vendas_df['Data de Faturamento'].dt.month==(data_atual.month)))].groupby(['ID Vendedor','Status do Pedido'],as_index=False).agg({'Numero do Pedido':'count'})

    grppedido_df.rename(columns={'Numero do Pedido':'Pedido'},inplace=True)

    grppedido_df.loc[~grppedido_df['Status do Pedido'].isin(['FATURADO','EM ABERTO']),'Pedido']=grppedido_df['Pedido']*-1

    grppedido_df=grppedido_df[['ID Vendedor','Pedido']].groupby(['ID Vendedor'],as_index=False).sum()

    #atendimento
    grpatendimento_df=vendas_df[['ID Vendedor','ID Cliente','Status do Pedido','Numero do Pedido']].loc[(vendas_df['Data de Faturamento'].dt.year==data_atual.year)&((vendas_df['Data de Faturamento'].dt.month==(data_atual.month)))].groupby(['ID Vendedor','ID Cliente','Status do Pedido'],as_index=False).agg({'Numero do Pedido':'count'})

    grpatendimento_df=grpatendimento_df[['ID Vendedor','Status do Pedido','ID Cliente']].groupby(['ID Vendedor','Status do Pedido'],as_index=False).count()

    grpatendimento_df.rename(columns={'ID Cliente':'Atendimento'},inplace=True)

    grpatendimento_df.loc[~grpatendimento_df['Status do Pedido'].isin(['FATURADO','EM ABERTO']),'Atendimento']=grpatendimento_df['Atendimento']*-1

    grpatendimento_df=grpatendimento_df[['ID Vendedor','Atendimento']].groupby(['ID Vendedor'],as_index=False).sum()

    tabela_dict['Vendedor']=tabela_dict['Vendedor'].merge(grpvenda_df,on='ID Vendedor',how='left')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria', 'Supervisor', 'Email Sup', 'Gerente', 'Email Gerente','Meta R$','Total Geral']]

    tabela_dict['Vendedor']=tabela_dict['Vendedor'].merge(grppedido_df,on='ID Vendedor',how='left')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria', 'Supervisor', 'Email Sup', 'Gerente', 'Email Gerente','Meta R$','Total Geral','Pedido']]

    tabela_dict['Vendedor']=tabela_dict['Vendedor'].merge(grpatendimento_df,on='ID Vendedor',how='left')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria', 'Supervisor', 'Email Sup', 'Gerente', 'Email Gerente','Meta R$','Total Geral','Pedido','Atendimento']]

    tabela_dict['Calendario']['Feriado']=tabela_dict['Calendario'].apply(lambda info: tabela_dict['Feriado']['Mês Base'].loc[tabela_dict['Feriado']['Mês Base']==info['Mês Base']].count(),axis=1)

    tabela_dict['Calendario']['Dias Úteis']=tabela_dict['Calendario'].apply(lambda info: 0 if info['Feriado']==1 else info['Dias Úteis'],axis=1)

    tabela_dict['Calendario'].drop(columns=['Feriado'],inplace=True)

    dias_uteis=tabela_dict['Calendario']['Dias Úteis'].loc[(tabela_dict['Calendario']['Data'].dt.year==data_atual.year)&(tabela_dict['Calendario']['Data'].dt.month==data_atual.month)].sum()

    tabela_dict['Calendario']['Data']=pd.to_datetime(tabela_dict['Calendario']['Data'].dt.date)

    data_min=tabela_dict['Calendario']['Data'].loc[(tabela_dict['Calendario']['Data'].dt.year==data_atual.year)&(tabela_dict['Calendario']['Data'].dt.month==data_atual.month)].min()

    data_max=datetime.now()

    dias_trabalhados=tabela_dict['Calendario']['Dias Úteis'].loc[(tabela_dict['Calendario']['Data'].dt.year==data_atual.year)&(tabela_dict['Calendario']['Data'].dt.month==data_atual.month)&(tabela_dict['Calendario']['Data'].between(data_min,data_max))].sum()

    tabela_dict['Vendedor']['Projeção R$']=tabela_dict['Vendedor'].apply(lambda info: round(((info['Total Geral']/dias_trabalhados)*dias_uteis),2),axis=1)    

    tabela_dict['Vendedor']['Diferença R$']=tabela_dict['Vendedor'].apply(lambda info: info['Meta R$']-info['Total Geral'],axis=1)

    tabela_dict['Vendedor']['% Reliazado']=tabela_dict['Vendedor'].apply(lambda info: round((info['Total Geral']/info['Meta R$']),4)*100 if info['Meta R$']!=0 else 0,axis=1)

    return tabela_dict['Vendedor']

    pass

def CorpoEmail(clientes,vendas):

    emails={'E-mail':clientes['E-mail'].loc[(clientes['E-mail']!='')].unique().tolist(),
            
            'Email Sup':clientes['Email Sup'].loc[clientes['Email Sup']!=''].unique().tolist()
            
            }

    colunas={'E-mail':'Email Sup','Email Sup':'Email Gerente'}

    clientes.sort_values('Dias',ascending=False,inplace=True)

    data_atual=data.HoraAtual()

    if(data_atual.hour<=11):

        msg='Bom dia'

        pass

    else:
        
        msg='Boa tarde'

        pass

    for coluna,email in emails.items():
        
        for env in email:

            email_to=[]

            email_cc=[]
                        
            email_resp=clientes[colunas[coluna]].loc[clientes[coluna]==env].unique().tolist()

            base_cliente=Moeda.Numero(len(clientes['ID Cliente'].loc[clientes[coluna]==env].unique().tolist()))

            base_atend=Moeda.Numero(len(clientes['ID Cliente'].loc[(clientes[coluna]==env)&(clientes['Comprou']=='SIM')].unique().tolist()))
                            
            if(coluna=='E-mail'):
                
                nome=clientes['Nome Resumido'].loc[clientes[coluna]==env].unique().tolist()
                
                mensagem=f"""
                
                <p>{msg}</p>

                <p>{str(nome[0]).title()}</p>
                                
                <p>Foi encaminhado uma relação de {base_cliente} cliente(s) e você atendeu cerca de {base_atend} cliente(s).</p>

                <p>Essa mensagem é enviada automaticamente por favor não enviar mensagem para este e-mail</p>

                <p>Atenciosamente BOT TI</p>
                
                """

                email_to.append(env)

                if(env!=email_resp[0]):

                    #email_cc.append(email_resp[0])

                    pass

                temp_path=os.path.join(os.getcwd(),'*.xlsx')

                arq=(f'{str(nome[0]).title()}.xlsx')
                
                clientes[['ID Cliente', 'CNPJ', 'Caracter CNPJ', 'Razão Social', 'Nome Fantasia',
       'Status do Cliente', 'Matriz', 'Segmento', 'Canal', 'Tabela',
       'Condição de Pagto', 'Prazo', 'Forma Pagto', 'Crédito', 'Tributação',
       'CEP', 'Endereço', 'Bairro', 'Cidade', 'UF', 'Numero', 'Complemento',
       'Região', 'DDD', 'Contato', 'ID Vendedor',
       'Nome', 'Nome Resumido','Equipe','Supervisor','Primeira Compra',
       'Última Compra','Dias', 'Total Geral', 'Pedido', 'Comprou']].loc[(clientes[coluna]==env)&(~clientes['Equipe'].str.contains('120'))].to_excel(arq,index=False,encoding='ISO-8859-1')

                anexo=glob(temp_path)

                temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

                Email.EnviarEmail(corpo=mensagem,assunto='Relação de Clientes',kwargs=temp_dict)

                RemoverArquivo('.xlsx')
                
                pass
            
            else:
                
                nome=clientes['Supervisor'].loc[clientes[coluna]==env].unique().tolist()
                
                arq=(f'{str(nome[0]).title()}.xlsx')
                
                clientes[['ID Cliente', 'CNPJ', 'Caracter CNPJ', 'Razão Social', 'Nome Fantasia',
       'Status do Cliente', 'Matriz', 'Segmento', 'Canal', 'Tabela',
       'Condição de Pagto', 'Prazo', 'Forma Pagto', 'Crédito', 'Tributação',
       'CEP', 'Endereço', 'Bairro', 'Cidade', 'UF', 'Numero', 'Complemento',
       'Região', 'DDD', 'Contato', 'ID Vendedor',
       'Nome', 'Nome Resumido','Equipe','Supervisor','Primeira Compra',
       'Última Compra','Dias', 'Total Geral', 'Pedido', 'Comprou']].loc[(clientes[coluna]==env)&(~clientes['Equipe'].str.contains('120'))].to_excel(arq,index=False,encoding='ISO-8859-1')

                arq=(f'Metas {str(nome[0]).title()}.xlsx')

                meta=Moeda.FormatarMoeda(vendas['Meta R$'].loc[vendas[coluna]==env].sum())

                pedido=Moeda.Numero(vendas['Pedido'].loc[vendas[coluna]==env].sum())

                atendimento=Moeda.Numero(vendas['Atendimento'].loc[vendas[coluna]==env].sum())

                total=Moeda.FormatarMoeda(vendas['Total Geral'].loc[(vendas[coluna]==env)&(~vendas['Equipe'].str.contains('120'))].sum())

                vendas.loc[vendas[coluna]==env].to_excel(arq,index=False,encoding='ISO-8859-1')

                mensagem=f"""
                
                <p>{msg}</p>

                <p>{str(nome[0]).title()}</p>
                                
                <p>Foi encaminhado uma relação de {base_cliente} cliente(s) e você atendeu cerca de {base_atend} cliente(s). Você tem faturado R$ {total} e sua meta é de R$ {meta} dando um total de pedidos {pedido} e o total de atendimento das vendas é de {atendimento}.</p>

                <p>Essa mensagem é enviada automaticamente por favor não enviar mensagem para este e-mail</p>

                <p>Atenciosamente BOT TI</p>
                
                """

                anexo=glob(temp_path)

                email_to.append(env)

                if(env!=email_resp[0]):

                    #email_cc.append(email_resp[0])

                    pass

                temp_path=os.path.join(os.getcwd(),'*.xlsx')

                anexo=glob(temp_path)

                temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

                Email.EnviarEmail(corpo=mensagem,assunto='Relação Geral de Vendas',kwargs=temp_dict)                            

                RemoverArquivo('.xlsx')
                            
                pass
                        
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

    cliente_df=Clientes(tabela)

    vendas_df=Vendas(tabela)
    
    CorpoEmail(cliente_df,vendas_df)

    pass