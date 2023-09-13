import streamlit as st
from pages.templates import *
import time
import socket as s
import os
from glob import glob
from SQL import SQL

sql=SQL()

querys=dict()

def main():

    IP=s.gethostbyname(s.gethostname())

    path_base=os.path.join(os.getcwd(),IP)
    os.makedirs(path_base,exist_ok=True)

    temp_nav={'cadastro.txt':'Cadastro','menu.txt':'Menu'}
       
    temp_path=os.path.join(path_base,'*.txt*')
    arq=glob(temp_path)

    if len(arq)<=0:
    
        placeholder=st.empty()

        temp_dict={'Login':'','Senha':''}

        with placeholder.form(key='login'):

            st.header('Acesso do RH')
            st.text('Software para gerenciamento de pessoas')
            st.markdown('----')
            
            temp_dict['Login']=st.text_input('Usuário',placeholder='Informe o e-mail',key='user').lower()
            temp_dict['Senha']=st.text_input('Senha',type='password',placeholder='Informe a senha',key='password')
            btn1,btn2=st.columns(2)
            btn_log=btn1.form_submit_button('Logar',use_container_width=True,type='primary')
            btn_user=btn2.form_submit_button('Cadastro',use_container_width=True,type='secondary')

            pass
        
        if btn_log==True:

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

            if cont>1:

                querys['LOG']="""

                SELECT * FROM acesso

                """

                df=sql.GetDataframe(querys['LOG'])

                row=df.loc[(df['USUARIO']==temp_dict['Login'])&(df['SENHA']==temp_dict['Senha']),'CD_USER'].count()

                if row>0:

                    mensagem=st.success('Conectado')
                    time.sleep(2)
                    mensagem.empty()

                    placeholder.empty()

                    temp_path=os.path.join(path_base,'menu.txt')
                    arq=glob(temp_path)

                    with open(temp_path,'w') as file:

                        file.write(temp_dict['Login'])

                        pass
                    
                    tela=Menu()
                    tela.main()
          
                    pass

                else:

                    mensagem=st.warning('Usuário não encontrado no banco de dados!')
                    time.sleep(1)
                    mensagem.empty()

                    pass
                

                pass

            pass

        elif btn_user==True:

            placeholder.empty()

            temp_path=os.path.join(path_base,'cadastro.txt')

            with open(temp_path,'w') as file:

                file.write('')

                pass

            tela=Cadastro()
            tela.main()

            pass

        pass

    else:

        arq=os.path.basename(arq[-1])

        tela=globals().get(temp_nav[arq])()
        tela.main()

        pass

    pass


if __name__=='__main__':

    main()

    pass