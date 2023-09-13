from glob import glob
import os
import streamlit as st
import time
from glob import glob
import pages.interface as gui
import socket as s
from SQL import SQL
from streamlit_js_eval import streamlit_js_eval

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

def Main():

    sql.CreateTable(tabelas.values())

    IP=s.gethostbyname(s.gethostname())
    temp_path=os.path.join(os.getcwd(),IP,'*.txt*')

    form=st.empty()

    temp_dict=dict()    

    arq=glob(temp_path)

    if len(arq)>0:

        path_name=os.path.basename(arq[-1])

        if path_name=='cadastro.txt':

            tela=gui.Usuario()
            tela.main()
            form.empty()

            pass

        elif path_name=='menu.txt':

            with open(arq[-1],'r') as file:

                user=file.read()

                pass

            tela=gui.Menu(user)
            tela.main()
            form.empty()            

            pass

        pass

    else:

        with form.form('login',clear_on_submit=False):

            st.header('Login')
            st.markdown('----')

            temp_dict['email']=st.text_input(label='E-mail',key='email')
            temp_dict['senha']=st.text_input(label='Senha',type='password',key='senha')

            btn1,btn2=st.columns(2)
            btn_logar=btn1.form_submit_button('Entrar',use_container_width=True,type='primary')
            btn_cad=btn2.form_submit_button('Cadastro',use_container_width=True)

            pass

        if btn_logar==True:

            resp=ValidarCampo(temp_dict)

            if resp!=None:
                
                mensagem=st.warning(resp)
                time.sleep(1)
                mensagem.empty()

                pass

            else:

                resp=Logar(temp_dict)

                if resp==1:

                    mensagem=st.success('Seja bem vindo')
                    time.sleep(1)
                    mensagem.empty()

                    resp=Navegar('menu',temp_dict['email'])

                    if resp==True:

                        tela=gui.Menu(temp_dict['email'])
                        tela.main()
                        form.empty()

                        pass

                    pass

                else:

                    mensagem=st.warning('Usuário não encontrado no banco de dados.')
                    time.sleep(1)
                    mensagem.empty()

                    pass

                pass

            pass

        if btn_cad==True:

            resp=Navegar('cadastro',temp_dict['email'])

            if resp==True:

                tela=gui.Usuario()
                tela.main()
                form.empty()

                pass            

            pass

        pass

    pass


def ValidarCampo(campos: dict):

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

def Logar(campos: dict):

    querys={

        'validar':

        """
        
        SELECT COUNT(*) FROM usuario WHERE EMAIL='{0}' AND SENHA='{1}'

        """.format(campos['email'],campos['senha'])
    }

    validar=sql.Code(querys['validar'])

    return validar

    pass

def Navegar(tela: str,user: str):

    IP=s.gethostbyname(s.gethostname())
    path_base=os.path.join(os.getcwd(),IP)
    temp_path=os.path.join(path_base,f'{tela}.txt')

    os.makedirs(path_base,exist_ok=True)

    arq=glob(temp_path)

    resp=False

    if len(arq)<=0:

        with open(temp_path,'w') as file:

            file.write(user)

            pass

        resp=True

        pass

    else:

        resp=True

        pass

    return resp

    pass


if __name__=='__main__':

    Main()

    pass