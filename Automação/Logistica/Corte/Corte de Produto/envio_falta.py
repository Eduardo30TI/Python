import pandas as pd
import os
import pyodbc
import win32com.client as win32
import glob
import sched
import time
from datetime import datetime, timedelta

usuario='Netfeira'

senha='sqlserver'

database='MOINHO'

driver='{SQL Server}'

server='192.168.0.252'

str_conexao=('Driver={0};Server={1};Database={4};UID={2};PWD={3}'.format(driver,server,usuario,senha,database))

querys=[

"""

WITH TabTpCorte (cd_tp_faltaprd,descrica) AS (

SELECT cd_tp_faltaprd,descricao
FROM tp_faltaprd
WHERE ativo=1
--AND descricao LIKE '%CORTE%'
),

TabFalta (dt_falta,cd_vend,cd_clien,nu_ped,cd_prod,unid_vda,qtde_falta_vda,preco_unit,vl_total) AS (

SELECT CONVERT(DATETIME,CAST(dt_falta AS date),101) AS dt_falta,
cd_vend,cd_clien,nu_ped,cd_prod,unid_vda,qtde_falta,preco_unit,
ROUND(qtde_falta*preco_basico,2) AS vl_total
FROM faltaprd
INNER JOIN TabTpCorte ON faltaprd.cd_tp_faltaprd=TabTpCorte.cd_tp_faltaprd
),

TabSupervisor (cd_equipe,descricao,nome_resumido,email) AS (

SELECT equipe.cd_equipe,descricao,
CASE WHEN CHARINDEX(' ',LTRIM(RTRIM(nome)))=0 THEN nome ELSE
LTRIM(RTRIM(LEFT(nome,(CHARINDEX(' ',LTRIM(RTRIM(nome))))))) + ' ' + 
RTRIM(LTRIM(RIGHT(nome,(CHARINDEX(' ',REVERSE(LTRIM(RTRIM(nome)))))))) END AS nome_resumido,
vendedor.e_mail
FROM equipe
INNER JOIN vendedor ON equipe.cd_vend_sup=vendedor.cd_vend
)

SELECT dt_falta AS 'Data de Falta',
TabFalta.cd_vend AS 'ID Vendedor',vendedor.nome_gue AS 'Vendedor',
TabSupervisor.descricao AS 'Equipe',
CASE WHEN TabSupervisor.descricao='EQUIPE 9 (ATIVO)' THEN 'PEDIDOS'
WHEN TabSupervisor.nome_resumido='JULIO DELFINO' THEN 'ROGERIO FELIPIM'
ELSE TabSupervisor.nome_resumido END AS 'Supervisor',
TabFalta.cd_clien AS 'ID Cliente',cliente.nome_res AS 'Nome Fantasia',
nu_ped AS 'Pedido',TabFalta.cd_prod AS 'SKU',produto.descricao AS 'Produto',
unid_vda AS 'Unid. VDA',qtde_falta_vda AS 'Qtde. VDA',
preco_unit AS 'Valor Unitário',vl_total AS 'Total do Pedido'
FROM TabFalta
INNER JOIN vendedor ON TabFalta.cd_vend=vendedor.cd_vend
INNER JOIN TabSupervisor ON vendedor.cd_equipe=TabSupervisor.cd_equipe
INNER JOIN cliente ON TabFalta.cd_clien=cliente.cd_clien
INNER JOIN produto ON TabFalta.cd_prod=produto.cd_prod
WHERE YEAR(dt_falta)=YEAR(GETDATE()) AND MONTH(dt_falta)=MONTH(GETDATE())
AND DAY(dt_falta)=DAY(GETDate())

"""
]

def ConexaoSQL():

    try:

        conecta=pyodbc.connect(str_conexao)

        return conecta

        pass

    except:

        print('Sem conexão com a base de dados')

        pass

    pass

def EnviarEmail(assunto,corpo,email_dest,email_cc=''):

    olApp = win32.Dispatch('Outlook.Application')
    olNS = olApp.GetNameSpace('MAPI')

    envio_destino=[email_dest]

    copia_email=[email_cc]

    # construct email item object
    mailItem = olApp.CreateItem(0)
    mailItem.Subject = assunto
    mailItem.BodyFormat = 1
    #mailItem.Body = corpo
    mailItem.HTMLBody=corpo
    mailItem.To = ';'.join(env for env in envio_destino)
    mailItem.Cc=';'.join(env for env in copia_email)
    mailItem.Sensitivity  = 2

    arquivo=[os.path.join(os.getcwd(),arq) for arq in glob.glob('*.xlsx') if arq.find('E-mail')]
    
    for anexo in arquivo:
    
        mailItem.Attachments.Add(anexo)
        
        pass
    #optional (account you want to use to send the email)
    #mailItem._oleobj_.Invoke(*(64209, 0, 8, 0, olNS.Accounts.Item('<email@gmail.com')))
    #mailItem.Display()
    #mailItem.Save()
    mailItem.Send()

    RemoverArquivo()

    pass

def FormatarMoeda(valor):
    
    valor=str(valor)
    
    inteiro=valor[:valor.find('.')]
    
    decimal=valor[valor.find('.'):]
    
    decimal=decimal[1:]
    
    if(len(decimal)==1):
        
        decimal=(f'0{decimal}')
        
        pass
    
    else:
        
        decimal=decimal[:2]
        
        pass
    
    moeda=('R$ {0},{1}'.format(inteiro,decimal))
    
    return moeda
    
    pass

