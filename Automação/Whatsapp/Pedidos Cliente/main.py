from Acesso import Login
from Query import Query
import pandas as pd
import os
from glob import glob
from datetime import datetime
from Moeda import Moeda

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Pedidos':

    """

    SELECT v.[Data de Faturamento],v.Pedido,v.[ID Cliente],c.[Nome Fantasia],
    v.SKU,p.Produto,v.[Valor VDA],v.[Unid. VDA],v.[Qtde. VDA],v.[Total Venda]
    FROM netfeira.vw_targetestatistico v
    INNER JOIN netfeira.vw_produto p ON v.SKU=p.SKU
    INNER JOIN netfeira.vw_cliente c ON v.[ID Cliente]=c.[ID Cliente]
    WHERE [ID Situação]='AB' AND [Data de Faturamento]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

    
    """,

    'Telefone':

    """

    SELECT b.cd_clien AS [ID Cliente],b.ddd AS [DDD],
    CASE WHEN b.ddd=LEFT(b.numero,2) THEN RIGHT(b.numero,9) ELSE b.numero END AS [Contato Cliente]
    FROM (

        SELECT a.cd_clien,a.tp_tel,a.ddd,a.numero,
        COUNT(a.numero)OVER(PARTITION BY a.numero) AS seq
        FROM tel_cli a

    )b
    INNER JOIN tp_tel c ON b.tp_tel=c.tp_tel
    WHERE b.seq=1 AND LEN(LEFT(b.numero,9))=9
    AND c.descricao='CELULAR'

    """
}

def Main():

    df=sql.CriarTabela(kwargs=querys)

    temp_path=os.path.join(os.getcwd(),'Consolidado.csv')
    arq=glob(temp_path)
    
    df['Pedidos']=df['Pedidos'].merge(df['Telefone'],on='ID Cliente')

    for c in ['Pedido','Contato Cliente']:

        df['Pedidos'][c]=df['Pedidos'][c].astype(str)

        pass

    df['Pedidos']['ID']=df['Pedidos']['Pedido']+df['Pedidos']['Contato Cliente']
    
    temp_df=pd.DataFrame()

    lista=[]

    if len(arq)>0:

        temp_df=pd.read_csv(arq[-1],encoding='UTF-8')
        temp_df['ID']=temp_df['ID'].astype(str)

        codigos=temp_df['ID'].unique().tolist()
        lista=temp_df['Nome Fantasia'].unique().tolist()

        df['Pedidos']=df['Pedidos'].loc[~df['Pedidos']['ID'].isin(codigos)]

        pass

    if len(df['Pedidos'])>0:
        
        pedidos=df['Pedidos']['ID'].unique().tolist()

        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        for p in pedidos:

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            nome=df['Pedidos'].loc[df['Pedidos']['ID']==p,'Nome Fantasia'].unique().tolist()[-1]
            pedido=df['Pedidos'].loc[df['Pedidos']['ID']==p,'Pedido'].unique().tolist()[-1]
            ddd=df['Pedidos'].loc[df['Pedidos']['ID']==p,'DDD'].unique().tolist()[-1]
            telefone=df['Pedidos'].loc[df['Pedidos']['ID']==p,'Contato Cliente'].unique().tolist()[-1]
            dt_ped=df['Pedidos'].loc[df['Pedidos']['ID']==p,'Data de Faturamento'].unique().tolist()[-1]
            dt_ped=datetime.strftime(dt_ped,'%d/%m/%Y')

            vl_total=Moeda.FormatarMoeda(df['Pedidos'].loc[df['Pedidos']['ID']==p,'Total Venda'].sum())

            mensagem=f'{msg} sr(a) *{nome}* meu nome é Iris um chatbot desenvolvido pela DE MARCHI SP e venho te parabenizar pela sua preferência. Abaixo você tera informações sobre seu pedido. Qualquer dúvida você pode entrar em contato: (11) 4673-2000 para obter informações sobre seu pedido com um de nossos colaboradores.\n\nPedido: *{pedido}* - Data do Pedido: *{dt_ped}*\nTotal do Pedido: *R$ {vl_total}*' if not nome in lista else f'Olá sr(a) *{nome}* aqui quem fala é a Iris venho te parabenizar pela sua preferência. Abaixo você tera informações sobre seu pedido. Qualquer dúvida você pode entrar em contato: (11) 4673-2000 para obter informações sobre seu pedido com um de nossos colaboradores.\n\nPedido: *{pedido}* - Data do Pedido: *{dt_ped}*\nTotal do Pedido: *R$ {vl_total}*'

            for c in df['Pedidos'].loc[df['Pedidos']['ID']==p,'Produto'].unique().tolist():

                unidade=df['Pedidos'].loc[(df['Pedidos']['ID']==p)&(df['Pedidos']['Produto']==c),'Unid. VDA'].unique().tolist()[-1]
                vl_venda=Moeda.FormatarMoeda(df['Pedidos'].loc[(df['Pedidos']['ID']==p)&(df['Pedidos']['Produto']==c),'Valor VDA'].unique().tolist()[-1])

                vl_total=Moeda.FormatarMoeda(df['Pedidos'].loc[(df['Pedidos']['ID']==p)&(df['Pedidos']['Produto']==c),'Total Venda'].sum())
                qtde=Moeda.Numero(df['Pedidos'].loc[(df['Pedidos']['ID']==p)&(df['Pedidos']['Produto']==c),'Qtde. VDA'].sum())

                mensagem+=f'\n\n.{c}\nvalor unitário: R$ {vl_venda}\nquantidade: {qtde}\ntotal: R$ {vl_total}'

                pass

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,'']

            #break

            pass

        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)
        
        temp_df=pd.concat([temp_df,df['Pedidos']],axis=0,ignore_index=True)
        temp_df.to_csv(temp_path,index=False,encoding='UTF-8')

        pass


    pass



if __name__=='__main__':

    Main()

    pass