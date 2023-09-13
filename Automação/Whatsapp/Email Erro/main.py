from Acesso import Login
from Query import Query
from Moeda import Moeda
import pandas as pd
import os
from glob import glob
from datetime import datetime
import win32com.client as win32
import re

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'cliente':

    """

    SELECT [ID Cliente],[Razão Social],[Nome Fantasia],[E-mail Cliente],DDD,Contato
    FROM netfeira.vw_cliente

    """
}

def main():

    df=sql.GetDados(querys=querys,tabela=['cliente'])
    df['cliente']['E-mail Cliente']=df['cliente']['E-mail Cliente'].apply(lambda info: str(info).strip())

    outlook=win32.Dispatch('Outlook.Application').GetNamespace('MAPI')

    #mapear caixa de entrada
    inbox=outlook.GetDefaultFolder(6)

    lista=[]

    indice=0

    #criar pasta
    for e in inbox.Folders:

        path=str(e.Name).lower()

        if path=='erro de envio':

            indice=1
            
            break

        pass

    if indice==0:

        inbox.Folders.Add('Erro de Envio')

        pass

    #varrer email
    for f in inbox.Items:

        subject=str(f.Subject)

        if subject.find('Undelivered')<0:

            continue

        body=str(f.Body)

        padrao=re.compile('(<.+):')
        email=str(re.findall(padrao,body)[-1])

        for r in ['<','>']:

            email=email.replace(r,'')
            
            pass

        email=email.strip().upper()

        lista.append(email)

        #mover email
        path_email=inbox.Folders['Erro de Envio']
        f.move(path_email)
                
        pass

    df['cliente']=df['cliente'].loc[df['cliente']['E-mail Cliente'].isin(lista)]

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

    if len(df['cliente'])>0:

        df['cliente'].to_excel('Erro de Envio.xlsx',index=False)

        temp_path=os.path.join(os.getcwd(),'Erro de Envio.xlsx')
                
        msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'
        clientes=Moeda.Numero(len(df['cliente']['ID Cliente'].unique().tolist()))

        mensagem=f'{msg} financeiro tudo bem? Aqui é a Iris estou em caminhando uma relação que contém {clientes} cliente(s) que não foi possível o envio da cobrança, por favor verificar se as informações de envio estão corretas. Grato pela colaboração e tenha um excelente dia.'

        whatsapp_df.loc[len(whatsapp_df)]=['Financeiro','11','942986681',mensagem,temp_path]
        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)

        pass
    

    pass


if __name__=='__main__':

    main()

    pass