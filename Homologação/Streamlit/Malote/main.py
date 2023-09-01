import streamlit as st
from datetime import datetime
from Acesso import Login
from Query import Query
from Moeda import Moeda

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)


def Main():

    dt_atual=datetime.now().date()

    st.title('Pagamentos')
       
    col1,col2=st.columns(2)
    dt1=col1.date_input('De',dt_atual)
    dt2=col2.date_input('Até',dt_atual)

    querys={

        'Roteiro':

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
        WHERE CONVERT(DATETIME,CAST(r.dt_retorno AS DATE),101) BETWEEN '{0}' and '{1}' AND nf.situacao IN('AB')
        --WHERE r.situacao='AB'
        ORDER BY it.nu_ped
        
        """.format(dt1,dt2)
    }

    btn=st.button('Consultar')

    if btn==True:

        df=sql.CriarTabela(kwargs=querys)

        malote=len(df['Roteiro']['Roteiro'].unique().tolist())
        pedidos=len(df['Roteiro']['Pedido'].unique().tolist())
        clientes=len(df['Roteiro']['ID Cliente'].unique().tolist())
        total=Moeda.FormatarMoeda(df['Roteiro']['Total NFe'].sum())

        col1,col2,col3=st.columns(3)

        col1.metric('Malote',malote)
        col2.metric('Pedidos',pedidos)
        col3.metric('Total',f'R$ {total}')

        for c in ['Roteiro','NFe','Pedido','ID Cliente']:

            df['Roteiro'][c]=df['Roteiro'][c].apply(FormatarTexto)

            pass
        
        st.header('Lista de Pedidos')
        st.dataframe(df['Roteiro'])


        pass

    pass

def FormatarTexto(val):

    val=str(val)

    val=val.replace(',','')

    return val

    pass

if __name__=='__main__':

    Main()

    pass