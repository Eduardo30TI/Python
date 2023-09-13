import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd
import time
from SQL import SQL
from CNPJ import CNPJ
from Gmail import Mail
import os
from datetime import datetime
import socket as s

gmail=Mail()

sql=SQL()

tabelas={

    'controle':

    """

    CREATE TABLE IF NOT EXISTS controle(
    
        NOTA TEXT,
        FORNECEDOR TEXT NOT NULL,
        DT_AGENDA DATETIME NOT NULL,
        QTDE SMALLINT NOT NULL,
        TIPO VARCHAR(250) NOT NULL,
        RECEBIDO VARCHAR(250) NOT NULL,
        OCORRENCIA TEXT NOT NULL,
        ID SMALLINT NOT NULL


    )

    """,

    'tipo':


    """

    CREATE TABLE IF NOT EXISTS tipo(
    
        CD_TIPO SMALLINT NOT NULL,
        TIPO VARCHAR(250)

    )

    """,

    'fornecedor':

    """
    
    CREATE TABLE IF NOT EXISTS fornecedor(
    
        CNPJ VARCHAR(250) NOT NULL,
        RAZAO_SOCIAL VARCHAR(250) NOT NULL,
        NOME_FANTASIA VARCHAR(250) NOT NULL

    )
    
    """
}

