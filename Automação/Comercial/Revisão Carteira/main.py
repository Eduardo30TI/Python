from Query import Query
import pandas as pd
from Tempo import DataHora
import os
from glob import glob
from Email import Email

sql=Query('Netfeira','sqlserver','MOINHO','192.168.0.252')

data=DataHora()

conectando=sql.ConexaoSQL()

def Base(tabelas_df):

    carteira_df=tabelas_df['Carteira'].loc[tabelas_df['Carteira']['Equipe'].str.contains('120')]

    tabelas_df['Revisão'].rename(columns={'ID Vendedor':'ID Novo','Vendedor':'Vendedor Novo'},inplace=True)

    carteira_df=carteira_df.merge(tabelas_df['Revisão'],on='ID Cliente',how='left')[['ID Cliente', 'CNPJ', 'Caracter CNPJ', 'Razão Social', 'Nome Fantasia',
        'Status do Cliente', 'Matriz', 'ID Segmento', 'Tabela',
        'Condição de Pagto', 'Prazo', 'Forma Pagto', 'Crédito', 'Tributação',
        'CEP', 'Endereço', 'Bairro', 'Cidade', 'UF', 'Numero', 'Complemento',
        'Latitude', 'Longitude', 'Região', 'DDD', 'Contato', 'ID Vendedor',
        'Nome', 'Nome Resumido', 'E-mail', 'Categoria', 'Equipe', 'Supervisor',
        'Email Sup', 'Gerente', 'Email Gerente', 'Principal', 'Primeira Compra',
        'Última Compra', 'Seq', 'Dias','Data de Faturamento','ID Novo','Vendedor Novo', 'Total do Pedido',
        'Dias do Pedido']]

    carteira_df=carteira_df.loc[(carteira_df['Dias do Pedido']<=365)]

    carteira_df.rename(columns={'ID Vendedor':'ID Antigo','Nome':'Vendedor Antigo'},inplace=True)

    carteira_df=carteira_df[['ID Cliente','CNPJ','Razão Social', 'Nome Fantasia','Data de Faturamento','Dias do Pedido','ID Antigo',
        'Vendedor Antigo','ID Novo','Vendedor Novo','Seq']].sort_values('Dias do Pedido',ascending=False)    

    return carteira_df

    pass

def Analise(tabelas_df):
    
    carteira_df=Base(tabelas_df)

    carteira_dict={1:carteira_df.loc[carteira_df['Seq']==1],2:carteira_df.loc[carteira_df['Seq']>1]}

    for tabela in carteira_dict.keys():
        
        carteira_df=carteira_dict[tabela]

        carteira_df=carteira_df[['ID Cliente','CNPJ','Razão Social', 'Nome Fantasia','Data de Faturamento','Dias do Pedido','ID Antigo',
        'Vendedor Antigo','ID Novo','Vendedor Novo']]

        cont_clientes=len(carteira_df['ID Cliente'].unique().tolist())

        if(cont_clientes>0):

            carteira_df.to_excel('Carteira.xlsx',index=False)

            temp_path=os.path.join(os.getcwd(),'*.xlsx')

            anexo=glob(temp_path)
            
            if(tabela==1):

                nome='MARA'

                email_to=['COBRANCA@DEMARCHIBRASIL.COM.BR']

                email_cc=['JULIO@DEMARCHIBRASIL.COM.BR','BEATRIZ@DEMARCHIBRASIL.COM.BR']

                pass

            else:

                nome='renato nogueira'

                email_to=['renato.nogueira@demarchisaopaulo.COM.BR']

                email_cc=['eduardo.marfim@DEMARCHIBRASIL.COM.BR','julio@DEMARCHIBRASIL.COM.BR']

                pass

            temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

            data_atual=data.HoraAtual()

            hora=data_atual.hour

            if(hora<=11):

                msg='Bom dia'

                pass


            else:

                msg='Boa tarde'

                pass

            if(tabela==1):

                mensagem=f"""
                
                    <p>{msg};</p>

                    <p>{str(nome).title()}</p>

                    <p>Estou encaminhando uma relação de {cont_clientes} cliente(s) para que tenha ciência, pois essas informações já foram alteradas via banco de dados.</p>

                    <P>Por favor não responder mensagem automática</P>

                    <p>Atenciosamente</p>

                    <p>BOT TI</p>
                
                """

                assunto='Transferência de Carteira'

                pass

            else:

                mensagem=f"""
                
                    <p>{msg};</p>

                    <p>{str(nome).title()}</p>

                    <p>Estou encaminhando uma relação de {cont_clientes} cliente(s) para que seja feita uma análise e identificar se os clientes em anexo devem permanecer com mais de um vendedor. Caso não seja necessário remover o vendedor da coluna 'ID Antigo' do sistema.</p>

                    <P>Por favor não responder mensagem automática</P>

                    <p>Atenciosamente</p>

                    <p>BOT TI</p>
                
                """

                assunto='Análise de Carteira'

                pass

            Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

            if(tabela==1):

                Transferencia(carteira_df)

                pass

            RemoverArquivo('.xlsx')

            pass

        pass

    pass

def Transferencia(carteira_df):

    codigo=carteira_df['ID Antigo'].max()

    base_dict=carteira_df[['ID Cliente','ID Novo']].to_dict()

    querys=dict()

    for i,cd_clien in base_dict['ID Cliente'].items():

        try:
            
            cd_vend=base_dict['ID Novo'][i]
            
            cd_vend=str(cd_vend).strip()
            
            querys['Alterar']="""
            
            UPDATE vend_cli
            SET cd_vend='{0}'
            WHERE cd_clien={1} AND cd_vend='{2}'
            
            """.format(cd_vend,cd_clien,codigo)
                        
            sql.Salvar(query=querys['Alterar'],conectando=conectando)
                
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

if __name__=='__main__':

    tabelas_df=sql.CriarTabela()

    Analise(tabelas_df)

    pass