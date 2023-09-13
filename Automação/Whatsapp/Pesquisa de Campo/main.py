from Acesso import Login
from Query import Query
import pandas as pd
from glob import glob
import os
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Vendedor':

    """
    
    SELECT v.[ID Vendedor],v.[Nome Resumido],v.DDD,v.Telefone 
    FROM netfeira.vw_vendedor v
    WHERE v.[Status do Vendedor]='ATIVO' AND v.Telefone IS NOT NULL
    
    """
}

def Main():

    df=sql.CriarTabela(kwargs=querys)

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    for i in df['Vendedor'].index.tolist():

        msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

        nome=df['Vendedor'].loc[i,'Nome Resumido']
        ddd=df['Vendedor'].loc[i,'DDD']
        telefone=df['Vendedor'].loc[i,'Telefone']

        mensagem=f'{msg} {str(nome).title()} tudo bem? Eu sou Iris o chatbot da DE MARCHI SP estou te encaminhando um link com uma pesquisa de campo que precisa ser preenchido. Essa pesquisa é bem simples e rápida o link está abaixo:\n\nhttps://docs.google.com/forms/d/e/1FAIpQLSdIzIYkm6O0VZkMFrAFu6qbj8C1-ZT1RfKY5U3ASmrI-O3J4w/viewform'

        whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,'']

        pass

    whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)

    pass

if __name__=='__main__':

    Main()

    pass