def CorpoEmail():

    conectando=ConexaoSQL()

    df=pd.read_sql(querys[0],conectando)

    supervisores=df['Supervisor'].unique().tolist()

    for nome in supervisores:
        
        sku=len(df['SKU'].loc[df['Supervisor']==nome].unique().tolist())
        
        pedido=len(df['Pedido'].loc[df['Supervisor']==nome].unique().tolist())

        if(pedido<=0):

            continue

        try:
        
            total=df[['Total do Pedido']].loc[df['Supervisor']==nome].sum().tolist()

            total=FormatarMoeda(total[0])
            
            mensagem=f"""
            
            <p>Bom dia;</p>

            <p>{str(nome).title()}</p>

            <p>Foram identificados cerca de {sku} itens que foram cortados. Totalizando R$ {total}</p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>Robô Autonomo</p>
                
            """

            Relatorio(nome)
            
            email_dest=GetEmail(nome)

            if(nome!='ROGERIO FELIPIM'):

                email_cc=GetEmail('ROGERIO FELIPIM')

                pass

            else:

                email_cc=''

                pass

            EnviarEmail('Corte de Produto',mensagem,email_dest,email_cc)

            pass

        except:

            continue
     
        pass

    EmailGeral()
        
    pass

def Relatorio(filtro=''):

    conecta=ConexaoSQL()

    temp_df=pd.read_sql(querys[0],conecta)

    if(filtro==''):

        produto_df=temp_df[['SKU','Produto','Qtde. VDA','Total do Pedido']].groupby(['SKU','Produto']).sum()

        produto_df.to_excel('Produtos.xlsx',index=True,encoding='ISO-8859-1')

        temp_df.to_excel('Detalhe do Corte.xlsx',index=False,encoding='ISO-8859-1')

        pass

    else:

        temp_df=temp_df.loc[temp_df['Supervisor']==filtro]
        
        produto_df=temp_df[['SKU','Produto','Qtde. VDA','Total do Pedido']].groupby(['SKU','Produto']).sum()

        produto_df.to_excel('Produtos.xlsx',index=True,encoding='ISO-8859-1')

        temp_df.to_excel('Detalhe do Corte.xlsx',index=False,encoding='ISO-8859-1')

        pass
  
    pass

def GetEmail(filtro):

    dados=[arq for arq in glob.glob('*') if not arq.find('E-mail')]
    
    temp_df=pd.read_excel(dados[0],sheet_name='Email')

    email=temp_df['EMAIL'].loc[temp_df['Supervisor']==filtro].tolist()

    return email[0]

    pass

def EmailGeral():

    conectando=ConexaoSQL()

    temp_df=pd.DataFrame()

    dados=[arq for arq in glob.glob('*') if not arq.find('E-mail')]
    
    sup_df=pd.read_excel(dados[0],sheet_name='Geral')

    df=pd.read_sql(querys[0],conectando)

    temp_df=df.merge(sup_df,on='Supervisor',how='right')

    temp_df=temp_df.loc[temp_df['SKU'].isnull()]

    temp_df=temp_df[['Supervisor','EMAIL']]

    sku=len(df['SKU'].unique())

    pedido=len(df['Pedido'].unique())

    total=df['Total do Pedido'].sum()

    total=FormatarMoeda(round(total,2))

    lista_email=temp_df['EMAIL'].tolist()

    lista=temp_df['Supervisor'].tolist()

    if(pedido>0):
    
        mensagem=f"""
        
        <p>Bom dia;</p>

        <p>{str(lista[0]).title()}</p>

        <p>Foram identificados cerca de {sku} itens que foram cortados. Totalizando R$ {total}</p>

        <P>Por favor não responder mensagem automática</P>

        <p>Atenciosamente</p>

        <p>Robô Autonomo</p>
               
        """

        Relatorio()

        email_dest=lista_email[0]

        email_cc=lista_email[-1]
        
        EnviarEmail('Corte de Produto',mensagem,email_dest,email_cc)

        print('E-mail enviado com sucesso!')

        pass

def GetHora():

    hora=str(datetime.now().hour)

    minuto=str(datetime.now().minute)

    segundos=str(datetime.now().second)

    if(len(hora)==1):

        hora=(f'0{hora}')

        pass

    if(len(minuto)==1):

        minuto=(f'0{minuto}')

        pass


    if(len(segundos)==1):

        segundos=(f'0{segundos}')

        pass
    

    tempo=(f'{hora}:{minuto}:{segundos}')

    return tempo

    pass

def RemoverArquivo():

    path_base=os.path.join(os.getcwd(),'*.xlsx')

    dados=glob.glob(path_base)

    for arq in dados:

        nome=str(os.path.basename(arq))

        if(nome.find('E-mail')>=0):

            continue

        os.remove(arq)

        pass

    pass

if __name__=='__main__':
        
    tempo=GetHora()

    executador=sched.scheduler(time.time,time.sleep)

    if(tempo=='08:03:59'):
        
        executador.enter(1,1,CorpoEmail)
        executador.run()

        pass

    pass