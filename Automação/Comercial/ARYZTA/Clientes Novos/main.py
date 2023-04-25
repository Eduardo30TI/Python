from Query import Query
import pandas as pd
from Tempo import DataHora
from Acesso import Login
from RemoverArquivo import Remover
from datetime import timedelta
import os
from glob import glob
from Email import Email

data=DataHora()

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'TargetEstatistico':
    
    """
    
    SELECT * FROM netfeira.vw_estatistico
    WHERE [Situação] IN ('FATURADO','EM ABERTO') AND [Tipo de Operação] IN ('VENDAS','BONIFICAÇÃO','AMOSTRA')    
    
    """,
    
    'Produto':
    
    """
    
    SELECT * FROM netfeira.vw_produto
    
    """,
    
    'Cliente':
    
    """
    
    SELECT * FROM netfeira.vw_cliente
    
    """,
    
    'Segmento':
    
    """
    
    SELECT * FROM netfeira.vw_segmento
    
    """,
    
    'Calendário':
    
    """
        
    DECLARE @DTInicial AS DATETIME,@DTFinal AS DATETIME

    SET @DTInicial='2018-01-01'
    SET @DTFinal= CONCAT(YEAR(GETDATE())+1,'-01-','01')

    ;WITH Calendario (Datas) AS(

    SELECT @DTInicial
    UNION ALL
    SELECT Datas+1
    FROM Calendario WHERE  Datas+1<@DTFinal
    )

    SELECT CONVERT(DATETIME,CAST(Datas AS DATE),101) AS 'Data',YEAR(Datas) AS 'Ano',MONTH(Datas) AS 'Cód. Mês',
    CHOOSE(MONTH(Datas),'JANEIRO','FEVEREIRO','MARÇO','ABRIL','MAIO','JUNHO','JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO') AS 'Mês',
    CHOOSE(MONTH(Datas),'JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ') AS 'Mês Resumido',
    DAY(Datas) AS 'Dia',CONVERT(VARCHAR(7),Datas,120) AS 'Mês Meta',
    DATEPART(DW,Datas) AS 'Cód. Semana',CHOOSE(DATEPART(DW,Datas),'DOM','SEG','TER','QUAR','QUI','SEX','SÁB') AS 'Semana',
    CASE WHEN DATEPART(DW,Datas) IN (7,1) THEN 0 ELSE 1 END AS 'Dias Úteis',
    CASE WHEN MONTH(Datas)<=3 THEN '1º TRIM' WHEN MONTH(Datas)<=6 THEN '2º TRIM' WHEN MONTH(Datas)<=9 THEN '3º TRIM' WHEN MONTH(Datas)<=12 THEN '4º TRIM' END AS 'Trimestre Ano',
    CASE WHEN MONTH(Datas)<=6 THEN '1º SEM' ELSE '2º SEM' END AS 'Semestre Ano',DATEPART(WEEK,Datas) AS 'Semana Ano',
    CONVERT(VARCHAR,DAY(Datas))+'/'+CONVERT(VARCHAR,MONTH(Datas)) AS 'Mês Base'
    FROM Calendario OPTION(MAXRECURSION 10000)    
    
    
    """
    
}

def Base(tabela_df):

    tabela_df['Cliente']=tabela_df['Cliente'].merge(tabela_df['Segmento'],on='ID Segmento',how='inner')[['ID Cliente', 'CNPJ', 'CNPJ Caracter', 'Razão Social', 'Nome Fantasia',
        'Tipo de Cliente', 'Status do Cliente', 'Segmento','Canal', 'Matriz',
        'Crédito', 'Data de Cadastro', 'Primeira Compra', 'Última Compra',
        'Dias Compra', 'Tabela', 'Condição de Pagto', 'Prazo Pagto',
        'Pagamento', 'CEP', 'Endereço', 'Bairro', 'Município', 'Numero',
        'Complemento', 'Região', 'UF', 'DDD', 'Contato']]

    tabela_df['TargetEstatistico']=tabela_df['TargetEstatistico'].merge(tabela_df['Cliente'],on='ID Cliente',how='inner')[['Origem', 'ID Empresa', 'ID Cliente','CNPJ','Razão Social', 'Nome Fantasia','Segmento','Canal', 'ID Vendedor', 'Pedido', 'Nfe',
        'Tipo de Pedido', 'Tipo de Operação', 'ID Cadastro', 'Data de Emissão',
        'Data de Faturamento', 'SKU', 'Seq', 'Qtde', 'Unid. VDA', 'Fator VDA',
        'Preço Tabela', 'Desc %', 'Desc R$', 'Valor VDA', 'Preço Unitário',
        'Total Geral', 'Custo CUE', 'Margem Bruta R$', 'Custo Capado CUE',
        'Total AV', 'PIS R$', 'COFINS R$', 'ICMS R$', 'Verba R$',
        'Margem CTB R$', 'Situação', 'Total Geral AV']]

    tabela_df['TargetEstatistico']=tabela_df['TargetEstatistico'].merge(tabela_df['Produto'],on='SKU',how='inner')[['Origem', 'ID Empresa', 'ID Cliente', 'CNPJ', 'Razão Social',
        'Nome Fantasia', 'Segmento', 'Canal', 'ID Vendedor', 'Pedido', 'Nfe',
        'Tipo de Pedido', 'Tipo de Operação', 'ID Cadastro', 'Data de Emissão',
        'Data de Faturamento', 'SKU','Cód. Fabricante', 'Produto', 'Status', 'Fabricante',
        'Departamento', 'Seção', 'Categoria', 'Linha','Seq', 'Qtde', 'Unid. VDA', 'Fator VDA',
        'Preço Tabela', 'Desc %', 'Desc R$', 'Valor VDA', 'Preço Unitário',
        'Total Geral', 'Custo CUE', 'Margem Bruta R$', 'Custo Capado CUE',
        'Total AV', 'PIS R$', 'COFINS R$', 'ICMS R$', 'Verba R$',
        'Margem CTB R$', 'Situação', 'Total Geral AV']]

    ClienteNovo(tabela_df['TargetEstatistico'],tabela_df)

    ClienteSemCompra(tabela_df['TargetEstatistico'],tabela_df)
    
    pass

def ClienteNovo(temp_df,tabela_df):

    data_atual=data.HoraAtual()

    ano=data_atual.year

    mes=data_atual.month-1

    hora=data_atual.hour

    vendas_df=pd.DataFrame()

    vendas_df=temp_df

    data_min=tabela_df['Calendário']['Data'].loc[(tabela_df['Calendário']['Data'].dt.year==ano)&(tabela_df['Calendário']['Data'].dt.month==mes)].min()

    clientes_df=vendas_df[['ID Cliente','Fabricante','Total Geral']].loc[vendas_df['Data de Faturamento']<data_min].groupby(['ID Cliente','Fabricante'],as_index=False).sum() 

    codigos=clientes_df['ID Cliente'].loc[clientes_df['Fabricante'].str.contains('ARYZTA')].tolist()

    clientes_df=clientes_df.loc[~clientes_df['ID Cliente'].isin(codigos)]

    codigos=vendas_df['ID Cliente'].loc[(vendas_df['Data de Faturamento'].dt.year==ano)&(vendas_df['Data de Faturamento'].dt.month==mes)&((vendas_df['Fabricante'].str.contains('ARYZTA')))].unique().tolist()

    codigos=clientes_df['ID Cliente'].loc[clientes_df['ID Cliente'].isin(codigos)].unique().tolist()

    temp_df=vendas_df[['Segmento','ID Cliente','Razão Social','Fabricante','Linha','Total AV']].loc[(vendas_df['Data de Faturamento'].dt.year==ano)&(vendas_df['Data de Faturamento'].dt.month==mes)&((vendas_df['Fabricante'].str.contains('ARYZTA')))&(vendas_df['ID Cliente'].isin(codigos))].groupby(['Segmento','ID Cliente','Razão Social','Fabricante','Linha'],as_index=False).sum()

    if(len(temp_df)>0):

        temp_df.to_excel('Clientes Novos.xlsx',index=False)

        email_to=['rafael.fabiano@grupobimbo.com']

        email_cc=['eduardo.marfim@demarchibrasil.com.br','renato.nogueira@demarchisaopaulo.com.br']

        if(hora<=11):

            msg='Bom dia'

            pass

        else:

            msg='Boa tarde'

            pass

        nome='rafael'

        if(mes<=0):

            mes_nome=data.Mes(12)

            ano=ano-1

            pass

        else:

            mes_nome=data.Mes(mes)

            pass

        mes_nome=str(mes_nome).title()

        mensagem=f"""
                                    
            <p>{msg};</p>

            <p>{str(nome).title()}</p>

            <p>Tudo bem, em anexo contém cerca de {len(temp_df)} cliente(s) novo(s), referente ao mês de {mes_nome} do ano de {ano}.</p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>BOT TI</p>
                
        """

        assunto='Clientes novos ARYZTA'

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        anexo=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

        Remover.RemoverArquivo('.xlsx')       

        pass

    pass

