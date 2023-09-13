from __future__ import print_function
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime
from Email import Email
from Moeda import Moeda
from RemoverArquivo import Remover
from glob import glob
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1bGFXbWKGpkJD5SswHgy4aWmRmzqaxsapZpFBFBsydUI'
SAMPLE_RANGE_NAME = 'Controle!A1:L'

path_json=os.path.join(os.getcwd(),'JSON','credencial.json')

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path_json, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


    try:

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result=sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,range=SAMPLE_RANGE_NAME).execute()

        df=pd.DataFrame(data=result['values'])
        df.columns=df.iloc[0].tolist()
        df.drop(index=0,inplace=True)

        dt_atual=datetime.now().date()
        
        df['Data de Recebimento']=pd.to_datetime(df['Data de Recebimento'])

        df['Valor do Malote']=df['Valor do Malote'].apply(lambda info: float(str(info).replace(',','.')))

        df=df.loc[df['Data de Recebimento'].dt.date==dt_atual]
        
        if len(df)>0:

            assunto=f'Controle de Malote - {ConverterData(dt_atual)}'

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            email_to=['cobranca@demarchibrasil.com.br']

            email_cc=['loja@demarchibrasil.com.br','athos.alcantara@demarchisaopaulo.com.br']

            vl_malote=Moeda.FormatarMoeda(df['Valor do Malote'].sum())

            qtd_malote=Moeda.Numero(len(df['Romaneio'].unique().tolist()))

            qtde_nf=Moeda.Numero(len(df['Pedido'].unique().tolist()))

            mensagem=f"""
                        
            <p>{msg};</p>

            <p>Foram conferidos {qtd_malote} malotes contendo {qtde_nf} notas. Dando um total de R$ {vl_malote}.</p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>BOT TI</p>

            
            """

            dt_form=str(dt_atual).replace('-','_')

            df.to_excel(f'Malote {dt_form}.xlsx',index=False,encoding='UTF-8')

            temp_path=os.path.join(os.getcwd(),'*.xlsx')
            anexo=glob(temp_path)

            temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

            Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)
            Remover.RemoverArquivo('.xlsx')

            pass

        pass

    except HttpError as err:
        print(err)

        pass


    pass


def ConverterData(data):

    return datetime.strftime(data,'%d/%m/%Y')

    pass


if __name__ == '__main__':
    main()