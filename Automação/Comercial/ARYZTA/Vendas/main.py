from datetime import datetime
import email
from Acesso import Login
from Query import Query
from Tempo import DataHora
from Moeda import Moeda
from Email import Email
from RemoverArquivo import Remover
from glob import glob
import os
import pandas as pd

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={

    'Vendas':


    """
    
    DECLARE @DTBASE DATETIME,@DTFIM DATETIME,@DTINICIO DATETIME,@DIAS SMALLINT

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    IF DAY(@DTBASE)=1

        BEGIN

            SET @DIAS=DAY(@DTBASE)*-1

            SET @DTFIM=DATEADD(DAY,@DIAS,@DTBASE)

            SET @DTINICIO=CONCAT(YEAR(@DTFIM),'-',MONTH(@DTFIM),'-01')

        END;

    ELSE

        BEGIN

            SET @DTFIM=@DTBASE

            SET @DTINICIO=CONCAT(YEAR(@DTFIM),'-',MONTH(@DTFIM),'-01')

        END;


    SELECT * FROM netfeira.vw_targetestatico
    WHERE [Tipo de Operação]<>'OUTROS' AND [Data de Faturamento] BETWEEN @DTINICIO AND @DTFIM AND Situação<>'EM ABERTO'
    ORDER BY [Data de Faturamento]    
    
    """,

    'Produto':

    """
    
    SELECT * FROM netfeira.vw_produto
    WHERE Fabricante='ARYZTA'
    
    """,

    'Cliente':

    """
    
    SELECT * FROM netfeira.vw_cliente
    
    """,

    'Segmento':

    """
    
    SELECT * FROM netfeira.vw_segmento
    
    """,

    'Vendedor':

    """
    
    SELECT * FROM netfeira.vw_vendedor
    
    """,

    'Supervisor':

    """
    
    SELECT * FROM netfeira.vw_supervisor
    
    """

}

def Main(tabelas_df):

    tabelas_df['Cliente']=tabelas_df['Cliente'].merge(tabelas_df['Segmento'],on='ID Segmento',how='inner')[['ID Cliente', 'CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'Segmento','Canal', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato', 'Limite de Crédito',
        'Principal']]

    tabelas_df['Vendedor']=tabelas_df['Vendedor'].merge(tabelas_df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe','Supervisor']]

    tabelas_df['Vendas']=tabelas_df['Vendas'].merge(tabelas_df['Produto'],on='SKU',how='inner')[['Data de Emissão', 'Data de Faturamento', 'Pedido', 'Nfe', 'ID Empresa',
        'ID Cliente', 'ID Vendedor', 'Tipo de Pedido', 'Tipo de Operação',
        'Tabelas', 'SKU','Cód. Fabricante', 'Produto', 'Status', 'Fabricante',
        'Departamento', 'Seção', 'Categoria', 'Linha', 'Qtde', 'Unid. VDA', 'Qtde VDA', 'Valor VDA',
        'Total Geral', 'Total Venda', 'Comissão R$', 'Margem Bruta R$',
        'Cad Vendedor', 'Situação', 'Peso Bruto KG', 'Peso Líquido KG']]    


    tabelas_df['Vendas']=tabelas_df['Vendas'].merge(tabelas_df['Cliente'],on='ID Cliente',how='inner')[['Data de Emissão', 'Data de Faturamento', 'Pedido', 'Nfe', 'ID Empresa',
        'ID Cliente','CNPJ','Razão Social', 'Nome Fantasia','Matriz','Segmento','Canal','Bairro','Município', 'ID Vendedor', 'Tipo de Pedido', 'Tipo de Operação',
        'Tabelas', 'SKU', 'Cód. Fabricante', 'Produto', 'Status', 'Fabricante',
        'Departamento', 'Seção', 'Categoria', 'Linha', 'Qtde', 'Unid. VDA',
        'Qtde VDA', 'Valor VDA', 'Total Geral', 'Total Venda', 'Comissão R$',
        'Margem Bruta R$', 'Cad Vendedor', 'Situação', 'Peso Bruto KG',
        'Peso Líquido KG']]


    tabelas_df['Vendas']=tabelas_df['Vendas'].merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')[['Data de Emissão', 'Data de Faturamento', 'Pedido', 'Nfe', 'ID Empresa',
        'ID Cliente', 'CNPJ', 'Razão Social', 'Nome Fantasia', 'Matriz',
        'Segmento', 'Canal', 'Bairro', 'Município', 'ID Vendedor','Vendedor', 'Nome Resumido', 'Equipe', 'Supervisor',
        'Tipo de Pedido', 'Tipo de Operação', 'Tabelas', 'SKU',
        'Cód. Fabricante', 'Produto', 'Status', 'Fabricante', 'Departamento',
        'Seção', 'Categoria', 'Linha', 'Qtde', 'Unid. VDA', 'Qtde VDA',
        'Valor VDA', 'Total Geral', 'Situação', 'Peso Bruto KG','Peso Líquido KG']]

    produto_df=pd.DataFrame()

    produto_df=tabelas_df['Vendas'][['SKU', 'Cód. Fabricante', 'Produto','Fabricante','Linha','Qtde','Total Geral','Peso Bruto KG', 'Peso Líquido KG']].groupby(['SKU', 'Cód. Fabricante', 'Produto','Fabricante','Linha'],as_index=False).sum()

    produto_df.sort_values('Qtde',ascending=False,inplace=True,ignore_index=True)
    
    linha_df=pd.DataFrame()

    linha_df=produto_df[['Linha','Qtde','Total Geral','Peso Bruto KG', 'Peso Líquido KG']].groupby(['Linha'],as_index=False).sum()

    linha_df.sort_values('Qtde',ascending=False,inplace=True,ignore_index=True)

    if(len(tabelas_df['Vendas'])>0):

        produto_df.to_excel('Produtos.xlsx',index=False)

        linha_df.to_excel('Linha.xlsx',index=False)

        tabelas_df['Vendas'].to_excel('Histórico de Venda.xlsx',index=False)

        dt_min=tabelas_df['Vendas']['Data de Faturamento'].min()

        dt_max=tabelas_df['Vendas']['Data de Faturamento'].max()

        Enviar(dt_min,dt_max)

        pass

    pass

def Enviar(dt_min,dt_max):

    data_atual=data.HoraAtual()

    hora=data_atual.hour

    msg='Bom dia;' if hora<12 else 'boa tarde;'

    assunto='SELL OUT ARYZTA SP'

    email_to=['rafael.fabiano@grupobimbo.com']

    email_cc=['julio@demarchibrasil.com.br','eduardo.marfim@demarchibrasil.com.br','renato.nogueira@demarchisaopaulo.com.br']

    nome='rafael'

    mensagem=f"""
    
    <p>{msg.title()}</p>

    <p>{str(nome).title()}</p>

    <p>Segue o SELL OUT entre o dia {datetime.strftime(dt_min,'%d/%m/%Y')} até {datetime.strftime(dt_max,'%d/%m/%Y')}.</p>

    <P>Por favor não responder mensagem automática</P>

    <p>Atenciosamente</p>

    <p>BOT TI</p>     
    
    
    """

    temp_path=os.path.join(os.getcwd(),'*.xlsx')

    anexo=glob(temp_path)

    temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

    Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

    Remover.RemoverArquivo('.xlsx')

    pass

if __name__=='__main__':

    tabelas_df=sql.CriarTabela(kwargs=querys)

    Main(tabelas_df)

    pass