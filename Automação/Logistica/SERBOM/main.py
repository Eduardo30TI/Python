import win32com.client as win32
import os
from glob import glob
import pandas as pd
from Acesso import Login
from Query import Query
from Email import Email
from Moeda import Moeda
from RemoverArquivo import Remover
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)


email_conta=['expedicao@serbom.com.br','cadastro@serbom.com.br']

querys={

    'Data':

    """
    
    SELECT DATEADD(MONTH,-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)) AS [Data Anterior],
    CONVERT(DATETIME,CAST(GETDATE() AS DATE),101) AS [Data Atual]
    
    """
}

def Main():

    #identificar os e-mails
    outlook=win32.Dispatch('Outlook.Application').GetNamespace('MAPI')

    #caixa de entrada
    inbox=outlook.GetDefaultFolder(6)

    messages=inbox.items

    for message in messages:

        subject=message.Subject
        anexos=message.Attachments

        for anexo in anexos:

            if str(anexo).lower().find('.csv')<0:

                continue

            temp_path=os.path.join(os.getcwd(),str(anexo))

            anexo.SaveAsFile(temp_path)

            pass

        #break

        pass
    
    #mover os e-mails
    emails=[]
    for e in email_conta:
        
        for l in inbox.Items:
            
            if l.SenderEmailAddress.endswith(e):
                                
                emails.append(l)

                pass

            pass

        pass

    path_email=outlook.Folders.Item(1)

    path_email=path_email.Folders[inbox.Name].Folders['SERBOM']

    for m in emails:

        m.move(path_email)

        pass    

    try:

        temp_path=os.path.join(os.getcwd(),'*.csv')

        arquivos=glob(temp_path)

        temp_df=pd.DataFrame()

        for arq in arquivos:    

            df=pd.read_csv(arq,sep=';')

            temp_df=pd.concat([df,temp_df],axis=0,ignore_index=True)

            pass

        df=temp_df

        df.drop_duplicates(inplace=True)

        df.sort_values('Lote',ascending=True,inplace=True)

        df=df.loc[~df['Lote'].isin(['Sub-Total','Total Geral'])]

        df['Validade']=pd.to_datetime(df['Validade'])

        df['Data Entr.']=pd.to_datetime(df['Data Entr.'])

        col_replace=['Peso Liq.','Peso Bruto','Valor Total','Valor Unit.']

        for c in col_replace:

            df[c]=df[c].apply(ConverterValor)

            #break

            pass   

        path_base=os.path.join(os.getcwd(),'Memoria')

        if not os.path.exists(path_base):

            os.makedirs(path_base)

            pass

        path_base=os.path.join(path_base,'Consolidado.xlsx')

        arquivos=glob(path_base)

        if len(arquivos)<=0:

            temp_df.to_excel(path_base,index=False)

            pass

        else:

            temp_df=pd.read_excel(path_base)

            df['Lote']=pd.to_numeric(df['Lote'])

            lotes=df['Lote'].unique().tolist()

            temp_df=temp_df.loc[temp_df['Lote'].isin(lotes)]

            temp_df=pd.concat([df,temp_df],axis=0,ignore_index=True)

            colunas=temp_df.columns.tolist()

            dados_df=sql.CriarTabela(kwargs=querys)

            dt_atual=dados_df['Data'].loc[0,'Data Anterior']

            temp_df['Dias']=temp_df['Validade']-dt_atual

            temp_df['Dias']=temp_df['Dias'].apply(Dias)
            
            vencido_df=pd.DataFrame()

            vencido_df=temp_df.loc[temp_df['Dias']<=90]

            vencido_df.to_excel('Vencido.xlsx',index=False)

            if len(vencido_df)>0:

                email_to=['compras@demarchibrasil.com.br','edson.junior@demarchibrasil.com.br']

                email_cc=['rogerio.felipim@demarchibrasil.com.br','julio@demarchibrasil.com.br','renato@demarchibrasil.com.br']

                msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

                assunto='SERBOM - Produto próximo do vencimento'

                caixas=Moeda.Numero(vencido_df['Qtde'].sum())
                
                lote=Moeda.Numero(len(vencido_df['Lote'].unique().tolsit()))

                nome=''

                mensagem=f"""
                
                <p>{msg};</p>

                <p>{str(nome).title()}</p>

                <p>Segue a relação de produtos que estão próximo do vencimento. Lembrando que temos {lote} lote(s) contendo {caixas} caixa(s).</p>

                <P>Por favor não responder mensagem automática</P>

                <p>Atenciosamente</p>

                <p>BOT TI</p>                

                
                """

                vencido_df.sort_values('Codigo',ascending=True,ignore_index=True,inplace=True)

                vencido_df.to_excel('Vencido.xlsx',index=False)

                temp=os.path.join(os.getcwd(),'Vencido.xlsx')
                
                temp_dict={'To':email_to,'CC':email_cc,'Anexo':[temp]}

                Email.EnviarEmail(mensagem,assunto,temp_dict)
                
                pass

            df[colunas].to_excel(path_base,index=False)

            pass
        
        tipo=['.csv','.xlsx']

        for t in tipo:

            Remover.RemoverArquivo(t)

            pass        

        pass

    except:

        pass
    

    pass

def ConverterValor(val:str):

    val=val.replace(',','.')

    return float(val)
    
    pass

def Dias(val):

    val=str(val).split()

    return int(val[0])

    pass

if __name__=='__main__':

    Main()

    pass