class Controle:

    def __init__(self,titulo) -> None:

        self.titulo=titulo

        pass


    def main(self):

        sql.CreateTable(tabelas.values())

        placeholder=st.empty()

        with placeholder.container():

            st.header(self.titulo)
            st.markdown('----')

            tab1,tab2,tab3,tab4=st.tabs(['Agenda','Fornecedor','Tipo','Editar'])

            querys={

                'codigo':

                """

                SELECT COALESCE(MAX(ID),0)+1 FROM controle

                """
            }
            
            codigo=sql.Code(querys['codigo'])

            with tab1.container():

                temp_dict=dict()

                col1,col2=st.columns(2)

                nota=col1.text_input('Nota',key='nota')
                id=col2.text_input('ID',disabled=True,value=codigo)

                querys={

                    'validar':

                    """
                    
                    SELECT COUNT(*) FROM controle WHERE ID={0}

                    """.format(id)
                }

                validar=sql.Code(querys['validar'])

                df=sql.GetDataframe('SELECT * FROM fornecedor')
                lista=df['RAZAO_SOCIAL'].unique().tolist()
                                
                temp_dict['fornecedor']=st.selectbox('Fornecedor',options=lista,key='cb_forn')

                col3,col4=st.columns(2)
                temp_dict['agenda']=col3.date_input(label='Agendamento',key='tab1_data')
                temp_dict['qtde']=col4.text_input('Qtde',key='qtde')

                df=sql.GetDataframe('SELECT * FROM tipo')
                lista=df['TIPO'].unique().tolist()                
                temp_dict['tipo']=st.selectbox('Tipo',options=lista,key='cb_tipo')

                area=st.text_area('Observação',key='obs')

                btn=st.button('Salvar',type='primary',key='btn_agend')

                if btn==True:

                    resp=self.ValidarCampo(temp_dict)

                    if resp!=None:

                        mensagem=st.warning(resp)
                        time.sleep(1)
                        mensagem.empty()

                        pass


                    else:
    
                        if validar<=0:

                            tipo='INSERT'
                            
                            querys[tipo]="""

                            INSERT INTO controle(NOTA,FORNECEDOR,DT_AGENDA,QTDE,TIPO,RECEBIDO,OCORRENCIA,ID)VALUES('{0}','{1}','{2}',{3},'{4}','{5}','{6}',{7})

                            """.format(nota,temp_dict['fornecedor'],temp_dict['agenda'],temp_dict['qtde'],temp_dict['tipo'],'N',area,id)

                            pass


                        else:

                            tipo='UPDATE'

                            querys[tipo]="""

                            UPDATE controle
                            SET NOTA='{0}',
                            FORNECEDOR='{1}',
                            DT_AGENDA='{2}',
                            QTDE={3},
                            TIPO='{4}',
                            OCORRENCIA='{5}'
                            WHERE ID={6}

                            """.format(nota,temp_dict['fornecedor'],temp_dict['agenda'],temp_dict['qtde'],temp_dict['tipo'],area,id)

                            pass

                        sql.Save(querys[tipo])

                        dt_now=datetime.strftime(datetime.now(),'%d/%m/%Y %H:%M:%S')
                        assunto=f'NETFEIRA - {dt_now}'

                        IP=s.gethostbyname(s.gethostname())

                        temp_path=os.path.join(os.getcwd(),IP,f'Consolidado.csv')
                        df=sql.GetDataframe('SELECT * FROM controle')
                        df.to_csv(temp_path,encoding='UTF-8',index=False)
                        
                        #bot.ti@demarchibrasil.com.br
                        temp_dict={'To':['bot.ti@demarchibrasil.com.br'],'CC':[''],'Anexo':[temp_path]}
                        mensagem=f'Dados do dia {dt_now}'
                        gmail.Enviar(assunto=assunto,mensagem=mensagem,info=temp_dict)
                        os.remove(temp_path)                        

                        mensagem=st.success('Dados salvo com sucesso')
                        time.sleep(1)
                        mensagem.empty()

                        streamlit_js_eval(js_expressions='parent.window.location.reload()')

                        pass

                    pass

                pass

            with tab2.container():

                temp_dict=dict()

                col1,col2=st.columns(2)

                temp_dict['cnpj']=col1.text_input('CNPJ',key='cnpj')

                querys={

                    'validar':

                    """

                    SELECT COUNT(*) FROM fornecedor WHERE CNPJ='{0}'

                    """.format(temp_dict['cnpj'])
                }

                validar=sql.Code(querys['validar'])

                temp_dict['razao_social']=''
                temp_dict['nome_fantasia']=''

                if temp_dict['cnpj']!='':

                    cnpj=CNPJ(temp_dict['cnpj'])
                    
                    json=cnpj.GetDados()
                    temp_dict['razao_social']=json['razao_social']
                    temp_dict['nome_fantasia']=json['nome_fantasia']
                    
                    pass
                
                
                temp_dict['razao_social']=st.text_input('Razão Social',key='razao',value=temp_dict['razao_social']).upper()
                temp_dict['nome_fantasia']=st.text_input('Nome Fantasia',key='fantasia',value=temp_dict['nome_fantasia']).upper()

                btn=st.button('Salvar',type='primary',key='btn_forn')

                if btn==True:

                    resp=self.ValidarCampo(temp_dict)

                    if resp!=None:
                        
                        mensagem=st.warning(resp)
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    else:

                        if validar<=0:

                            tipo='INSERT'

                            querys[tipo]="""

                            INSERT INTO fornecedor(CNPJ,RAZAO_SOCIAL,NOME_FANTASIA)VALUES('{0}','{1}','{2}')

                            """.format(temp_dict['cnpj'],temp_dict['razao_social'],temp_dict['nome_fantasia'])

                            pass


                        else:

                            tipo='UPDATE'

                            querys[tipo]="""

                            UPDATE fornecedor
                            SET RAZAO_SOCIAL='{1}',
                            NOME_FANTASIA='{2}'
                            WHERE CNPJ='{0}'

                            """.format(temp_dict['cnpj'],temp_dict['razao_social'],temp_dict['nome_fantasia'])

                            pass


                        sql.Save(querys[tipo])

                        mensagem=st.success('Dados salvo com sucesso')
                        time.sleep(1)
                        mensagem.empty()

                        streamlit_js_eval(js_expressions='parent.window.location.reload()')

                        pass

                    pass

                pass

            with tab3.container():

                temp_dict=dict()

                querys={

                    'codigo':

                    """

                    SELECT COALESCE(MAX(CD_TIPO),0)+1 FROM tipo

                    """
                }

                col1,col2=st.columns(2)
                
                codigo=sql.Code(querys['codigo'])

                temp_dict['cd_tipo']=col1.text_input('Código',key='cd_tipo',value=codigo,disabled=True)
                temp_dict['tipo']=st.text_input('Tipo',key='tipo').upper()

                querys['validar']="""

                SELECT COUNT(*) FROM tipo WHERE TIPO='{0}'

                """.format(temp_dict['tipo'])

                validar=sql.Code(querys['validar'])

                btn=st.button('Salvar',type='primary',key='btn_tipo')

                if btn==True:

                    resp=self.ValidarCampo(temp_dict)
                    
                    if resp!=None:

                        mensagem=st.warning(resp)
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    else:

                        if validar<=0:

                            tipo='INSERT'

                            querys[tipo]="""

                            INSERT INTO tipo(CD_TIPO,TIPO)VALUES({0},'{1}')

                            """.format(temp_dict['cd_tipo'],temp_dict['tipo'])

                            pass


                        else:

                            tipo='UPDATE'

                            querys[tipo]="""

                            UPDATE tipo
                            SET tipo='{0}'
                            WHERE tipo='{0}'

                            """.format(temp_dict['tipo'])                 

                            pass

                        sql.Save(querys[tipo])

                        mensagem=st.success('Dados salvo com sucesso')
                        time.sleep(1)
                        mensagem.empty()

                        streamlit_js_eval(js_expressions='parent.window.location.reload()')

                        pass

                    pass

                pass

            with tab4.container():

                df=sql.GetDataframe('SELECT * FROM controle')
                colunas=df.columns.tolist()

                for c in colunas:

                    df[c]=df[c].astype(str)
                    print(df[c])

                    pass

                filtro=st.selectbox('Filtrar',options=colunas)
                
                if filtro=='DT_AGENDA':

                    val=st.date_input(label='Data',label_visibility='collapsed')
                    val=str(val)

                    pass

                else:

                    lista=df[filtro].unique().tolist()
                    val=st.selectbox(label='',options=lista,label_visibility='collapsed')

                    pass

                if len(df)>0:

                    df=df.loc[df[filtro].str.contains(val)]

                    tabela=st.data_editor(df)

                    pass
                
                btn=st.button('Salvar',type='primary',key='edit_btn')

                if btn==True:

                    for i in tabela.index.tolist():
                        
                        tipo='UPDATE'

                        querys[tipo]="""

                        UPDATE controle
                        SET NOTA='{0}',
                        FORNECEDOR='{1}',
                        DT_AGENDA='{2}',
                        QTDE={3},
                        TIPO='{4}',
                        OCORRENCIA='{6}',
                        RECEBIDO='{5}'
                        WHERE ID={7}

                        """.format(tabela.loc[i,'NOTA'],tabela.loc[i,'FORNECEDOR'],tabela.loc[i,'DT_AGENDA'],tabela.loc[i,'QTDE'],tabela.loc[i,'TIPO'],tabela.loc[i,'RECEBIDO'],tabela.loc[i,'OCORRENCIA'],tabela.loc[i,'ID'])

                        sql.Save(querys[tipo])

                        pass

                    dt_now=datetime.strftime(datetime.now(),'%d/%m/%Y %H:%M:%S')
                    assunto=f'NETFEIRA - {dt_now}'

                    IP=s.gethostbyname(s.gethostname())

                    temp_path=os.path.join(os.getcwd(),IP,f'Consolidado.csv')
                    df=sql.GetDataframe('SELECT * FROM controle')
                    df.to_csv(temp_path,encoding='UTF-8',index=False)
                    
                    #bot.ti@demarchibrasil.com.br
                    temp_dict={'To':['bot.ti@demarchibrasil.com.br'],'CC':[''],'Anexo':[temp_path]}
                    mensagem=f'Dados do dia {dt_now}'
                    gmail.Enviar(assunto=assunto,mensagem=mensagem,info=temp_dict)
                    os.remove(temp_path)                    
                    
                    mensagem=st.success('Dados salvo com sucesso')
                    time.sleep(1)
                    mensagem.empty()

                    streamlit_js_eval(js_expressions='parent.window.location.reload()')

                    pass

                pass

            pass

        pass


    def ValidarCampo(self,campos: dict):

        temp_dict=dict()
        lista=[]
        cont=0

        for k,v in campos.items():

            resp=v==''
            lista.append(resp)
            temp_dict[resp]=k
            
            pass

        if lista.count(False)==len(campos.keys()):

            resp=None

            pass

        elif lista.count(True)==len(campos.keys()):

            resp='Preencher todos os campos!'

            pass

        else:

            resp=f'Preencher o campo {temp_dict[True]}'

            pass

        return resp

        pass

    pass