import streamlit as st
from CNPJ import CNPJ
from CEP import CEP
import time
import os
from glob import glob
from SQL import SQL
from DownloadXLSX import ExcelDW
from streamlit_js_eval import streamlit_js_eval

sql=SQL()

querys=dict()

tabelas={
    
    'empresa':

    """
    
    CREATE TABLE IF NOT EXISTS empresa(
    
        CD_EMP SMALLINT NOT NULL,
        CNPJ VARCHAR(250) NOT NULL,
        RAZAO VARCHAR(250) NOT NULL,
        FANTASIA VARCHAR(250) NOT NULL,
        CEP VARCHAR(8) NOT NULL,
        ENDERECO VARCHAR(250) NOT NULL,
        BAIRRO VARCHAR(250) NOT NULL,
        CIDADE VARCHAR(250) NOT NULL,
        UF CHAR(2) NOT NULL,
        NUMERO VARCHAR(250) NOT NULL

    )

    """
}

class Empresa:

    def main(self):

        sql.CreateTable(tabelas.values())

        placeholder=st.empty()

        label_cnpj=None

        temp_dict=dict()

        with placeholder.container():

            st.header('Cadastro de empresa')

            tab1,tab2=st.tabs(['Empresa','Lista'])

            querys['Empresa']="""

            SELECT * FROM empresa

            """

            df=sql.GetDataframe(querys['Empresa'])

            for c in df.columns.tolist():

                df[c]=df[c].astype(str)

                pass

            leach_col=tab2.selectbox('Filtrar',options=df.columns.tolist())
            leach=tab2.text_input(label='Pesquisa',placeholder='Digite dados para pesquisa').upper()
            tab2.dataframe(df.loc[df[leach_col].str.contains(leach)])
            data=ExcelDW.DownloadXLSX(df)
            tab2.download_button('Exportar',data=data,file_name='Empresa.xlsx')

            col1,col2=tab1.columns(2)

            label_cnpj=col1.text_input('CNPJ',key='cnpj')
            temp_dict['cnpj']=label_cnpj

            if label_cnpj!='':

                json=CNPJ(label_cnpj)
                json=json.GetDados()

                temp_dict['razao_social']=tab1.text_input('Razão Social',value=json['razao_social'],disabled=True)
                temp_dict['nome_fantasia']=tab1.text_input('Nome Fantasia',value=json['nome_fantasia'],disabled=True)
                
                col3,col4=tab1.columns(2)
                cep=col3.text_input('CEP')

                temp_dict['cep']=cep
                
                if cep!='':

                    if len(cep)==8 and cep.isnumeric():

                        json=CEP.GetCEP(cep)

                        temp_dict['bairro']=col4.text_input('Bairro',value=str(json['bairro']).upper())
                        temp_dict['logradouro']=tab1.text_input('Endereço',value=str(json['logradouro']).upper())

                        col5,col6,col7=tab1.columns(3)
                        temp_dict['cidade']=col5.text_input('Cidade',value=str(json['cidade']).upper())
                        temp_dict['uf']=col6.text_input('UF',value=str(json['uf']).upper())
                        temp_dict['numero']=col7.text_input('Número')

                        pass

                    else:
                        
                        mensagem=st.warning('CEP invalido!')
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    pass

                btn=tab1.button('Salvar',type='primary')

                if btn==True:

                    cont=0

                    for k,v in temp_dict.items():

                        if v=='':

                            mensagem=st.warning(f'Informe o {k}')
                            time.sleep(1)
                            mensagem.empty()

                            break

                        else:
                            
                            cont+=1

                            pass

                        pass

                    if cont>0:

                        self.Insert(temp_dict,tab1)

                        pass

                    pass

                pass
            
            pass

        pass


    def Insert(self,dados_dict: dict,form):

        querys={

            'CODIGO':


            """

            SELECT COALESCE(MAX(CD_EMP),0)+1 FROM empresa

            """,

            'VALIDAR':

            """

            SELECT COUNT(*) FROM empresa WHERE CNPJ='{0}'

            """.format(dados_dict['cnpj'])
        }

        codigo=sql.Code(querys['CODIGO'])
        validar=sql.Code(querys['VALIDAR'])

        if validar<=0:

            tipo='INSERT'

            querys[tipo]="""
            
            INSERT INTO empresa (CD_EMP,CNPJ,RAZAO,FANTASIA,CEP,ENDERECO,BAIRRO,CIDADE,UF,NUMERO) VALUES({0},'{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')

            """.format(codigo,dados_dict['cnpj'],dados_dict['razao_social'],dados_dict['nome_fantasia'],dados_dict['cep'],dados_dict['logradouro'],dados_dict['bairro'],dados_dict['cidade'],dados_dict['uf'],dados_dict['numero'])

            pass


        else:

            tipo='UPDATE'

            querys[tipo]="""

            UPDATE empresa
            SET CEP='{1}',
            ENDERECO='{2}',
            BAIRRO='{3}',
            CIDADE='{4}',
            UF='{5}',
            NUMERO='{6}'
            WHERE CNPJ='{0}'

            """.format(dados_dict['cnpj'],dados_dict['cep'],dados_dict['logradouro'],dados_dict['bairro'],dados_dict['cidade'],dados_dict['uf'],dados_dict['numero'])

            pass

        sql.Save(querys[tipo])

        mensagem=form.success('Dados salvo com sucesso!')
        time.sleep(1)
        mensagem.empty()
        time.sleep(1)
        streamlit_js_eval(js_expressions='parent.window.location.reload()')

        pass

    pass