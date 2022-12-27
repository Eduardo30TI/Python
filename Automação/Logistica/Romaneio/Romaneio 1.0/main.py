from Query import Query
from Tempo import DataHora
import os
from glob import glob
import pandas as pd
from Email import Email
from Moeda import Moeda

sql=Query('Netfeira','sqlserver','MOINHO','192.168.0.252')

data=DataHora()

def Base(tabelas_df):

    if(len(tabelas_df['Romaneio'])>0):

        tabelas_df['Romaneio']=tabelas_df['Romaneio'].merge(tabelas_df['Frete'],on='Romaneio',how='inner')[['Romaneio', 'Data da Montagem', 'Data de Saída', 'Data do Retorno',
            'Região', 'ID Motorista', 'Motorista', 'Veículo', 'Placa', 'Pedido',
            'NFe', 'Data de Faturamento', 'Tipo de Pedido', 'Tipo', 'ID Cliente',
            'ID Vendedor', 'SKU', 'Seq', 'Qtde', 'Unid. VDA', 'Qtde VDA',
            'Valor Unitário', 'Total Vendido', 'Peso Bruto', 'Peso Líquido',
            'Situação','Custo KG']]

        tabelas_df['Romaneio']['Frete R$']=tabelas_df['Romaneio'].apply(lambda info: info['Custo KG']*info['Peso Bruto'],axis=1)
        
        tabelas_df['Romaneio'].rename(columns={'Região':'Região do Roteiro'},inplace=True)

        tabelas_df['Romaneio']=tabelas_df['Romaneio'].merge(tabelas_df['Cliente'],on='ID Cliente',how='inner')[['Romaneio', 'Data da Montagem', 'Data de Saída', 'Data do Retorno',
        'Região do Roteiro', 'ID Motorista', 'Motorista', 'Veículo', 'Placa', 'Pedido',
        'NFe', 'Data de Faturamento', 'Tipo de Pedido', 'Tipo', 'ID Cliente','CNPJ', 'Razão Social', 'Nome Fantasia',
        'ID Vendedor', 'SKU', 'Seq', 'Qtde', 'Unid. VDA', 'Qtde VDA',
        'Valor Unitário', 'Total Vendido', 'Peso Bruto', 'Peso Líquido',
        'Situação','Custo KG','Frete R$']]

        tabelas_df['Romaneio']=tabelas_df['Romaneio'].merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['Romaneio', 'Data da Montagem', 'Data de Saída', 'Data do Retorno',
            'Região do Roteiro', 'ID Motorista', 'Motorista', 'Veículo', 'Placa', 'Pedido',
            'NFe', 'Data de Faturamento', 'Tipo de Pedido', 'Tipo', 'ID Cliente','CNPJ', 'Razão Social', 'Nome Fantasia',
            'ID Vendedor','Vendedor', 'Nome Resumido', 'ID Equipe', 'SKU', 'Seq', 'Qtde', 'Unid. VDA', 'Qtde VDA',
            'Valor Unitário', 'Total Vendido', 'Peso Bruto', 'Peso Líquido',
            'Situação','Custo KG','Frete R$']]

        tabelas_df['Romaneio']=tabelas_df['Romaneio'].merge(tabelas_df['Supervisor'],on='ID Equipe',how='inner')[['Romaneio', 'Data da Montagem', 'Data de Saída', 'Data do Retorno',
            'Região do Roteiro', 'ID Motorista', 'Motorista', 'Veículo', 'Placa', 'Pedido',
            'NFe', 'Data de Faturamento', 'Tipo de Pedido', 'Tipo', 'ID Cliente','CNPJ', 'Razão Social', 'Nome Fantasia',
            'ID Vendedor','Vendedor', 'Nome Resumido', 'Equipe','Supervisor', 'SKU', 'Seq', 'Qtde', 'Unid. VDA', 'Qtde VDA',
            'Valor Unitário', 'Total Vendido', 'Peso Bruto', 'Peso Líquido',
            'Situação','Custo KG','Frete R$']]


        tabelas_df['Romaneio']=tabelas_df['Romaneio'].merge(tabelas_df['Produto'],on='SKU',how='inner')[['Romaneio', 'Data da Montagem', 'Data de Saída', 'Data do Retorno',
            'Região do Roteiro', 'ID Motorista', 'Motorista', 'Veículo', 'Placa', 'Pedido',
            'NFe', 'Data de Faturamento', 'Tipo de Pedido', 'Tipo', 'ID Cliente','CNPJ', 'Razão Social', 'Nome Fantasia',
            'ID Vendedor','Vendedor', 'Nome Resumido', 'Equipe','Supervisor', 'SKU','Produto', 'Status', 'Fabricante',
            'Departamento', 'Seção', 'Categoria', 'Linha', 'Seq', 'Qtde', 'Unid. VDA', 'Qtde VDA',
            'Valor Unitário', 'Total Vendido', 'Peso Bruto', 'Peso Líquido',
            'Situação','Custo KG','Frete R$']]

        pass
            
    return tabelas_df

    pass

