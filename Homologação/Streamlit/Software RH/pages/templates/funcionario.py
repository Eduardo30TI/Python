import streamlit as st
from CNPJ import CNPJ
from CEP import CEP
import time
import os
from glob import glob
from SQL import SQL
from DownloadXLSX import ExcelDW
import pandas as pd
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

querys=dict()

sql=SQL()

tabelas={

    'funcionario':

    """

    CREATE TABLE IF NOT EXISTS funcionario(
        
        CD_FUNC SMALLINT NOT NULL,
        NOME TEXT NOT NULL,
        CPF VARCHAR(250),
        SEXO CHAR(1),
        CEP VARCHAR(8),
        ENDERECO TEXT,
        BAIRRO TEXT,
        CIDADE TEXT,
        UF TEXT,
        NUMERO VARCHAR(250),
        EMAIL TEXT,
        CD_CARGO SMALLINT NOT NULL,
        STATUS BOOLEAN NOT NULL,
        DDD CHAR(2),
        CONTATO VARCHAR(250),
        DT_ADMISSAO DATE NOT NULL,
        CD_EMP SMALLINT NOT NULL,
        CD_GRAU SMALLINT NOT NULL
        
    )

    """

}

class Funcionario:

    def main(self):

        sql.CreateTable(tabelas.values())

        querys={

            'funcionario':


            """

            SELECT * FROM funcionario

            """,

            'cargo':


            """

            SELECT * FROM cargo
            WHERE STATUS=1

            """,

            'empresa':


            """

            SELECT * FROM empresa

            """,

            'escolaridade':

            """

            SELECT * FROM escolaridade
            WHERE STATUS=1

            """,

            'codigo':

            """
            
            SELECT COALESCE(MAX(CD_FUNC),0)+1 FROM funcionario

            """

        }

        df=sql.GetDados(querys)

        placeholder=st.empty()

        temp_dict=dict()

        codigo=sql.Code(querys['codigo'])
        
        with placeholder.container():

            st.header('Cadastro de colaborador')

            tab1,tab2,tab3,tab100=st.tabs(['Cadastro','Importar','Exportar','Editar'])

            with tab1:

                tab4,tab5,tab6=tab1.tabs(['Dados','Endereço','Admissão'])
                
                with tab4:
               
                    col1,col2=tab4.columns(2)
                    
                    col1.text_input('Código',key='cd_func',disabled=True,value=codigo)
                    temp_dict['status']=col2.checkbox('Status',key='st_func')

                    temp_dict['nome']=tab4.text_input('Nome',key='nome').upper()
                    
                    col3,col4=tab4.columns(2)

                    temp_dict['cpf']=col3.text_input('CPF',key='cpf')
                    temp_dict['sexo']=col4.radio('Sexo',options=['M','F'],horizontal=True)

                    temp_dict['email']=tab4.text_input('E-mail',key='email')
                    
                    pass


                with tab5:

                    col1,col2=tab5.columns(2)

                    temp_dict['cep']=col1.text_input('CEP',key='cep')

                    if temp_dict['cep']!='':
                    
                        log_dict=CEP.GetCEP(temp_dict['cep'])

                        for k,v in log_dict.items():

                            log_dict[k]=str(v).upper()

                            pass

                        temp_dict['bairro']=col2.text_input('Bairro',key='bairro',value=log_dict['bairro'])
                        temp_dict['endereco']=tab5.text_input('Endereço',key='endereco',value=log_dict['logradouro'])

                        col3,col4,col5=tab5.columns(3)

                        temp_dict['cidade']=col3.text_input('Cidade',key='cidade',value=log_dict['cidade'])
                        temp_dict['uf']=col4.text_input('UF',key='estado',value=log_dict['uf'])
                        temp_dict['numero']=col5.text_input('Número',key='numero')

                        pass

                    else:

                        temp_dict['bairro']=col2.text_input('Bairro',key='bairro')
                        temp_dict['endereco']=tab5.text_input('Endereço',key='endereco')

                        col3,col4,col5=tab5.columns(3)

                        temp_dict['cidade']=col3.text_input('Cidade',key='cidade')
                        temp_dict['uf']=col4.text_input('UF',key='estado')
                        temp_dict['numero']=col5.text_input('Número',key='numero')


                        pass


                    pass


                with tab6:

                    lista=df['empresa']['RAZAO'].unique().tolist()
                    val=tab6.selectbox('Empresa',key='empresa',options=lista)
                    temp_dict['cd_emp']=df['empresa'].loc[df['empresa']['RAZAO']==val,'CD_EMP'].values[-1]

                    col1,col2=tab6.columns(2)

                    temp_dict['ddd']=col1.text_input('DDD',key='ddd')
                    temp_dict['contato']=col2.text_input('Contato',key='contato')
                    
                    temp_dict['dt_admissao']=tab6.date_input('Data de Admissão')
                    lista=df['escolaridade']['DESCRICAO'].unique().tolist()
                    val=tab6.selectbox('Escolaridade',key='escolaridade',options=lista)
                    temp_dict['cd_grau']=df['escolaridade'].loc[df['escolaridade']['DESCRICAO']==val,'CD_GRAU'].values[-1]

                    col3,col4=tab6.columns(2)
                    
                    lista=df['cargo']['DESCRICAO'].unique().tolist()
                    val=col3.selectbox('Cargo',key='cargo',options=lista)
                    temp_dict['cd_cargo']=df['cargo'].loc[df['cargo']['DESCRICAO']==val,'CD_CARGO'].values[-1]
                    col4.text_input('Salário',key='salario',disabled=True,value=df['cargo'].loc[df['cargo']['DESCRICAO']==val,'SALARIO'].values[-1])


                    pass

                btn1,btn2=tab1.columns(2)                                
                btn_salvar=btn1.button('Salvar',type='primary',key='save',use_container_width=True)

                if btn_salvar==True:

                    resp=self.ValidarCampos(temp_dict)

                    if resp[0]!=None:

                        mensagem=tab1.warning(f'Preencher o campo {resp[0]}')
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    else:

                        resp=self.Salvar(temp_dict,'Salvar')

                        if resp==True:

                            mensagem=tab1.success('Dados salvo com sucesso')
                            time.sleep(1)
                            mensagem.empty()
                            streamlit_js_eval(js_expressions='parent.window.location.reload()')

                            pass

                        else:

                            mensagem=tab1.warning('Dados já consta no banco de dados')
                            time.sleep(1)
                            mensagem.empty()                            

                            pass

                        pass

                    pass


                pass


            with tab2:

                with tab2.expander('Cadastro massivo de colaboradores.'):

                    colunas=[l for l in df['funcionario'].columns.tolist() if not l in ['CD_FUNC','ENDERECO','BAIRRO','CIDADE','UF']]

                    temp_df=pd.DataFrame(columns=colunas)

                    data=ExcelDW.DownloadXLSX(temp_df)
                    st.download_button('Base EXCEL',data=data,file_name='Base.xlsx')

                    pass

                files=tab2.file_uploader('Importar',type=['.xlsx'],accept_multiple_files=False)

                progress=tab2.progress(0)

                btn=tab2.button('Importar',key='btn_importar',type='primary')

                if btn==True:

                    if files==None:

                        mensagem=tab2.warning('Não tem arquivos para serem inseridos!')
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    else:
                    
                        excel_df=pd.read_excel(files)

                        excel_df['CEP']=excel_df['CEP'].apply(CEP.ValidarCEP)

                        for i in range(0,len(excel_df)):

                            cep=excel_df.loc[i,'CEP']

                            log_dict=CEP.GetCEP(cep)

                            temp_dict={'logradouro':'ENDERECO','bairro':'BAIRRO','cidade':'CIDADE','uf':'UF'}

                            for k,v in temp_dict.items():

                                excel_df.loc[i,v]=str(log_dict[k]).upper()

                                pass

                            pass
                        
                        colunas=[{l:str(l).lower()} for l in excel_df.columns.tolist()]

                        for c in colunas:

                            excel_df.rename(columns=c,inplace=True)
                            
                            pass

                        for c in excel_df.columns.tolist():

                            excel_df[c]=excel_df[c].apply(lambda info: str(info).upper())

                            pass

                        for i in range(0,len(excel_df)):

                            log_dict=excel_df.loc[i].to_dict()

                            progress.progress(int(i))
                            time.sleep(5)

                            resp=self.Salvar(log_dict,'Editar')

                            if resp==True:

                                mensagem=tab2.success('Dados importados com sucesso')
                                time.sleep(1)
                                mensagem.empty()
                                streamlit_js_eval(js_expressions='parent.window.location.reload()')

                                pass

                            pass

                        pass

                    pass

                pass


            with tab3:

                colunas=df['funcionario'].columns.tolist()
                col_leach=tab3.selectbox('Filtrar',options=colunas)

                temp_df=pd.DataFrame(columns=colunas)

                for c in colunas:

                    df['funcionario'][c]=df['funcionario'][c].astype(str)

                    pass
                
                leach=tab3.text_input('Pesquisar',label_visibility='collapsed',placeholder='Pesquisar').upper()

                colunas=[l for l in colunas if l!='CPF']

                if leach=='':

                    tab3.dataframe(df['funcionario'])

                    pass

                else:

                    temp_df=df['funcionario'][colunas].loc[df['funcionario'][col_leach].str.contains(leach)]
                    tab3.dataframe(temp_df)


                    pass

                data=ExcelDW.DownloadXLSX(temp_df)

                tab3.download_button('Download XLSX',data=data,file_name='Funcionário.xlsx')

                pass

            with tab100:

                if len(df['funcionario'])>0:

                    tab4,tab5,tab6=tab100.tabs(['Dados','Endereço','Admissão'])
                                    
                    with tab4:
                
                        col1,col2=tab4.columns(2)
                        
                        val=col1.selectbox('Código',key='cd_func_edit',options=df['funcionario']['CD_FUNC'].unique().tolist())
                        
                        temp_df=df['funcionario'].loc[df['funcionario']['CD_FUNC']==val]

                        temp_dict['status']=col2.checkbox('Status',key='st_func_edit',value=temp_df['STATUS'].values[-1])

                        temp_dict['nome']=tab4.text_input('Nome',key='nome_edit',value=temp_df['NOME'].values[-1]).upper()
                        
                        col3,col4=tab4.columns(2)

                        temp_dict['cpf']=col3.text_input('CPF',key='cpf_edit',value=temp_df['CPF'].values[-1])
                        temp_dict['sexo']=col4.radio('Sexo',key='sexo_edit',options=['M','F'],horizontal=True)
                
                        temp_dict['email']=tab4.text_input('E-mail',key='email_edit',value=temp_df['EMAIL'].values[-1])
                        
                        pass


                    with tab5:

                        col1,col2=tab5.columns(2)

                        temp_dict['cep']=col1.text_input('CEP',key='cep_edit',value=temp_df['CEP'].values[-1])

                        if temp_dict['cep']!='':
                        
                            log_dict=CEP.GetCEP(temp_dict['cep'])

                            for k,v in log_dict.items():

                                log_dict[k]=str(v).upper()

                                pass

                            temp_dict['bairro']=col2.text_input('Bairro',key='bairro_edit',value=log_dict['bairro'])
                            temp_dict['endereco']=tab5.text_input('Endereço',key='endereco_edit',value=log_dict['logradouro'])

                            col3,col4,col5=tab5.columns(3)

                            temp_dict['cidade']=col3.text_input('Cidade',key='cidade_edit',value=log_dict['cidade'])
                            temp_dict['uf']=col4.text_input('UF',key='estado_edit',value=log_dict['uf'])
                            temp_dict['numero']=col5.text_input('Número',key='numero_edit',value=temp_df['NUMERO'].values[-1])

                            pass

                        else:

                            temp_dict['bairro']=col2.text_input('Bairro',key='bairro_edit')
                            temp_dict['endereco']=tab5.text_input('Endereço',key='endereco_edit')

                            col3,col4,col5=tab5.columns(3)

                            temp_dict['cidade']=col3.text_input('Cidade',key='cidade_edit')
                            temp_dict['uf']=col4.text_input('UF',key='estado_edit')
                            temp_dict['numero']=col5.text_input('Número',key='numero_edit')

                            pass


                        pass


                    with tab6:

                        lista=df['empresa']['RAZAO'].unique().tolist()
                        val=tab6.selectbox('Empresa',key='empresa_edit',options=lista)
                                
                        temp_dict['cd_emp']=df['empresa'].loc[df['empresa']['RAZAO']==val,'CD_EMP'].values[-1]

                        col1,col2=tab6.columns(2)

                        temp_dict['ddd']=col1.text_input('DDD',key='ddd_edit',value=temp_df['DDD'].values[-1])
                        temp_dict['contato']=col2.text_input('Contato',key='contato_edit',value=temp_df['CONTATO'].values[-1])
                        
                        temp_dict['dt_admissao']=tab6.date_input('Data de Admissão',key='dt_admissao_edit',value=datetime.strptime(temp_df['DT_ADMISSAO'].values[-1],'%Y-%m-%d'))
                        lista=df['escolaridade']['DESCRICAO'].unique().tolist()
                        val=tab6.selectbox('Escolaridade',key='escolaridade_edit',options=lista)
                        temp_dict['cd_grau']=df['escolaridade'].loc[df['escolaridade']['DESCRICAO']==val,'CD_GRAU'].values[-1]

                        col3,col4=tab6.columns(2)
                        
                        lista=df['cargo']['DESCRICAO'].unique().tolist()
                        val=col3.selectbox('Cargo',key='cargo_edit',options=lista)
                        temp_dict['cd_cargo']=df['cargo'].loc[df['cargo']['DESCRICAO']==val,'CD_CARGO'].values[-1]
                        col4.text_input('Salário',key='salario_edit',disabled=True,value=df['cargo'].loc[df['cargo']['DESCRICAO']==val,'SALARIO'].values[-1])


                        pass

                    btn1,btn2=tab100.columns(2)                                
                    btn_editar=btn1.button('Editar',type='primary',key='edit',use_container_width=True)

                    if btn_editar==True:

                        resp=self.ValidarCampos(temp_dict)

                        if resp[0]!=None:

                            mensagem=tab1.warning(f'Preencher o campo {resp[0]}')
                            time.sleep(1)
                            mensagem.empty()

                            pass

                        else:

                            resp=self.Salvar(temp_dict,'Editar')

                            if resp==True:

                                mensagem=tab100.success('Dados editados com sucesso')
                                time.sleep(1)
                                mensagem.empty()
                                streamlit_js_eval(js_expressions='parent.window.location.reload()')

                                pass

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

            if str(v)=='':

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

            SELECT COALESCE(MAX(CD_FUNC),0)+1 FROM funcionario

            """,

            'validar':

            """

            SELECT COUNT(*) FROM funcionario WHERE CPF='{0}'

            """.format(dados_dict['cpf']),

            'UPDATE':

            """
            UPDATE funcionario
            SET NOME='{1}',
            SEXO='{2}',
            CEP='{3}',
            ENDERECO='{4}',
            BAIRRO='{5}',
            CIDADE='{6}',
            UF='{7}',
            NUMERO='{8}',
            EMAIL='{9}',
            CD_CARGO='{10}',
            STATUS={11},
            DDD='{12}',
            CONTATO='{13}',
            DT_ADMISSAO='{14}',
            CD_EMP={15},
            CD_GRAU={16}
            WHERE CPF={0}

            """.format(dados_dict['cpf'],dados_dict['nome'],dados_dict['sexo'],dados_dict['cep'],dados_dict['endereco'],dados_dict['bairro'],dados_dict['cidade'],dados_dict['uf'],dados_dict['numero'],dados_dict['email'],dados_dict['cd_cargo'],dados_dict['status'],dados_dict['ddd'],dados_dict['contato'],dados_dict['dt_admissao'],dados_dict['cd_emp'],dados_dict['cd_grau'])

            
        }


        codigo=sql.Code(querys['codigo'])
        validar=sql.Code(querys['validar'])

        resp=True

        if validar<=0:

            tipo='INSERT'

            querys[tipo]="""

            INSERT INTO funcionario (CD_FUNC,NOME,CPF,SEXO,CEP,ENDERECO,BAIRRO,CIDADE,UF,NUMERO,EMAIL,CD_CARGO,STATUS,DDD,CONTATO,DT_ADMISSAO,CD_EMP,CD_GRAU) VALUES({0},'{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}',{11},'{12}',{13},'{14}','{15}',{16},{17})

            """.format(codigo,dados_dict['nome'],dados_dict['cpf'],dados_dict['sexo'],dados_dict['cep'],dados_dict['endereco'],dados_dict['bairro'],dados_dict['cidade'],dados_dict['uf'],dados_dict['numero'],dados_dict['email'],dados_dict['cd_cargo'],dados_dict['status'],dados_dict['ddd'],dados_dict['contato'],dados_dict['dt_admissao'],dados_dict['cd_emp'],dados_dict['cd_grau'])

            sql.Save(querys[tipo])

            pass

        else:

            tipo='UPDATE'

            if btn=='Salvar':

                resp=False

                pass


            else:

                sql.Save(querys[tipo])

                pass

            pass
        
        return resp

        pass

    pass