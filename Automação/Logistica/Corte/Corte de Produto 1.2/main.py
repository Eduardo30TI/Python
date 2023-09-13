from Acesso import Login
from Moeda import Moeda
from Email import Email
from Query import Query
from RemoverArquivo import Remover
from Tempo import DataHora
import os
from glob import glob

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

data=DataHora()

querys={
    
    'Faltas':"""
        
    DECLARE @DTBASE DATETIME,@DTFIM DATETIME, @DTINICIO DATETIME

    SET @DTBASE=CONVERT(DATETIME,CAST(GETDATE() AS date),101)

    IF MONTH(GETDATE())=1 AND DAY(GETDATE())=1

        BEGIN

            SET @DTFIM=CONVERT(DATETIME,CAST(
            CONCAT(YEAR(DATEADD(MONTH,MONTH(@DTBASE)*-1,@DTBASE)),'-',MONTH(DATEADD(MONTH,MONTH(@DTBASE)*-1,@DTBASE)),'-31') AS date),101)

            SET @DTINICIO=CONVERT(DATETIME,CAST(CONCAT(YEAR(@DTFIM),'-01-01') AS date),101)

        END
        
    ELSE

        BEGIN

            IF DAY(GETDATE())=1

                BEGIN

                    SET @DTFIM=DATEADD(DAY,DAY(@DTBASE)*-1,@DTBASE)
                
                    SET @DTINICIO=CONVERT(DATETIME,CAST(CONCAT(YEAR(@DTFIM),'-',MONTH(@DTFIM),'-01') AS date),101)

                END

            ELSE

                BEGIN

                    SET @DTFIM=@DTBASE

                    SET @DTINICIO=@DTFIM

                END


        END


    SELECT * FROM netfeira.vw_falta
    WHERE [Data de Falta] BETWEEN @DTINICIO AND @DTFIM
    
    """,
    
    'Vendedores':"""
    
    SELECT * FROM netfeira.vw_vendedor
    
    
    """,
    
    'Supervisor':"""
    
    SELECT * FROM netfeira.vw_supervisor
    
    """
    
}

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

    Analisar(tabela_dict['Faltas'])

    pass

def Analisar(corte_df):

    colunas=[l for l in corte_df.columns.tolist() if str(l).find('mail')>0]

    col_dict={'E-mail':'Nome Resumido','Email Sup':'Supervisor','Email Gerente':'Gerente'}
    
    for coluna in colunas:

        emails=[l for l in corte_df[coluna].unique().tolist() if l!='']

        if(len(emails)<=0):

            continue

        for email in emails:

            email_to=[]

            email_cc=[]

            temp_df=corte_df.loc[corte_df[coluna]==email]

            produto_df=temp_df[['SKU','Produto','Total do Pedido']].groupby(['SKU','Produto'],as_index=False).agg({'Total do Pedido':'sum'})

            produto_df.sort_values('Total do Pedido',ascending=False,inplace=True)
            
            nome=temp_df[col_dict[coluna]].unique().tolist()

            nome=nome[-1]

            sku=Moeda.Numero(len(temp_df['SKU'].unique().tolist()))

            total=Moeda.FormatarMoeda(temp_df['Total do Pedido'].sum())

            data_atual=data.HoraAtual()

            hora=data_atual.hour

            id_mes=data_atual.month

            ano=data_atual.month

            dia=data_atual.day

            if(hora<12):

                msg='Bom dia'

                pass

            else:

                msg='Boa tarde'

                pass

            if(id_mes==1):

                ano=ano-1

                id_mes=12

                mes=data.Mes(id_mes)

                assunto=f'Corte de Produto referênte a {mes.title()} de {ano}'

                mensagem=f"""
                                
                <p>{msg};</p>

                <p>{str(nome).title()}</p>

                <p>Foram identificados cerca de {sku} itens que foram cortados, referente {mes.title()} de {ano}. Totalizando R$ {total}</p>

                <P>Por favor não responder mensagem automática</P>

                <p>Atenciosamente</p>

                <p>BOT TI</p>                
                
                """

                pass

            else:

                if(dia==1):

                    id_mes-=1

                    mes=data.Mes(id_mes)

                    assunto=f'Corte de Produto referênte a {mes.title()} de {ano}'

                    assunto=assunto.title()                    

                    mensagem=f"""
                                    
                    <p>{msg};</p>

                    <p>{str(nome).title()}</p>

                    <p>Foram identificados cerca de {sku} itens que foram cortados, referente {mes.title()} de {ano}. Totalizando R$ {total}</p>

                    <P>Por favor não responder mensagem automática</P>

                    <p>Atenciosamente</p>

                    <p>BOT TI</p>                
                    
                    """             
                    
                    pass

                else:

                    data_form=data_atual.strftime('%d/%m/%Y')

                    assunto='Corte de Produto'

                    mensagem=f"""
                                    
                    <p>{msg};</p>

                    <p>{str(nome).title()}</p>

                    <p>Foram identificados cerca de {sku} itens que foram cortados, referente ao dia {data_form}. Totalizando R$ {total}</p>

                    <P>Por favor não responder mensagem automática</P>

                    <p>Atenciosamente</p>

                    <p>BOT TI</p>                
                    
                    """                    

                    pass

                pass

            email_to.append(email)

            if(coluna=='Email Gerente'):

                email_cc=['julio@demarchibrasil.com.br','edson.junior@demarchibrasil.com.br']

                temp_df.to_excel('Corte Geral.xlsx',index=False,encoding='ISO-8859-1')

                pass

            else:

                arq=f'{str(nome).title()}.xlsx'

                temp_df.to_excel(arq,index=False,encoding='ISO-8859-1')

                pass
            
            produto_df.to_excel('Produto.xlsx',index=False,encoding='ISO-8859-1')

            temp_path=os.path.join(os.getcwd(),'*.xlsx')

            anexo=glob(temp_path)

            temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

            Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

            Remover.RemoverArquivo('.xlsx')
            
            pass

        pass

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Base(tabelas)

    pass