def ClienteSemCompra(temp_df,tabela_df):

    data_atual=data.HoraAtual()

    ano=data_atual.year

    mes=data_atual.month

    hora=data_atual.hour

    vendas_df=pd.DataFrame()

    vendas_df=temp_df

    if(mes==1):

        data_min=tabela_df['Calendário']['Data'].loc[(tabela_df['Calendário']['Data'].dt.year==ano-1)&(tabela_df['Calendário']['Data'].dt.month==11)].min()

        data_max=tabela_df['Calendário']['Data'].loc[(tabela_df['Calendário']['Data'].dt.year==ano-1)&(tabela_df['Calendário']['Data'].dt.month==12)].max()

        pass

    elif(mes==2):

        data_min=tabela_df['Calendário']['Data'].loc[(tabela_df['Calendário']['Data'].dt.year==ano-1)&(tabela_df['Calendário']['Data'].dt.month==12)].min()

        data_max=tabela_df['Calendário']['Data'].loc[(tabela_df['Calendário']['Data'].dt.year==ano)&(tabela_df['Calendário']['Data'].dt.month==mes-1)].max()

        pass    

    else:

        data_min=tabela_df['Calendário']['Data'].loc[(tabela_df['Calendário']['Data'].dt.year==ano)&(tabela_df['Calendário']['Data'].dt.month==mes-2)].min()

        data_max=tabela_df['Calendário']['Data'].loc[(tabela_df['Calendário']['Data'].dt.year==ano)&(tabela_df['Calendário']['Data'].dt.month==mes-1)].max()

        pass

    vendas_df=vendas_df.loc[(vendas_df['Data de Faturamento'].between(data_min,data_max))&(vendas_df['Fabricante'].str.contains('ARYZTA'))]

    vendas_df=vendas_df.merge(tabela_df['Calendário'],left_on='Data de Faturamento',right_on='Data',how='inner')[['Origem', 'ID Empresa', 'ID Cliente', 'CNPJ', 'Razão Social',
        'Nome Fantasia', 'Segmento', 'Canal', 'ID Vendedor', 'Pedido', 'Nfe',
        'Tipo de Pedido', 'Tipo de Operação', 'ID Cadastro', 'Data de Emissão',
        'Data de Faturamento','Ano','Cód. Mês','Mês', 'SKU', 'Cód. Fabricante', 'Produto', 'Status',
        'Fabricante', 'Departamento', 'Seção', 'Categoria', 'Linha', 'Seq',
        'Qtde', 'Unid. VDA', 'Fator VDA', 'Preço Tabela', 'Desc %', 'Desc R$',
        'Valor VDA', 'Preço Unitário', 'Total Geral', 'Custo CUE',
        'Margem Bruta R$', 'Custo Capado CUE', 'Total AV', 'PIS R$',
        'COFINS R$', 'ICMS R$', 'Verba R$', 'Margem CTB R$', 'Situação',
        'Total Geral AV']]    

    vendas_df=vendas_df[['ID Cliente','Razão Social','Cód. Mês','Segmento','Canal','Total AV']].groupby(['ID Cliente','Razão Social','Cód. Mês','Segmento','Canal'],as_index=False).sum()

    if((mes-1)==0):

        vendas_df.sort_values('Cód. Mês',ascending=False,inplace=True)
        
        pass

    else:
        
        vendas_df.sort_values('Cód. Mês',ascending=True,inplace=True)
        
        pass

    mes_df=vendas_df.pivot(index=['ID Cliente','Razão Social','Segmento','Canal'],columns='Cód. Mês',values='Total AV').reset_index()

    colunas=mes_df.columns.tolist()

    for c in colunas[-2:]:
        
        mes_nome=data.Mes(c)
        
        mes_df.rename(columns={c:mes_nome.title()},inplace=True)
        
        pass

    mes_df=mes_df.loc[mes_df.iloc[:,-1].isnull()]

    mes_df['Status']='SEM COMPRA'

    contagem=mes_df['ID Cliente'].unique().tolist()

    if(hora<=11):

        msg='Bom dia'

        pass

    else:

        msg='Boa tarde'

        pass
    
    nome='rafael'

    email_to=['rafael.fabiano@grupobimbo.com']

    email_cc=['eduardo.marfim@demarchibrasil.com.br','renato.nogueira@demarchisaopaulo.com.br']  

    mensagem=f"""
                                    
            <p>{msg};</p>

            <p>{str(nome).title()}</p>

            <p>Tudo bem, em anexo contém cerca de {len(contagem)} cliente(s) sem compra(s).</p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>BOT TI</p>
                
        """

    if(len(mes_df)>0):

        mes_df.to_excel('Sem Compra.xlsx',index=False)

        assunto='Clientes sem compra ARYZTA'

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        anexo=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}
    
        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

        Remover.RemoverArquivo('.xlsx')

        pass

    pass

if __name__=='__main__':

    data_atual=data.HoraAtual()

    if(data_atual.day==1):

        tabelas=sql.CriarTabela(kwargs=querys)
        
        Base(tabelas)

        pass

    pass