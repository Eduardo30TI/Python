from __future__ import print_function
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from Acesso import Login
from Query import Query
from datetime import datetime
import requests
import pyautogui as gui
from RemoverArquivo import Remover
from joblib import Parallel,delayed

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Roteiro':

    """
    
    SELECT r.nu_rom AS [Roteiro],nf.nome_motor AS [Motorista],
    CONVERT(DATETIME,CAST(r.dt_montagem AS DATE),101) AS [Data da Montagem],
    it.nu_ped AS [Pedido],nf.nu_nf_emp_fat AS [NFe],cli.[ID Cliente],cli.[Nome Fantasia],cli.Matriz,nf.vl_tot_nf AS [Total NFe]
    FROM romaneio r
    INNER JOIN it_rom it ON r.nu_rom=it.nu_rom
    INNER JOIN nota nf ON it.nu_nf=nf.nu_nf AND it.nu_ped=nf.nu_ped AND it.cd_emp=nf.cd_emp
    INNER JOIN netfeira.vw_cliente cli ON nf.cd_clien=cli.[ID Cliente]
    WHERE YEAR(r.dt_montagem)=YEAR(GETDATE())
    ORDER BY it.nu_ped
    
    """,

    'Pendente':

    """

    SELECT r.nu_rom AS [Roteiro],nf.nome_motor AS [Motorista],
    CONVERT(DATETIME,CAST(r.dt_montagem AS DATE),101) AS [Data da Montagem],
    it.nu_ped AS [Pedido],nf.nu_nf_emp_fat AS [NFe],cli.[ID Cliente],cli.[Nome Fantasia],cli.Matriz,nf.vl_tot_nf AS [Total NFe]
	,nf.cond_pagto AS [Condição de Pagamento],f.descricao AS [Forma de Pagamento],
	CASE WHEN r.situacao='EN' THEN 'ENCERRADO' WHEN r.situacao='CA' THEN 'CANCELADO' WHEN r.situacao='AB' THEN 'ABERTO'
	WHEN r.situacao='PE' THEN 'PENDENTE' END AS [Situação do Roteiro]
    FROM romaneio r
    INNER JOIN it_rom it ON r.nu_rom=it.nu_rom
    INNER JOIN nota nf ON it.nu_nf=nf.nu_nf AND it.nu_ped=nf.nu_ped AND it.cd_emp=nf.cd_emp
    INNER JOIN netfeira.vw_cliente cli ON nf.cd_clien=cli.[ID Cliente]
	INNER JOIN formpgto f ON nf.formpgto=f.formpgto
	WHERE r.situacao='AB'
    ORDER BY it.nu_ped
    
    """,

    'Realizado':

    """
    
    SELECT r.nu_rom AS [Roteiro],nf.nome_motor AS [Motorista],
    CONVERT(DATETIME,CAST(r.dt_montagem AS DATE),101) AS [Data da Montagem],
	CONVERT(DATETIME,CAST(r.dt_retorno AS DATE),101) AS [Data de Retorno],
    it.nu_ped AS [Pedido],nf.nu_nf_emp_fat AS [NFe],cli.[ID Cliente],cli.[Nome Fantasia],cli.Matriz,nf.vl_tot_nf AS [Total NFe]
	,nf.cond_pagto AS [Condição de Pagamento],f.descricao AS [Forma de Pagamento],
	CASE WHEN r.situacao='EN' THEN 'ENCERRADO' WHEN r.situacao='CA' THEN 'CANCELADO' WHEN r.situacao='AB' THEN 'ABERTO'
	WHEN r.situacao='PE' THEN 'PENDENTE' END AS [Situação do Roteiro]
    FROM romaneio r
    INNER JOIN it_rom it ON r.nu_rom=it.nu_rom
    INNER JOIN nota nf ON it.nu_nf=nf.nu_nf AND it.nu_ped=nf.nu_ped AND it.cd_emp=nf.cd_emp
    INNER JOIN netfeira.vw_cliente cli ON nf.cd_clien=cli.[ID Cliente]
	INNER JOIN formpgto f ON nf.formpgto=f.formpgto
	WHERE YEAR(r.dt_retorno)=YEAR(GETDATE()) AND nf.situacao IN('AB')
	--WHERE r.situacao='AB'
    ORDER BY it.nu_ped

    """

}

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1bGFXbWKGpkJD5SswHgy4aWmRmzqaxsapZpFBFBsydUI'


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
            flow = InstalledAppFlow.from_client_secrets_file(path_json, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


    try:
        
        temp_dict={'Roteiro':'Base!A2:I','Pendente':'Romaneio!A2:L','Realizado':'Finalizado!A2:M'}

        for key,value in temp_dict.items():

            SAMPLE_RANGE_NAME = value

            df=sql.GetDados(querys,tabela=[key])

            col_leach='Condição de Pagamento'

            if key in ['Pendente','Realizado']:

                df[key]=df[key].loc[df[key][col_leach].str.contains('A VISTA')]

                pass

            service = build('sheets', 'v4', credentials=creds)

            plan=value[:value.find('!')]

            # Call the Sheets API
            sheet = service.spreadsheets()
            sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID,range=SAMPLE_RANGE_NAME).execute()

            colunas=[l for l in df[key].columns.tolist() if str(l).find('Data')>=0]

            for c in colunas:
            
                df[key][c]=df[key][c].apply(ConverterData)

                pass

            valores=df[key].values.tolist()

            sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=f'{plan}!A2',valueInputOption='USER_ENTERED',body={'values':valores}).execute()
            
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