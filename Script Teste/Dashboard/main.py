import streamlit as st
import pandas as pd

# texto
st.header('Seja bem vindo')
st.sidebar.image('https://demarchi.com.br/images/logo/logo-demarchi.png')
st.sidebar.header('Dasboard Python - primeiro programa')

st.sidebar.text_input('Digite')

st.markdown('~~Meu Menu~~')
st.caption('Esse é uma aula teste de python')

pessoas=[{'Nome':'Eduardo','Idade': 29},{'Nome':'Dayane','Idade': 32}]

st.write('# Pessoas',pessoas)

#Exibir dados

