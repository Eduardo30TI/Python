import streamlit as st
import os
import socket as s
import time
import shutil
from streamlit_js_eval import streamlit_js_eval
from SQL import SQL

sql=SQL()

tabelas={

    'usuario':

    """

    CREATE TABLE IF NOT EXISTS usuario(
    
        CODE SMALLINT NOT NULL,
        EMAIL TEXT NOT NULL,
        SENHA VARCHAR(250) NOT NULL


    )

    """
}

class Usuario:

    def __init__(self):


        pass

    def main(self):

        sql.CreateTable(tabelas.values())

        IP=s.gethostbyname(s.gethostname())
        path_base=os.path.join(os.getcwd(),IP)

        form=st.empty()

        temp_dict=dict()

        with form.form('cadastro'):

            st.header('Cadastro de usuário')

            temp_dict['email']=st.text_input('E-mail',key='cad_email')
            temp_dict['senha']=st.text_input('Senha',type='password',key='cad_senha')
            temp_dict['confirma']=st.text_input('Confirmar Senha',type='password',key='cad_confirma')

            btn1,btn2=st.columns(2)
            btn_save=btn1.form_submit_button('Salvar',use_container_width=True,type='primary')
            btn_voltar=btn2.form_submit_button('Voltar',use_container_width=True,type='secondary')

            pass

        if btn_save==True:

            resp=self.ValidarCampo(temp_dict)

            if resp!=None:

                mensagem=st.warning(resp)
                time.sleep(1)
                mensagem.empty()

                pass

            else:
    
                if temp_dict['senha']!=temp_dict['confirma']:

                    mensagem=st.warning('Senha de confirmação incorreta!')
                    time.sleep(1)
                    mensagem.empty()

                    pass

                else:

                    resp=self.Salvar(temp_dict)

                    if resp==True:

                        mensagem=st.success('Dados salvo com sucesso!')
                        time.sleep(1)
                        mensagem.empty()
                        shutil.rmtree(path_base)
                        streamlit_js_eval(js_expressions='parent.window.location.reload()')

                        pass

                    else:

                        mensagem=st.warning('Não foi possível cadastrar as informações')
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    pass
                
                pass

            pass

        if btn_voltar==True:

            shutil.rmtree(path_base)
            streamlit_js_eval(js_expressions='parent.window.location.reload()')

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

    def Salvar(self,campos: dict):

        try:

            querys={

                'validar':

                """

                SELECT COUNT(*) FROM usuario WHERE EMAIL='{0}'

                """.format(campos['email']),

                'codigo':

                """

                SELECT COALESCE(MAX(CODE),0)+1 FROM usuario

                """
            }

            validar=sql.Code(querys['validar'])
            codigo=sql.Code(querys['codigo'])

            if validar<=0:

                tipo='INSERT'

                querys[tipo]=f"""

                INSERT INTO usuario(CODE,EMAIL,SENHA) VALUES({codigo},'{campos['email']}','{campos['senha']}')

                """

                pass

            else:

                tipo='UPDATE'

                querys[tipo]=f"""

                UPDATE usuario
                SET SENHA='{campos['senha']}'
                WHERE EMAIL='{campos['email']}'

                """

                pass

            sql.Save(querys[tipo])

            tipo=True

            pass

        except:

            tipo=False

            pass

        return tipo

        pass

    pass

