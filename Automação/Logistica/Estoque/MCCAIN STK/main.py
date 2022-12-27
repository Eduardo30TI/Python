from Email.outlook import Email
from Query import Query
from Acesso import Login
import pandas as pd
import os
from glob import glob
from Tempo import DataHora


s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()


def Estoque(tabelas_df):

    tabelas_df['Produto']=tabelas_df['Produto'][['SKU','Categoria','Linha','Grupo MCCAIN']].loc[tabelas_df['Produto']['Fabricante']=='MCCAIN']

    tabelas_df['Estoque']=tabelas_df['Estoque'].merge(tabelas_df['Produto'],on='SKU',how='inner')[['Local', 'Tipo', 'SKU', 'Cód. Fabricante', 'Produto', 'Fabricante','Grupo MCCAIN',
       'Unid. CMP', 'Qtde CMP']]

    estoque_df=tabelas_df['Estoque'].groupby(['SKU','Cód. Fabricante','Produto','Fabricante','Grupo MCCAIN','Unid. CMP'],as_index=False).sum()

    grupo=estoque_df['Grupo MCCAIN'].unique().tolist()

    nome={'MCCAIN VAREJO':'MATHEUS','MCCAIN FOOD':'JOSÉ'}

    emails={'MCCAIN VAREJO':['Matheus.ZAPATEIRO@mccain.com.br'],'MCCAIN FOOD':['Bruno.BARBOSA@mccain.com.br']}

    for g in grupo:

        if(len(grupo)<=0):

            continue
        
        data_atual=data.HoraAtual()

        hora=data_atual.hour

        if(hora<=11):

            msg='Bom dia'

            pass

        else:

            msg='Boa tarde'

            pass

        temp_df=estoque_df.loc[(estoque_df['Grupo MCCAIN']==g)&(estoque_df['Qtde CMP']>0)]

        temp_df.to_excel(f'Estoque {g}.xlsx',index=False,encoding='UTF-8')

        mensagem=f"""
                
        <p>{msg};</p>

        <p>{str(nome[g]).title()}</p>

        <p>Segue a relação do estoque {str(g).upper()} do dia {data_atual.strftime('%d/%m/%Y')}</p>

        <P>Por favor não responder mensagem automática</P>

        <p>Atenciosamente</p>

        <p>BOT TI</p>        
        
        """
        
        email_to=emails[g]

        email_cc=['compras@demarchibrasil.com.br','edson.junior@demarchibrasil.com.br']

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        anexo=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

        assunto=f'Estoque {str(g).upper()}'

        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

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

    tabelas=sql.CriarTabela()

    Estoque(tabelas)

    pass