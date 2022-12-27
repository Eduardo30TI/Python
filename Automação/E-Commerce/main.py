from Query import Query
from Tempo import DataHora
from Email import Email
import pandas as pd
from glob import glob
import os

sql=Query('Netfeira','sqlserver','MOINHO','192.168.0.252')

data=DataHora()

conectando=sql.ConexaoSQL()

def Analise():

    tabelas_df=sql.CriarTabela()

    estoque_df=tabelas_df['Estoque']

    temp_path=os.path.join(os.getcwd(),'*.csv')
    
    dados=glob(temp_path)

    data_atual=data.HoraAtual()

    msg=('Bom dia' if data_atual.hour<=11 else 'Boa tarde')

    nome='Renato Nogueira'

    email_to=['renato.nogueira@demarchisaopaulo.com.br']

    email_cc=['eduardo.marfim@demarchibrasil.com.br']

    mensagem=f"""
    
    <p>{msg};</p>

    <p>{nome}</p>

    <p>Estou te encaminhando uma relação de produtos para que seja verificado na plataforma digitar por favor analisar.</p>

    <p>Por favor não responder ou encaminhar e-mail para este contato</p>

    <p>Atenciosamente BOT TI</p>
    
    """    

    if(len(dados)==0):

        estoque_df.loc[estoque_df['Acompanhamento']!='OK'].to_csv('Produtos B2C.csv',index=False,encoding='ISO-8859-1')

        estoque_df.loc[estoque_df['Acompanhamento']!='OK'].to_excel('Produtos B2C.xlsx',index=False,encoding='ISO-8859-1')

        temp_path=os.path.join(os.getcwd(),'*.xlsx')
        
        dados=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':dados}
        
        Email.EnviarEmail(corpo=mensagem,assunto='Produtos B2C',kwargs=temp_dict)

        pass


    else:

        temp_df=pd.read_csv(dados[0],encoding='ISO-8859-1')

        temp_df.rename(columns={'Acompanhamento':'Revisão'},inplace=True)

        resumo_df=temp_df[['SKU','Revisão']]
                
        estoque_df=estoque_df.merge(resumo_df,on='SKU',how='left')[['Local de Estoque', 'SKU', 'Produto', 'Fabricante', 'Departamento',
       'Seção', 'Categoria', 'Linha', 'Saldo Atual', 'Data da Movimentação',
       'Penúltima Movimentação', 'Penúltima Data', 'Acompanhamento','Revisão']]

        estoque_df['Revisão']=estoque_df.apply(lambda info: 'ANALISADO' if info['Acompanhamento']==info['Revisão'] else info['Acompanhamento'],axis=1)

        estoque_df=estoque_df.loc[estoque_df['Revisão']!="ANALISADO"]

        estoque_df=estoque_df.loc[estoque_df['Revisão']!='OK']

        if(len(estoque_df)>0):

            temp_path=os.path.join(os.getcwd(),'*.xlsx')
            
            dados=glob(temp_path)

            estoque_df.drop(columns=['Revisão'],inplace=True)

            estoque_df.to_excel('Produtos B2C.xlsx',index=False,encoding='ISO-8859-1')

            temp_path=os.path.join(os.getcwd(),'*.xlsx')
            
            dados=glob(temp_path)

            temp_dict={'To':email_to,'CC':email_cc,'Anexo':dados}
            
            Email.EnviarEmail(corpo=mensagem,assunto='Produtos B2C',kwargs=temp_dict)                

            pass

        tabelas_df['Estoque'].loc[tabelas_df['Estoque']['Acompanhamento']!='OK'].to_csv('Produtos B2C.csv',index=False,encoding='ISO-8859-1')
        
        pass

    pass

if __name__=='__main__':

    Analise()
    
    pass