from Acesso import Login
from Query import Query
from Moeda import Moeda
import pandas as pd
import os
from glob import glob
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Pedidos':

    """
    
    SELECT er.[Data de Emissão],er.[Tipo de Pedido],er.[Tipo],er.Origem,
    er.[ID Usuário],us.[Nome Resumido] AS [Usuário]
    ,er.Empresa,er.Pedido,
    er.[ID Cliente],cli.[Nome Fantasia],cli.Matriz,
    er.[ID Vendedor],vend.Vendedor,sup.Equipe,sup.Supervisor,
    er.[Total Geral]
    FROM netfeira.vw_pedidos_errados er
    INNER JOIN netfeira.vw_vendedor vend ON er.[ID Vendedor]=vend.[ID Vendedor]
    INNER JOIN netfeira.vw_cliente cli ON er.[ID Cliente]=cli.[ID Cliente]
    INNER JOIN netfeira.vw_supervisor sup ON vend.[ID Equipe]=sup.[ID Equipe]
    INNER JOIN netfeira.vw_usuario us ON er.[ID Usuário]=us.[ID Usuário]
    ORDER BY [Data de Emissão]
    
    """,

    'Equipe':


    """
    
    SELECT Equipe,Supervisor,[DDD Sup],[Telefone Sup]
    FROM netfeira.vw_supervisor
    WHERE Equipe LIKE '%9%'
    
    """

}

def Main(df):

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    temp_path=os.path.join(os.getcwd(),'consolidado.csv')

    if datetime.now().day==1 and os.path.exists(temp_path):

        os.remove(temp_path)

        pass

    else:

        if datetime.now().day!=1:

            if not os.path.exists(temp_path):

                df['Pedidos'].to_csv(temp_path,index=False)

                temp_df=pd.DataFrame()

                pass

            else:

                temp_df=pd.read_csv(temp_path)

                lista=temp_df['Pedido'].unique().tolist()

                df['Pedidos']=df['Pedidos'].loc[~df['Pedidos']['Pedido'].isin(lista)]

                pass

            pedidos=Moeda.Numero(len(df['Pedidos']['Pedido'].unique().tolist()))

            total=Moeda.FormatarMoeda(df['Pedidos']['Total Geral'].sum())

            whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

            nome=str(df['Equipe']['Supervisor'].tolist()[-1]).title()

            ddd=df['Equipe']['DDD Sup'].tolist()[-1]

            telefone=df['Equipe']['Telefone Sup'].tolist()[-1]

            mensagem=f"""
            
            Divergência de Digitação

            {msg} {nome} tudo bem? Estou te encaminhando uma relação contendo {pedidos} pedido(s) para fazer uma verificação se estão para os vendedor(es) corretos. Totalizando R$ {total}
                    
            """
            
            if len(df['Pedidos'])>0:

                temp_df=pd.concat([temp_df,df['Pedidos']],axis=0,ignore_index=True)

                temp_path=os.path.join(os.getcwd(),'Divergência.xlsx')

                df['Pedidos'].to_excel(temp_path,index=False)
                
                whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,temp_path]            

                whatsapp_df.to_excel('whatsapp.xlsx',index=False)

                temp_path=os.path.join(os.getcwd(),'Consolidado.csv')

                temp_df.to_csv(temp_path,index=False,encoding='UTF-8')
                
                pass

            pass

        pass

    pass

if __name__=='__main__':

    tabelas=sql.CriarTabela(kwargs=querys)

    Main(tabelas)

    pass