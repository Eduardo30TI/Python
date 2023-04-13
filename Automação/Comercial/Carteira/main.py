from Email.outlook import Email
from Query import Query
import os
from glob import glob
import pandas as pd
from Tempo import DataHora

sql=Query('Netfeira','sqlserver','MOINHO','192.168.0.252')

conectando=sql.ConexaoSQL()

data=DataHora()

def Base(tabela_df):

    tabela_df['Vendedor']=tabela_df['Vendedor'].merge(tabela_df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
       'Categoria']]


    vendedor_df=tabela_df['Vendedor'].loc[tabela_df['Vendedor']['Equipe'].str.contains('120')]


    return vendedor_df

    pass

def Analise(tabelas_df):
    
    vendedor_df=Base(tabelas_df)

    tabela_df['Carteira'].rename(columns={'ID Vendedor':'ID Antigo','Nome':'Vendedor Antigo'},inplace=True)

    codigo=vendedor_df['ID Vendedor'].max()

    nome=vendedor_df['Vendedor'].max()

    tabela_df['Carteira']['ID Novo']=codigo

    tabela_df['Carteira']['Vendedor Novo']=nome

    carteira_df=tabela_df['Carteira'].loc[(tabela_df['Carteira']['Dias']>365)&(~tabela_df['Carteira']['Equipe'].str.contains('120'))]

    carteira_df=carteira_df[['ID Cliente', 'CNPJ', 'Razão Social', 'Nome Fantasia','Última Compra','Dias','ID Antigo','Vendedor Antigo','ID Novo','Vendedor Novo']]  

    cont_clientes=len(carteira_df['ID Cliente'].unique().tolist())

    if(cont_clientes>0):

        carteira_df.to_excel('Carteira.xlsx',index=False)

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        anexo=glob(temp_path)

        nome='MARA'

        email_to=['COBRANCA@DEMARCHIBRASIL.COM.BR']

        email_cc=['JULIO@DEMARCHIBRASIL.COM.BR','BEATRIZ@DEMARCHIBRASIL.COM.BR']

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

        data_atual=data.HoraAtual()

        hora=data_atual.hour

        if(hora<=11):

            msg='Bom dia'

            pass


        else:

            msg='Boa tarde'

            pass

        mensagem=f"""
        
            <p>{msg};</p>

            <p>{str(nome).title()}</p>

            <p>Estou encaminhando uma relação de {cont_clientes} cliente(s) para que tenha ciência, pois essas informações já foram alteradas via banco de dados.</p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>BOT TI</p>
        
        """

        Email.EnviarEmail(corpo=mensagem,assunto='Transferência de Carteira',kwargs=temp_dict)

        Transferencia(carteira_df)
        
        RemoverArquivo('.xlsx')

        pass

    pass

def Transferencia(carteira_df):

    base_dict=carteira_df[['ID Cliente','ID Antigo']].to_dict()

    querys=dict()

    codigo=carteira_df['ID Novo'].max()

    for i,cd_clien in base_dict['ID Cliente'].items():

        try:
            
            cd_vend=base_dict['ID Antigo'][i]
            
            cd_vend=str(cd_vend).strip()
            
            querys['Alterar']="""
            
            UPDATE vend_cli
            SET cd_vend='{0}'
            WHERE cd_clien={1} AND cd_vend='{2}'
            
            """.format(codigo,cd_clien,cd_vend)
                        
            sql.Salvar(query=querys['Alterar'],conectando=conectando)

            #print(querys['Alterar'])
                
            #break

            pass

        except:

            continue
        
        pass

    print('Alterado com sucesso!')    

    pass

def RemoverArquivo(filtro):

    filtro=(f'*{filtro}')

    temp_path=os.path.join(os.getcwd(),filtro)

    dados=glob(temp_path)

    for arq in dados:
        
        os.remove(arq)

    pass

def Main(tabela_df):

    tabela_df['Carteira']=tabela_df['Carteira'][['ID Cliente','ID Vendedor']].loc[tabela_df['Carteira']['Principal']=='SIM']

    tabela_df['Cliente']=tabela_df['Cliente'].merge(tabela_df['Carteira'],on='ID Cliente',how='inner')

    tabela_df['Cliente']['Status']=tabela_df['Cliente'].apply(lambda info: 'SIM' if info['Principal']==info['ID Vendedor'] else 'NÃO',axis=1)

    tabela_df['Cliente']=tabela_df['Cliente'].loc[tabela_df['Cliente']['Status']=='NÃO']

    cliente_df=pd.DataFrame()

    cliente_df=tabela_df['Cliente']

    cliente_df.rename(columns={'Principal':'ID Antigo','ID Vendedor':'ID Novo'},inplace=True)

    if(len(cliente_df)>0):

        for indice,linha in cliente_df.iterrows():
                
            query=f"""
            
            UPDATE cliente
            SET cd_vend='{linha['ID Novo']}'
            WHERE cd_clien={linha['ID Cliente']}
            
            """
            
            sql.Salvar(query,sql.conectando)
            
            pass

        pass

    pass

if __name__=='__main__':

    tabela_df=sql.CriarTabela()

    Analise(tabela_df)

    tabela_df=sql.CriarTabela()

    Main(tabela_df)

    pass