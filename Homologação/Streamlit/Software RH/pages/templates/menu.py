import streamlit as st
import socket as s
from glob import glob
import os
from streamlit_js_eval import streamlit_js_eval
from .empresa import Empresa
from .funcionario import Funcionario
from .area import Area
from .cargos import Cargo
from .escolaridade import Escolaridade

class Menu:

    def main(self):

        IP=s.gethostbyname(s.gethostname())

        path_base=os.path.join(os.getcwd(),IP)
        os.makedirs(path_base,exist_ok=True)

        temp_path=os.path.join(path_base,'menu.txt')

        user=None

        with open(temp_path,'r') as file:

            user=file.read().strip()

            pass

        placeholder=st.empty()

        with placeholder.container():
            
            sidebar=st.sidebar

            sidebar.title(f'Usuário Logado: {user}')
            btn_close=sidebar.button('Sair',type='primary')
            sidebar.markdown('----')
            val=sidebar.selectbox('Opções',options=['Empresa','Área','Cargo','Escolaridade','Funcionario'])

           
            if val=='Empresa':

                tela=Empresa()
                tela.main()

                pass

            elif val=='Funcionario':

                tela=Funcionario()
                tela.main()

                pass


            elif val=='Área':

                tela=Area()
                tela.main()

                pass

            elif val=='Cargo':

                tela=Cargo()
                tela.main()

                pass

            elif val=='Escolaridade':

                tela=Escolaridade()
                tela.main()

                pass

            pass

        if btn_close==True:

            placeholder.empty()
            
            os.remove(temp_path)
            streamlit_js_eval(js_expressions='parent.window.location.reload()')

            pass

        pass

    pass