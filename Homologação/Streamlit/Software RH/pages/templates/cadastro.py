import streamlit as st
import os
from glob import glob
import socket as s
import time
import pandas as pd
from SQL import SQL
from streamlit_js_eval import streamlit_js_eval

sql=SQL()

querys=dict()

tabelas={

    'Acesso':

    """

    CREATE TABLE IF NOT EXISTS acesso(
    
        CD_USER SMALLINT NOT NULL,
        USUARIO TEXT NOT NULL,
        SENHA TEXT NOT NULL

    )

    """
}

class Cadastro:

    def main(self):

        sql.CreateTable(tabelas.values())

        temp_path=os.path.join(os.getcwd(),'RelatorioContas.xlsx')
        df=pd.read_excel(temp_path)

        placeholder=st.empty()

        temp_dict={'Login':'','Senha':'','Confirmar':''}

        with placeholder.form(key='cadastro'):

            st.header('Cadastro de Usuário')
            st.markdown('----')
            
            temp_dict['Login']=st.text_input('Usuário',placeholder='Informe o e-mail',key='cad_user').lower()
            temp_dict['Senha']=st.text_input('Senha',type='password',placeholder='Informe a senha',key='cad_password')
            temp_dict['Confirmar']=st.text_input('Confirmar',type='password',placeholder='Confirmar senha',key='confirmar')
            btn1,btn2=st.columns(2)
            btn_save=btn1.form_submit_button('Salvar',use_container_width=True)
            btn_voltar=btn2.form_submit_button('<< Voltar',use_container_width=True)

            pass

        if btn_save==True:

            cont=0

            for k,v in temp_dict.items():

                if v=='':

                    mensagem=st.warning(f'Preencher o campo {k}.')
                    time.sleep(1)
                    mensagem.empty()

                    break

                else:

                    cont+=1

                    pass

                pass

            
            if cont>2:

                if len(df.loc[df['Nome']==temp_dict['Login']])<=0:

                    mensagem=st.warning('Usuário invalido!')
                    time.sleep(1)
                    mensagem.empty()

                    pass 

                elif temp_dict['Senha']!=temp_dict['Confirmar']:

                    mensagem=st.warning('Senha de confirmação não é valida.')
                    time.sleep(1)
                    mensagem.empty()

                    pass

                else:

                    querys['CODE']="""

                    SELECT COUNT(CD_USER)+1 FROM acesso

                    """

                    querys['VALIDE']="""

                    SELECT COUNT(CD_USER) FROM acesso WHERE usuario='{0}'

                    """.format(temp_dict['Login'])

                    codigo=sql.Code(querys['CODE'])
                    valide=sql.Code(querys['VALIDE'])

                    if valide==0:

                        tipo='INSERT'

                        querys[tipo]="""

                        INSERT INTO acesso (CD_USER,USUARIO,SENHA) VALUES({0},'{1}','{2}')

                        """.format(codigo,temp_dict['Login'],temp_dict['Senha'])

                        pass


                    else:

                        tipo='UPDATE'

                        querys[tipo]="""

                        UPDATE acesso
                        SET SENHA='{1}'
                        WHERE USUARIO='{0}'

                        """.format(temp_dict['Login'],temp_dict['Senha'])

                        pass

                    sql.Save(querys[tipo])

                    mensagem=st.success('Dados salvo com sucesso!')
                    time.sleep(1)
                    mensagem.empty()
                    time.sleep(1)

                    IP=s.gethostbyname(s.gethostname())

                    path_base=os.path.join(os.getcwd(),IP)
                    os.makedirs(path_base,exist_ok=True)
                    temp_path=os.path.join(path_base,'cadastro.txt')
                    arq=glob(temp_path)

                    os.remove(arq[-1])
                    streamlit_js_eval(js_expressions='parent.window.location.reload()')

                    pass

                pass

            pass

        elif btn_voltar==True:

            IP=s.gethostbyname(s.gethostname())

            path_base=os.path.join(os.getcwd(),IP)
            os.makedirs(path_base,exist_ok=True)
            temp_path=os.path.join(path_base,'cadastro.txt')
            arq=glob(temp_path)

            os.remove(arq[-1])
            streamlit_js_eval(js_expressions='parent.window.location.reload()')

            pass


        pass


    pass
