import warnings
import streamlit as st
from pages.tela import*


warnings.filterwarnings('error')

def Main():

    lista=['Consultar CNPJ','Google Telefone']

    sidebar=st.sidebar
    sidebar.title('Menu')
    sidebar.text('Consultar lista de contato pelo Google')
    sidebar.markdown('----')

    val=sidebar.selectbox('Telas',options=lista)

    if val=='Consultar CNPJ':

        tela=Consultar(val)
        tela.main()

        pass

    elif val=='Google Telefone':

        tela=GS(val)
        tela.main()

        pass

    pass


if __name__=='__main__':

    Main()

    pass