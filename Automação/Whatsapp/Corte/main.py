from Acesso import Login
from Query import Query
from Moeda import Moeda
import pandas as pd
import os
from datetime import datetime,timedelta

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={
    
    'Faltas':"""
        
        SELECT * FROM netfeira.vw_falta
        WHERE [Data de Falta]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)
    
    """,
    
    'Vendedores':"""
    
    SELECT vend.[ID Vendedor],vend.[Nome Resumido],
	vend.[ID Equipe],vend.DDD,vend.Telefone,Categoria
	FROM netfeira.vw_vendedor vend
    WHERE vend.[Status do Vendedor]='ATIVO'
    
    
    """,
    
    'Supervisor':"""
    
    SELECT [ID Equipe],Equipe,[ID Sup],Supervisor,[DDD Sup],[Telefone Sup],[ID Gerente],Gerente,[DDD Gerente],[Telefone Gerente]
    FROM netfeira.vw_supervisor
    
    """
    
}

def Main(tabelas_df):

    tabelas_df['Vendedores']=tabelas_df['Vendedores'].merge(tabelas_df['Supervisor'],on='ID Equipe',how='inner')[['ID Vendedor', 'Nome Resumido','Categoria', 'DDD', 'Telefone',
       'Equipe', 'ID Sup', 'Supervisor', 'DDD Sup',
       'Telefone Sup', 'ID Gerente', 'Gerente', 'DDD Gerente',
       'Telefone Gerente']]

    tabelas_df['Faltas']=tabelas_df['Faltas'].merge(tabelas_df['Vendedores'],on='ID Vendedor',how='inner')[['Data e Hora', 'ID Cliente','Nome Fantasia','ID Vendedor','Nome Resumido','Categoria', 'Equipe','ID Sup', 'Supervisor', 'DDD Sup',
       'Telefone Sup', 'ID Gerente', 'Gerente', 'DDD Gerente',
       'Telefone Gerente', 'DDD', 'Telefone', 'Pedido',
       'SKU', 'Produto', 'Unid. VDA', 'Qtde. VDA', 'Valor Unitário',
       'Total do Pedido']]

    colunas={'ID Vendedor':'ID Sup','ID Sup':'ID Gerente','ID Gerente':'ID Gerente'}

    col_nome={'ID Vendedor':'Nome Resumido','ID Sup':'Supervisor','ID Gerente':'Gerente'}

    col_ddd={'ID Vendedor':'DDD','ID Sup':'DDD Sup','ID Gerente':'DDD Gerente'}

    col_tel={'ID Vendedor':'Telefone','ID Sup':'Telefone Sup','ID Gerente':'Telefone Gerente'}

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    for col1,col2 in colunas.items():

        if(len(tabelas['Faltas'])<=0):

            continue

        codigos=tabelas['Faltas'][col1].loc[(tabelas_df['Faltas']['Categoria']=='CLT')&(~tabelas_df['Faltas']['Telefone'].isnull())].unique().tolist()
        
        for c in codigos:
            
            temp_df=pd.DataFrame()

            id=tabelas_df['Faltas'][col2].loc[tabelas_df['Faltas'][col1]==c].unique().tolist()[-1]

            if(col1=='ID Sup'):

                if(c==id):

                    continue

                nome=str(tabelas_df['Faltas'][col_nome[col1]].loc[tabelas_df['Faltas'][col1]==c].unique().tolist()[-1]).title()
                
                ddd=tabelas_df['Faltas'][col_ddd[col1]].loc[tabelas_df['Faltas'][col1]==c].unique().tolist()[-1]

                telefone=tabelas_df['Faltas'][col_tel[col1]].loc[tabelas_df['Faltas'][col1]==c].unique().tolist()[-1]

                pass

            else:

                nome=str(tabelas_df['Faltas'][col_nome[col1]].loc[tabelas_df['Faltas'][col1]==c].unique().tolist()[-1]).title()

                ddd=tabelas_df['Faltas'][col_ddd[col1]].loc[tabelas_df['Faltas'][col1]==c].unique().tolist()[-1]

                telefone=tabelas_df['Faltas'][col_tel[col1]].loc[tabelas_df['Faltas'][col1]==c].unique().tolist()[-1]   
                    
                pass

            temp_df=tabelas_df['Faltas'][['Data e Hora', 'ID Cliente','Nome Fantasia','ID Vendedor','Nome Resumido', 'Equipe','Pedido',
            'SKU', 'Produto', 'Unid. VDA', 'Qtde. VDA', 'Valor Unitário',
            'Total do Pedido']].loc[tabelas_df['Faltas'][col1]==c]
            
            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            dt_atual=datetime.strftime(datetime.now().date(),'%d/%m/%Y')

            assunto='Corte de Produto'

            total=Moeda.FormatarMoeda(temp_df['Total do Pedido'].sum())

            pedido=Moeda.Numero(len(temp_df['Pedido'].unique().tolist()))
            
            mensagem=f"""
            
            {assunto}

            {msg}

            {nome} tudo bem, foram identificados referente ao {dt_atual} cerca de {pedido} pedido(s) que foram cortados dando um total de R$ {total}.
            
            """

            temp_df.sort_values('Data e Hora',ascending=True,inplace=True)

            temp_df.to_excel(f'{nome}.xlsx',index=False,encoding='UTF-8')

            temp_path=os.path.join(os.getcwd(),f'{nome}.xlsx')

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,temp_path]

            pass

        pass

    whatsapp_df.to_excel('whatsapp.xlsx',index=False,encoding='UTF-8')
    
    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)
    
    pass