import win32com.client as win32
import os
from glob import glob
import pandas as pd
from datetime import datetime,timedelta

def anexo():

    #localizar o email na caixa de entrada

    outlook=win32.Dispatch('Outlook.Application').GetNamespace('MAPI')

    inbox=outlook.GetDefaultFolder(6)
    mensagens=inbox.items
    
    for msg in mensagens:

        subject=str(msg.Subject)
        
        if subject.find('NETFEIRA')<0:

            continue


        #criar a pasta
        resp=False
        for f in inbox.Folders:

            if str(f.name)=='Agenda':

                resp=True

                break

            pass

        if resp==False:

            inbox.Folders.Add('Agenda')

            pass

        #mover o email

        path_email=inbox.Folders['Agenda']

        msg.move(path_email)

        pass


    mensagens=inbox.Folders['Agenda'].items

    for msg in mensagens:

        ano_now=str(datetime.now().year)
        
        subject=str(msg.Subject)

        if subject.find(ano_now)<0:

            continue

        #fazer download do anexo

        anexos=msg.Attachments

        df=pd.DataFrame()
        
        for a in anexos:

            temp_path=os.path.join(os.getcwd(),str(a))

            a.SaveAsFile(temp_path)

            arquivos=glob('*.csv*')

            for arq in arquivos:

                temp_df=pd.read_csv(arq,encoding='UTF-8')
                df=pd.concat([df,temp_df],axis=0,ignore_index=True)
                os.remove(arq)

                pass

            pass

        cont=0

        for i in df.index.tolist():

            cont+=1

            df.loc[i,'ROW']=int(cont)

            pass

        for i in df['ID'].unique().tolist():

            max=df.loc[df['ID']==i,'ROW'].max()
            df.loc[df['ID']==i,'MAX']=max

            pass

        df['AB']=df.apply(lambda info: 1 if info['ROW']==info['MAX'] else 0,axis=1)
        df=df.loc[(df['AB']==1)&(df['RECEBIDO']=='N')]
        
        return df
                
        pass

    pass

def main():

    df=anexo()
    
    temp_path=os.path.join(os.getcwd(),'memoria.xlsx')
    arq=glob(temp_path)

    temp_df=pd.DataFrame()

    dt_now=datetime.now()-timedelta(days=1)

    df['DT_AGENDA']=pd.to_datetime(df['DT_AGENDA'])
    df=df.loc[df['DT_AGENDA'].dt.date==dt_now.date()]

    if len(arq)>0:

        temp_df=pd.read_excel(arq[-1])
        lista=temp_df['ID'].unique().tolist()

        df=df.loc[~df['ID'].isin(lista)]
            
        pass

    if len(df)>0:
        
        contatos={'Compras':'11942987717','Omário':'11940240053','Edson':'11974660844'}

        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        for i in df.index.tolist():

            fornec=df.loc[i,'FORNECEDOR']
            dt_agenda=datetime.strftime(df.loc[i,'DT_AGENDA'],'%d/%m/%Y')
            qtde=df.loc[i,'QTDE']
            tipo=str(df.loc[i,'TIPO']).lower()

            for k,v in contatos.items():

                ddd=v[:2]
                telefone=v[3:]

                msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

                mensagem=f'{msg} {k} aqui é a Iris tudo bem? Hoje: *{dt_agenda}*\n está previsto para chegar o fornecedor *{fornec}* no total de {qtde} {tipo}(s)'

                whatsapp_df.loc[len(whatsapp_df)]=[k,ddd,telefone,mensagem,'']

                pass

            pass


        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)
            
        temp_df=pd.concat([temp_df,df],axis=0,ignore_index=True)
        temp_df.to_excel(temp_path)

        pass

    pass

if __name__=='__main__':

    main()

    pass