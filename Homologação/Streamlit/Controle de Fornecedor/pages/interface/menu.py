import streamlit as st
from .importador import Importador
from .agenda import Agendamento
from .manual import Controle
import socket as s
import shutil
from streamlit_js_eval import streamlit_js_eval
import os

telas=['Importador XML','Agenda','Controle de Agenda']

class Menu:

    def __init__(self,usuario):

        self.user=usuario

        pass


    def main(self):

        placeholder=st.empty()

        with placeholder.container():

            sidebar=st.sidebar
            sidebar.header(f'Usuário: {self.user}')
            btn=sidebar.button('Logout',key='sair')
            sidebar.markdown('----')

            val=sidebar.selectbox('Tela',options=telas)
            
            if val=='Importador XML':

                tela=Importador(val)
                tela.main()

                pass

            elif val=='Agenda':

                tela=Agendamento(val)
                tela.main()

                pass

            elif val=='Controle de Agenda':

                tela=Controle(val)
                tela.main()

                pass                       

            pass

        if btn==True:

            IP=s.gethostbyname(s.gethostname())
            path_base=os.path.join(os.getcwd(),IP)
            shutil.rmtree(path_base)
                        
            streamlit_js_eval(js_expressions='parent.window.location.reload()')

            pass

        pass


    pass