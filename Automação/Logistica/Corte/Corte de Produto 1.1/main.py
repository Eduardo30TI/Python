from Email import Email
from Query import Query
from glob import glob
import os
import pandas as pd
from Tempo import DataHora
from Moeda import Moeda

sql=Query('Netfeira','sqlserver','MOINHO','192.168.0.252')

data=DataHora()

def Base(tabela_dict):

    tabela_dict['Faltas']=tabela_dict['Faltas'].merge(tabela_dict['Vendedores'],on='ID Vendedor',how='inner')[['Data de Falta', 'ID Vendedor','Vendedor', 'Nome Resumido', 'ID Equipe', 'E-mail',
        'Categoria', 'ID Cliente', 'Nome Fantasia', 'Pedido',
        'SKU', 'Produto', 'Unid. VDA', 'Qtde. VDA', 'Valor Unitário',
        'Total do Pedido']]

    tabela_dict['Faltas']=tabela_dict['Faltas'].merge(tabela_dict['Supervisor'],on='ID Equipe',how='inner')[['Data de Falta', 'ID Vendedor','Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria','Supervisor', 'Email Sup',
        'Gerente', 'Email Gerente', 'ID Cliente', 'Nome Fantasia', 'Pedido',
        'SKU', 'Produto', 'Unid. VDA', 'Qtde. VDA', 'Valor Unitário',
        'Total do Pedido']]

    tabela_dict['Faltas'].sort_values('Total do Pedido',ascending=False,inplace=True)

    return tabela_dict['Faltas']     

    pass

def Analisar(tabela):

    dados_df=Base(tabela)

    emails={'E-mail':dados_df['E-mail'].loc[(dados_df['E-mail']!='')].unique().tolist(),
            
            'Email Sup': dados_df['Email Sup'].loc[(dados_df['Email Sup']!='')].unique().tolist()
            
        }

    colunas={'E-mail':'Email Sup','Email Sup':'Email Gerente'}

    for coluna,email in emails.items():
        
        for env in email:
            
            email_to=[]
            
            email_cc=[]
            
            email_res=dados_df[colunas[coluna]].loc[dados_df[coluna]==env].unique().tolist()

            pedido=len(dados_df['Pedido'].loc[dados_df[coluna]==env].unique().tolist())

            sku=len(dados_df['SKU'].loc[dados_df[coluna]==env].unique().tolist())

            total=round(dados_df['Total do Pedido'].loc[dados_df[coluna]==env].sum(),2)

            total=Moeda.FormatarMoeda(total)

            data_atual=data.HoraAtual()

            if(data_atual.hour<=11):

                msg='Bom dia'

                pass

            else:

                msg='Boa tarde'

                pass
            
            if(coluna=='E-mail'):
            
                nome=dados_df['Nome Resumido'].loc[dados_df[coluna]==env].unique().tolist()
                
                nome=str(nome[0]).title()
                
                arq=(f'{nome}.xlsx')

                if(pedido<=0):

                    continue

                email_to.append(env)

                if(env!=email_res[0]):

                    #email_cc.append(email_res[0])

                    pass

                menssagem=f"""
                
                <p>{msg}</p>

                <p>{nome}</p>
                
                <p>Foram identificados cerca de {sku} itens que foram cortados. Totalizando R$ {total}</p>

                <p>Por favor não responder ou enviar e-mail, pois se trata de uma mensagem automática</p>

                <p>Atenciosamente BOT TI</p>
                
                """

                dados_df.loc[dados_df[coluna]==env].to_excel(arq,index=False,encoding='ISO-8859-1')

                produto_df=dados_df[['SKU','Produto','Total do Pedido']].loc[dados_df[coluna]==env].groupby(['SKU','Produto'],as_index=False).agg({'Total do Pedido':'sum'})

                produto_df.sort_values('Total do Pedido',ascending=False,inplace=True) 

                produto_df.to_excel('Produto.xlsx',index=False,encoding='ISO-8859-1')

                temp_path=os.path.join(os.getcwd(),'*.xlsx')

                anexo=glob(temp_path)

                temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}                

                Email.EnviarEmail(corpo=menssagem,assunto='Corte de Produto',kwargs=temp_dict)
                
                pass
            
            else:
               
                nome=dados_df['Supervisor'].loc[dados_df[coluna]==env].unique().tolist()
                
                nome=str(nome[0]).title()
                
                arq=(f'{nome}.xlsx')

                if(pedido<=0):

                    continue

                email_to.append(env)

                if(env!=email_res[0]):

                    #email_cc.append(email_res[0])

                    pass                

                menssagem=f"""
                
                <p>{msg}</p>

                <p>{nome}</p>
                
                <p>Foram identificados cerca de {sku} itens que foram cortados. Totalizando R$ {total}</p>

                <p>Por favor não responder ou enviar e-mail, pois se trata de uma mensagem automática</p>

                <p>Atenciosamente BOT TI</p>
                
                """

                dados_df.loc[dados_df[coluna]==env].to_excel(arq,index=False,encoding='ISO-8859-1')

                produto_df=dados_df[['SKU','Produto','Total do Pedido']].loc[dados_df[coluna]==env].groupby(['SKU','Produto'],as_index=False).agg({'Total do Pedido':'sum'})

                produto_df.sort_values('Total do Pedido',ascending=False,inplace=True)

                produto_df.to_excel('Produto.xlsx',index=False,encoding='ISO-8859-1')                

                temp_path=os.path.join(os.getcwd(),'*.xlsx')

                anexo=glob(temp_path)

                temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}
                
                Email.EnviarEmail(corpo=menssagem,assunto='Corte de Produto',kwargs=temp_dict)
                
                pass
            
            RemoverArquivo('.xlsx')
            
            pass
        
        pass

    pass

def Geral():

    tabela=sql.CriarTabela()

    dados_df=Base(tabela)

    email_to=['edson.junior@demarchibrasil.com.br']

    email_cc=['julio@demarchibrasil.com.br']

    pedido=Moeda.Numero(len(dados_df['Pedido'].unique().tolist()))

    sku=Moeda.Numero(len(dados_df['SKU'].unique().tolist()))

    total=round(dados_df['Total do Pedido'].sum(),2)

    total=Moeda.FormatarMoeda(total)

    data_atual=data.HoraAtual()

    if(data_atual.hour<=11):
        
        msg='Bom dia'

        pass

    else:

        msg='Boa tarde'

        pass
    
    nome='Edson Junior'

    if(pedido>0):

        menssagem=f"""
                
        <p>{msg}</p>

        <p>{nome}</p>
                
        <p>Foram identificados cerca de {sku} itens que foram cortados. Totalizando R$ {total}</p>

        <p>Por favor não responder ou enviar e-mail, pois se trata de uma mensagem automática</p>

        <p>Atenciosamente BOT TI</p>
                
        """

        dados_df.to_excel('Corte Geral.xlsx',index=False,encoding='ISO-8859-1')

        produto_df=dados_df[['SKU','Produto','Total do Pedido']].groupby(['SKU','Produto'],as_index=False).agg({'Total do Pedido':'sum'})

        produto_df.sort_values('Total do Pedido',ascending=False,inplace=True)

        produto_df.to_excel('Produto.xlsx',index=False,encoding='ISO-8859-1')                

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        anexo=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}
                
        Email.EnviarEmail(corpo=menssagem,assunto='Corte de Produto',kwargs=temp_dict)

        RemoverArquivo('.xlsx')

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

    Analisar(tabela)

    Geral()

    pass