from datetime import datetime
from Acesso import Login
from Query import Query
from Moeda import Moeda
from RemoverArquivo import Remover
import streamlit as st
import pandas as pd
from Gmail import Mail
import os
from glob import glob

mail=Mail()

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

tabelas=''

def Main():

    dt_atual=datetime.now().date()

    st.title('Malote')
    col1,col2=st.sidebar.columns(2)
    dt1=col1.date_input(label='De',value=dt_atual)
    dt2=col2.date_input(label='Até',value=dt_atual)
    
    querys={

        'Roteiro':

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
        WHERE r.situacao='AB' AND CONVERT(DATETIME,CAST(r.dt_montagem AS DATE),101) BETWEEN '{0}' AND '{1}'
        ORDER BY it.nu_ped        
        
        """.format(dt1,dt2)
    }

    df=sql.CriarTabela(kwargs=querys)

    for c in ['Roteiro','NFe','Pedido','ID Cliente']:

        df['Roteiro'][c]=df['Roteiro'][c].apply(FormatarValor)

        pass

    #atualizar ao filtrar

    temp_path=os.path.join(os.getcwd(),'Base.xlsx')

    arq=glob(temp_path)

    if len(arq)>0:

        dados_df=pd.read_excel(arq[-1])
        lista=[str(l) for l in dados_df['Roteiro'].unique().tolist()]

        df['Roteiro']=df['Roteiro'].loc[~df['Roteiro']['Roteiro'].isin(lista)]

        btn1.success('Dados atualizado com sucesso!')

        pass

    btn1,btn2=st.sidebar.columns(2)
    btn_refresh=btn1.button('Atualizar')

    if btn_refresh==True:

        temp_path=os.path.join(os.getcwd(),'Base.xlsx')

        arq=glob(temp_path)

        if len(arq)>0:

            dados_df=pd.read_excel(arq[-1])
            lista=[str(l) for l in dados_df['Roteiro'].unique().tolist()]

            df['Roteiro']=df['Roteiro'].loc[~df['Roteiro']['Roteiro'].isin(lista)]

            btn1.success('Dados atualizado com sucesso!')

            pass

        pass
        
    btn_send=btn2.button('Email')

    if btn_send==True:

        temp_path=os.path.join(os.getcwd(),'Base.xlsx')

        arq=glob(temp_path)        

        if len(arq)>0:

            dados_df=pd.read_excel(arq[-1])

            dt_format=datetime.strftime(dt_atual,'%d_%m_%Y')

            temp_path=os.path.join(os.getcwd(),f'Malote {dt_format}.xlsx')

            dados_df=dados_df.loc[dados_df['Data Alteração'].dt.date==dt_atual]
            
            dados_df.to_excel(temp_path,index=False)

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            total=Moeda.FormatarMoeda(dados_df['Total NFe'].sum())

            mensagem=f"""
                        
            <p>{msg};</p>

            <p>Logística</p>

            <p>Foram identificados cerca de {len(dados_df['NFe'].unique().tolist())} notas que estão pendentes para finalização de malote. Totalizando R$ {total}</p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>BOT TI</p>
            
            """

            temp_dict={'To':['athos.alcantara@demarchisaopaulo.com.br','edson.francisco@demarchisaopaulo.com.br'],'CC':['edson.junior@demarchibrasil.com.br','loja@demarchibrasil.com.br'],'Anexo':[temp_path]}

            mail.Enviar(assunto=f'Malote {datetime.strftime(dt_atual,"%d/%m/%Y")}',mensagem=mensagem,info=temp_dict)

            st.sidebar.success('E-mail enviado com sucesso!')

            Remover.Remove(temp_path)
            
            pass

        else:

            st.sidebar.warning('Não tem dados a serem enviados')

            pass

        pass

    col1,col2,col3=st.columns(3)

    df['Roteiro'].sort_values('Roteiro',ascending=True,inplace=True)

    lista=df['Roteiro']['Roteiro'].unique().tolist()

    val=col1.selectbox('Roteiro',options=lista)

    df['Temp']=df['Roteiro'].loc[df['Roteiro']['Roteiro']==val]

    count=len(df['Temp'])

    if count>0:

        total=Moeda.FormatarMoeda(df['Temp']['Total NFe'].sum())

        col2.text_input('Total',f'R$ {total}')
        col3.text_input('Notas',len(df['Temp']['NFe'].unique().tolist()))

        st.dataframe(df['Temp'][['Roteiro','Motorista','NFe','ID Cliente','Nome Fantasia','Total NFe']])
        lista=df['Temp']['NFe'].unique().tolist()

        notas=st.multiselect('Notas',lista,key='Notas')
        status=st.selectbox('Status',['FALTA CANHOTO','AGUARDANDO LOGÍSTICA'],key='Status')
        txt_area=st.text_area('Observações',key='Obs')

        if len(notas)>0 and status!='' and txt_area!='':

            df['Temp']=df['Temp'].loc[df['Temp']['NFe'].isin(notas)]

            df['Temp']['Status']=status
            df['Temp']['Observações']=txt_area
            df['Temp']['Data Alteração']=dt_atual

            st.dataframe(df['Temp'].loc[df['Temp']['NFe'].isin(notas)])

            btn=st.button('Salvar')

            if btn==True:

                temp_path=os.path.join(os.getcwd(),'Base.xlsx')

                arq=glob(temp_path)                

                if len(arq)>0:

                    dados_df=pd.read_excel(arq[-1])

                    lista=dados_df['NFe'].unique().tolist()

                    dados_df=pd.concat([df['Temp'].loc[~df['Temp']['NFe'].isin(lista)],dados_df],axis=0,ignore_index=True)

                    dados_df.to_excel(temp_path,index=False)

                    pass

                else:

                    df['Temp'].to_excel(temp_path,index=False)

                    pass

                st.success('Dados salvo com sucesso!')
  
                pass

            pass
                
        pass

    else:

        col2.text_input('Total')
        col3.text_input('Notas')

        pass

    pass

def FormatarValor(val):

    val=str(val)

    val=val.replace(',','')

    return val

    pass

if __name__=='__main__':

    Main()

    pass