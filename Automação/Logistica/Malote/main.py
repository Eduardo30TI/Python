from Acesso import Login
from Email import Email
from Moeda import Moeda
from Query import Query
from RemoverArquivo import Remover
import os
from glob import glob
from datetime import datetime,timedelta
import pandas as pd

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

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
	WHERE CONVERT(DATETIME,CAST(r.dt_retorno AS DATE),101)=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101) AND nf.situacao IN('AB')
	--WHERE r.situacao='AB'
    ORDER BY it.nu_ped
    
    """
}

def Main():

    df=sql.CriarTabela(kwargs=querys)
    
    dt_atual=datetime.now().date()
        
    colunas=[l for l in df['Realizado'].columns.tolist() if str(l).find('Data')>=0]

    for c in colunas:

        df['Realizado'][c]=pd.to_datetime(df['Realizado'][c])

        pass

    col_leach='Condição de Pagamento'

    df['Realizado']=df['Realizado'].loc[df['Realizado'][col_leach].str.contains('A VISTA')]
        
    if len(df['Realizado'])>0:

        assunto=f'Controle de Malote - {ConverterData(dt_atual)}'

        msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

        email_to=['financeiro@demarchibrasil.com.br']

        email_cc=['loja@demarchibrasil.com.br','athos.alcantara@demarchisaopaulo.com.br']

        vl_malote=Moeda.FormatarMoeda(df['Realizado']['Total NFe'].sum())

        qtd_malote=Moeda.Numero(len(df['Realizado']['Roteiro'].unique().tolist()))

        qtde_nf=Moeda.Numero(len(df['Realizado']['Pedido'].unique().tolist()))

        mensagem=f"""
                        
        <p>{msg};</p>

        <p>Foram conferidos {qtd_malote} malotes contendo {qtde_nf} notas. Dando um total de R$ {vl_malote}.</p>

        <P>Por favor não responder mensagem automática</P>

        <p>Atenciosamente</p>

        <p>BOT TI</p>
            
        """

        dt_form=str(dt_atual).replace('-','_')

        df['Realizado'].to_excel(f'Malote {dt_form}.xlsx',index=False)

        temp_path=os.path.join(os.getcwd(),'*.xlsx')
        anexo=glob(temp_path)

        temp_dict={'To':email_to,'CC':email_cc,'Anexo':anexo}

        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)
        Remover.RemoverArquivo('.xlsx')

        pass
    

    pass

def ConverterData(data):

    return datetime.strftime(data,'%d/%m/%Y')

    pass

if __name__=='__main__':

    Main()

    pass