def Analise(tabelas_df):

    data_atual=data.HoraAtual()

    tabelas_df=Base(tabelas_df)

    if(len(tabelas_df['Romaneio'])>0):

        base_df=tabelas_df['Romaneio']

        motorista=base_df[['ID Motorista','Motorista','Total Vendido','Frete R$']].groupby(['ID Motorista','Motorista'],as_index=False).sum()

        motorista['Qtde NFe']=motorista.apply(lambda info: len(base_df['NFe'].loc[base_df['ID Motorista']==info['ID Motorista']].unique().tolist()),axis=1)

        motorista['Qtde Cliente']=motorista.apply(lambda info: len(base_df['ID Cliente'].loc[base_df['ID Motorista']==info['ID Motorista']].unique().tolist()),axis=1)

        motorista['Qtde Produto']=motorista.apply(lambda info: len(base_df['SKU'].loc[base_df['ID Motorista']==info['ID Motorista']].unique().tolist()),axis=1)    

        frete=Moeda.FormatarMoeda(motorista['Frete R$'].sum())

        valor=Moeda.FormatarMoeda(motorista['Total Vendido'].sum())

        percentual=round(motorista['Frete R$'].sum()/motorista['Total Vendido'].sum(),4)

        nfe=len(base_df['NFe'].unique().tolist())

        pedido=len(base_df['Pedido'].unique().tolist())

        produto=len(base_df['SKU'].unique().tolist())

        caminhao=len(base_df['Veículo'].unique().tolist())

        cliente=len(base_df['ID Cliente'].unique().tolist())

        hora=data_atual.hour

        id_mes=data_atual.month
        
        ano=data_atual.year
        
        nome='edson junior'

        if(hora<=11):

            msg='Bom dia'

            pass


        else:

            msg='Boa tarde'

            pass

        if(id_mes==1):

            id_mes=12

            ano-=1

            pass

        else:

            id_mes-=1

            pass

        mes_nome=data.Mes(id_mes)

        mensagem=f"""
        
        <p>{msg}</p>

        <p>{nome.title()}</p>

        <p>Segue a relação do que foi gasto com frete R$ {frete} o total de notas faturado foi de R$ {valor} cerca de {percentual:.2%}</p>

        <p> - Quantidade NFe: {nfe}</p>

        <p> - Total de Pedido: {pedido}</p>

        <p> - Clientes Atendidos: {cliente}</p>

        <p> - Quantidade de Produtos: {produto}</p>

        <p> - Quantidade de Caminhão: {caminhao}</p>

        <p>Por favor, não enviar ou responder mensagens nesse e-mail pois se trata de mensagem automática</p>

        <p>Atenciosamente BOT TI</p>
        
        """

        email_to=['EDSON.JUNIOR@DEMARCHIBRASIL.COM.BR']

        email_cc=['JULIO@DEMARCHIBRASIL.COM.BR']

        if(pedido>0):

            motorista.to_excel('Motorista.xlsx',index=False,encoding='ISO-8859-1')

            base_df.to_excel('Relação das Entregas.xlsx',index=False,encoding='ISO-8859-1')

            temp_path=os.path.join(os.getcwd(),'*.xlsx')

            anexo=glob(temp_path)

            temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

            Email.EnviarEmail(corpo=mensagem,assunto='Romaneio',kwargs=temp_dict)

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

    tabela_df=sql.CriarTabela()

    Analise(tabela_df)

    pass