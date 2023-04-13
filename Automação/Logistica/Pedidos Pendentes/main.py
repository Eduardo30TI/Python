from Acesso import Login
from Query import Query
from RemoverArquivo import Remover
from Email import Email
from Moeda import Moeda
import pandas as pd
from glob import glob
from datetime import datetime
import os

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Pedidos':

    """
    
    SELECT * FROM netfeira.vw_targetestatistico
    WHERE [ID Situação]='AB' AND [Data de Entrega]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101) 
    AND [Data de Emissão]=DATEADD(DAY,-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101))
    AND [Tipo de Operação]<>'OUTROS'    
    
    """,

    'Vendedor':

    """
    
    SELECT * FROM netfeira.vw_vendedor
    
    """,

    'Supervisor':

    """
    
    SELECT * FROM netfeira.vw_supervisor
    
    """,

    'Produto':

    """
    
    SELECT * FROM netfeira.vw_produto
    
    """,

    'Cliente':
    
    """
    
    SELECT * FROM netfeira.vw_cliente
    
    """    

}


def Main(tabelas_df):

    tabelas_df['Vendedor']=tabelas_df['Vendedor'].merge(tabelas_df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Vendedor', 'Nome Resumido', 'Equipe', 'E-mail',
        'Status do Vendedor','ID Sup', 'Supervisor', 'Email Sup',
        'ID Gerente', 'Gerente', 'Email Gerente']]


    tabelas_df['Pedidos']=tabelas_df['Pedidos'].merge(tabelas_df['Produto'],on='SKU',how='inner')[['Origem', 'Situação Entrega', 'ID Situação', 'Situação', 'Pedido',
        'NFe', 'Tipo de Pedido', 'Tipo de Operação', 'Tabelas',
        'Data de Emissão', 'Data de Faturamento', 'Data de Entrega',
        'ID Empresa', 'ID Cliente', 'ID Vendedor', 'SKU','Produto','Fabricante',
        'Departamento', 'Seção', 'Categoria', 'Linha', 'Seq', 'Qtde',
        'Unid. VDA', 'Fator', 'Qtde. VDA', 'Valor VDA', 'Total Venda',
        'Total AV', 'MG CRP', 'Margem CUE', 'Margem CMP', 'Comsissão R$',
        'COFINS R$', 'PIS R$', 'ICMS R$', 'ICMS ST R$', 'IPI R$',
        'Peso Bruto KG', 'Peso Líquido KG', 'Total Geral']]

    tabelas_df['Pedidos']=tabelas_df['Pedidos'].merge(tabelas_df['Vendedor'],on='ID Vendedor',how='inner')

    tabelas_df['Pedidos']=tabelas_df['Pedidos'].merge(tabelas_df['Cliente'],on='ID Cliente',how='inner')[['Origem', 'Situação Entrega', 'ID Situação', 'Situação', 'Pedido',
        'NFe', 'Tipo de Pedido', 'Tipo de Operação', 'Tabelas',
        'Data de Emissão', 'Data de Faturamento', 'Data de Entrega',
        'ID Empresa', 'ID Cliente','Razão Social', 'Nome Fantasia', 'ID Vendedor','Vendedor',
        'Nome Resumido', 'Equipe', 'E-mail', 'Data de Cadastro',
        'Status do Vendedor', 'ID Sup', 'Supervisor',
        'Email Sup', 'ID Gerente', 'Gerente', 'Email Gerente', 'SKU', 'Produto',
        'Fabricante', 'Departamento', 'Seção', 'Categoria', 'Linha', 'Seq',
        'Qtde', 'Unid. VDA', 'Fator', 'Qtde. VDA', 'Valor VDA', 'Total Geral']]


    tabelas_df['Consolidado']=tabelas_df['Pedidos'].groupby(['ID Vendedor','Nome Resumido','Equipe','E-mail','ID Sup',
        'Supervisor', 'Email Sup', 'ID Gerente', 'Gerente', 'Email Gerente'],as_index=False).agg({'Total Geral':'sum'})

    tabelas_df['Consolidado']['Pedido']=tabelas_df['Consolidado']['ID Vendedor'].apply(lambda info:len(tabelas_df['Pedidos']['Pedido'].loc[tabelas_df['Pedidos']['ID Vendedor']==info].unique().tolist()))

    tabelas_df['Consolidado']['Cliente']=tabelas_df['Consolidado']['ID Vendedor'].apply(lambda info:len(tabelas_df['Pedidos']['ID Cliente'].loc[tabelas_df['Pedidos']['ID Vendedor']==info].unique().tolist()))

    if(len(tabelas_df['Consolidado'])>0):

        colunas={'E-mail':'ID Vendedor','Email Sup':'ID Sup','Email Gerente':'ID Gerente'}

        col_nomes={'ID Vendedor':'Nome Resumido','ID Sup':'Supervisor','ID Gerente':'Gerente'}

        for key,value in colunas.items():

            emails=[l for l in tabelas_df['Consolidado'][key].unique().tolist() if l!='']

            for email in emails:

                msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

                assunto='Pedidos não faturados'

                codigo=tabelas_df['Consolidado'][value].loc[tabelas_df['Consolidado'][key]==email].unique().tolist()

                nome=tabelas_df['Consolidado'][col_nomes[value]].loc[tabelas_df['Consolidado'][value]==codigo[-1]].unique().tolist()

                total=tabelas_df['Consolidado']['Total Geral'].loc[tabelas_df['Consolidado'][value]==codigo[-1]].sum()

                pedido=tabelas_df['Consolidado']['Pedido'].loc[tabelas_df['Consolidado'][value]==codigo[-1]].sum()

                pedido=Moeda.Numero(pedido)

                total=Moeda.FormatarMoeda(total)

                mensagem=f"""
                                
                <p>{msg};</p>

                <p>{str(nome[-1]).title()}</p>

                <p>Foram identificados cerca de {pedido} pedidos que não foram faturados. Totalizando R$ {total}.</p>

                <P>Por favor não responder mensagem automática</P>

                <p>Atenciosamente</p>

                <p>BOT TI</p>                
                
                
                """

                if(value!='ID Vendedor'):

                    tabelas_df['Consolidado'].loc[tabelas_df['Consolidado'][value]==codigo[-1]].to_excel('Equipes.xlsx',index=False)

                    pass

                tabelas_df['Pedidos'].loc[tabelas_df['Pedidos'][value]==codigo[-1]].to_excel(f'{str(nome[-1]).title()}.xlsx',index=False)

                temp_path=os.path.join(os.getcwd(),'*.xlsx')

                anexo=glob(temp_path)

                email_to=[email]
                
                email_cc=[] if value!='ID Gerente' else ['julio@demarchibrasil.com.br','athos.alcantara@demarchisaopaulo.com.br','edson.junior@demarchibrasil.com.br'] 

                temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

                Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

                Remover.RemoverArquivo('.xlsx')

                pass

            pass

        pass

    pass


if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass