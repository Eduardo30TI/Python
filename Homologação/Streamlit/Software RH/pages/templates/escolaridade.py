import streamlit as st
import time
import os
from glob import glob
from SQL import SQL
from streamlit_js_eval import streamlit_js_eval

sql = SQL()

querys = dict()

tabelas = {

    'Escolaridade':

    """

    CREATE TABLE IF NOT EXISTS escolaridade(
    
        CD_GRAU SMALLINT NOT NULL,
        DESCRICAO TEXT NOT NULL,
        STATUS BOOLEAN NOT NULL

    )

    """


}


class Escolaridade:

    def main(self):


        sql.CreateTable(tabelas.values())

        querys={

            'codigo':

            """

            SELECT COALESCE(MAX(CD_GRAU),0)+1 FROM escolaridade

            """,

            'dados':

            """

            SELECT * FROM escolaridade

            """
        }

        df=sql.GetDataframe(querys['dados'])
        codigo=sql.Code(querys['codigo'])

        temp_dict=dict()

        placeholder=st.empty()

        with placeholder.container():

            tab1,tab2=st.tabs(['Salvar','Editar'])

            with tab1:

                col1,col2=tab1.columns(2)
                temp_dict['codigo']=col1.text_input('Código',key='cd_codigo',value=codigo,disabled=True)
                temp_dict['status']=col2.checkbox('Status',key='st_grau')

                temp_dict['escolaridade']=tab1.text_input('Escolaridade',key='grau').upper()

                with tab1.expander('Lista',expanded=False):

                    st.dataframe(df,use_container_width=True)

                    pass

                btn=tab1.button('Salvar',type='primary',key='save')

                if btn==True:

                    resp=self.ValidarCampos(temp_dict)

                    if resp[0]!=None:

                        mensagem=tab1.warning(f'Preencher o campo {resp[0]}')
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    else:

                        resp=self.Salvar(temp_dict,'Salvar')

                        if resp==True:

                            mensagem=tab1.success('Dados salvo com sucesso!')
                            time.sleep(1)
                            mensagem.empty()
                            streamlit_js_eval(js_expressions='parent.window.location.reload()')

                            pass

                        else:

                            mensagem=tab1.warning('Dados já consta salvo no banco de dados!')
                            time.sleep(1)
                            mensagem.empty()

                            pass

                        pass

                    pass

                pass

            with tab2:

                col1,col2=tab2.columns(2)

                if len(df)>0:

                    temp_dict['codigo']=col1.selectbox('Código',key='cd_codigo_edit',options=df['CD_GRAU'].unique().tolist())
                    temp_dict['status']=col2.checkbox('Status',key='st_grau_edit',value=df.loc[df['CD_GRAU']==temp_dict['codigo'],'STATUS'].values[-1])

                    temp_dict['escolaridade']=tab2.text_input('Escolaridade',key='grau_edit',value=df.loc[df['CD_GRAU']==temp_dict['codigo'],'DESCRICAO'].values[-1]).upper()

                    pass

                else:

                    temp_dict['codigo']=col1.selectbox('Código',key='cd_codigo_edit',options=[])
                    temp_dict['status']=col2.checkbox('Status',key='st_grau_edit')

                    temp_dict['escolaridade']=tab2.text_input('Escolaridade',key='grau_edit').upper()

                    pass

                btn=tab2.button('Editar',type='primary',key='edit')

                if btn==True:

                    resp=self.ValidarCampos(temp_dict)

                    if resp[0]!=None:

                        mensagem=tab1.warning(f'Preencher o campo {resp[0]}')
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    else:

                        resp=self.Salvar(temp_dict,'Editar')

                        if resp==True:

                            mensagem=tab1.success('Dados salvo com sucesso')
                            time.sleep(1)
                            mensagem.empty()
                            streamlit_js_eval(js_expressions='parent.window.location.reload()')

                            pass

                        pass

                    pass

                pass

            pass

        pass

    def ValidarCampos(self,temp_dict: dict):

        cont=0

        dados_dict=dict()

        for k,v in temp_dict.items():

            if v=='':

                cont=0

                dados_dict[cont]=k

                break

            else:

                cont+=1

                dados_dict[0]=None

                pass

            pass

        return dados_dict

        pass

    def Salvar(self,dados_dict: dict,btn: str):


        querys={

            'codigo':

            """

            SELECT COALESCE(MAX(CD_GRAU),0)+1 FROM escolaridade

            """,

            'validar':

            """

            SELECT COUNT(*) FROM escolaridade WHERE DESCRICAO='{0}'

            """.format(dados_dict['escolaridade']),

            'UPDATE':

            """

            UPDATE escolaridade
            SET DESCRICAO='{1}',
            STATUS={2}
            WHERE CD_GRAU={0}

            """.format(dados_dict['codigo'],dados_dict['escolaridade'],dados_dict['status'])

        }

        validar=sql.Code(querys['validar'])
        codigo=sql.Code(querys['codigo'])

        resp=True

        if validar<=0:

            tipo='INSERT'

            querys['INSERT']="""

            INSERT INTO escolaridade (CD_GRAU,DESCRICAO,STATUS) VALUES({0},'{1}',{2})

            """.format(codigo,dados_dict['escolaridade'],dados_dict['status'])

            sql.Save(querys[tipo])

            pass

        else:

            if btn=='Salvar':

                resp=False

                pass

            else:

                tipo='UPDATE'

                sql.Save(querys[tipo])

                pass
            
            pass

        
        return resp

        pass

    pass