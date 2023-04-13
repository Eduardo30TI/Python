from Email import Email
from Query import Query
import pandas as pd
from Tempo import DataHora
from glob import glob
import os
from Acesso import Login

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

data_atual=data.HoraAtual()

hora=data_atual.hour

ano=data_atual.year

def Analise(tabelas_df):

    carteira_df=tabelas_df['Carteira'].groupby(['ID Vendedor'],as_index=False).count()

    carteira_df.rename(columns={'ID Cliente':'Contagem'},inplace=True)    

    tabelas_df['Vendedor']=tabelas_df['Vendedor'].merge(tabelas_df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria','Data de Cadastro', 'ID Sup', 'Supervisor', 'Email Sup',
        'ID Gerente', 'Gerente', 'Email Gerente']]

    tabelas_df['Vendedor']=tabelas_df['Vendedor'].merge(carteira_df,on='ID Vendedor',how='left')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Categoria','Data de Cadastro', 'ID Sup', 'Supervisor', 'Email Sup',
        'ID Gerente', 'Gerente', 'Email Gerente','Contagem']]

    tabelas_df['Vendedor']['Gestor']=tabelas_df['Vendedor'].apply(lambda info: 'SIM' if info['ID Vendedor']==info['ID Sup'] else 'NÃO',axis=1)

    tabelas_df['Vendedor']=tabelas_df['Vendedor'].loc[(tabelas_df['Vendedor']['Gestor']=='NÃO')&(tabelas_df['Vendedor']['Contagem'].isnull())]

    tabelas_df['Vendedor'].to_excel('Vendedores.xlsx',index=False)

    tabelas_df['Vendedor']=tabelas_df['Vendedor'].loc[tabelas_df['Vendedor']['Data de Cadastro'].dt.year<ano]

    vendedores=tabelas_df['Vendedor']['ID Vendedor'].tolist()     

    #contagem=len(tabelas_df['Vendedor']['ID Vendedor'].tolist())

    Corpo(vendedores)

    pass

def Corpo(*vendedores):

    if(hora<12):

        msg='Bom dia'

        pass

    else:

        msg='Boa tarde'

        pass

    email_to=['cobranca@demarchibrasil.com.br']

    email_cc=['beatriz@demarchibrasil.com.br']

    temp_path=os.path.join(os.getcwd(),'*.xlsx')

    anexo=glob(temp_path)

    temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

    mensagem=f"""
    
    <p>{msg};</p>

    <p>Segue a relação de vendedores que foram inativados no sistema. Nesta relação contém {len(vendedores)} vendedore(s).</p>

    <P>Por favor não responder mensagem automática</P>

    <p>Atenciosamente</p>

    <p>BOT TI</p>
    
    """

    if(len(vendedores)>0):

        Email.EnviarEmail(corpo=mensagem,assunto='Inativação de Vendedores',kwargs=temp_dict)

        Transferir(vendedores)

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

def Transferir(*vendedores):

    conectando=sql.ConexaoSQL()

    for v in vendedores[0][0]:
        
        query="""
        
        UPDATE vendedor
        SET ativo=0
        WHERE cd_vend='{0}'
            
        """.format(v)
        
        sql.Salvar(query,conectando)

        #print(query)
        
        #break
        
        pass    

    pass

if __name__=='__main__':

    tabela=sql.CriarTabela()

    Analise(tabela)

    pass