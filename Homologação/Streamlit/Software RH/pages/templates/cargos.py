import streamlit as st
import time
import os
from glob import glob
from SQL import SQL
from streamlit_js_eval import streamlit_js_eval

sql = SQL()

querys = dict()

tabelas = {

    'Cargo':

    """

    CREATE TABLE IF NOT EXISTS cargo(
    
        CD_CARGO SMALLINT NOT NULL,
        DESCRICAO TEXT NOT NULL,
        STATUS BOOLEAN NOT NULL,
        CD_AREA SMALLINT NOT NULL,
        SALARIO DECIMAL(15,2) NOT NULL

    )

    """


}


class Cargo:

    def main(self):

        sql.CreateTable(tabelas.values())

        querys = {

            'Area':

            """

            SELECT * FROM area
            WHERE STATUS=True

            """,

            'CODIGO':

            """

            SELECT COALESCE(MAX(CD_CARGO),0)+1 FROM cargo

            """,

            'Cargo':

            """

            SELECT * FROM cargo

            """
        }

        placeholder = st.empty()

        temp_dict = dict()

        df=sql.GetDados(querys)

        codigo=sql.Code(querys['CODIGO'])

        with placeholder.container():

            tab1, tab2 = st.tabs(['Salvar', 'Editar'])

            # tab1 - salvar

            with tab1:

                col1, col2 = tab1.columns(2)
                temp_dict['codigo'] = col1.text_input('Código', key='cd_cargo',value=codigo,disabled=True)
                temp_dict['status'] = col2.checkbox('Status', key='st_cargo')
                
                temp_dict['cargo']=tab1.text_input('Cargo', key='cargo').upper().strip()

                col3,col4=tab1.columns(2)

                val=col3.selectbox('Área',options=df['Area'].loc[df['Area']['STATUS']==True,'DESCRICAO'].unique().tolist(),key='cd_area')
                temp_dict['cd-area']=df['Area'].loc[df['Area']['DESCRICAO']==val,'CD_AREA'].values[-1]
                temp_dict['salario']=col4.text_input('Salário',key='salario')

                with tab1.expander('Lista',expanded=False):

                    st.dataframe(df['Cargo'],use_container_width=True)

                    pass

                btn=tab1.button('Salvar',type='primary')

                if btn==True:

                    resp=self.ValidarCampos(temp_dict)

                    if resp[0]!=None:
                        
                        mensagem=tab1.warning(f'Preencher o campo {resp[0]}')
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    else:

                        resp=self.Salvar(temp_dict)

                        if resp==True:

                            mensagem=tab1.success('Dados salvo com sucesso')
                            time.sleep(1)
                            mensagem.empty()
                            time.sleep(1)
                            streamlit_js_eval(js_expressions='parent.window.location.reload()')

                            pass

                        pass

                    pass

                pass

            # tab2 - editar

            with tab2:

                col1, col2 = tab2.columns(2)

                if len(df['Cargo'])>0:

                    temp_dict['codigo']=col1.selectbox('Código',options=df['Cargo']['CD_CARGO'].unique().tolist())

                    temp_dict['status'] = col2.checkbox('Status',value=df['Cargo'].loc[df['Cargo']['CD_CARGO']==temp_dict['codigo'],'STATUS'].values[-1], key='st_cargo_edi')
                    
                    temp_dict['cargo']=tab2.text_input('Cargo',value=df['Cargo'].loc[df['Cargo']['CD_CARGO']==temp_dict['codigo'],'DESCRICAO'].values[-1], key='cargo_edi').upper()

                    col3,col4=tab2.columns(2)

                    val=col3.selectbox('Área',options=df['Area'].loc[df['Area']['STATUS']==True,'DESCRICAO'].unique().tolist(),key='cd_area_edi')
                    temp_dict['cd-area']=df['Area'].loc[df['Area']['DESCRICAO']==val,'CD_AREA'].values[-1]
                    temp_dict['salario']=col4.text_input('Salário',value=df['Cargo'].loc[df['Cargo']['CD_CARGO']==temp_dict['codigo'],'SALARIO'].values[-1],key='salario_edi')

                    pass

                else:

                    temp_dict['codigo']=col1.selectbox('Código',options=[])

                    temp_dict['status'] = col2.checkbox('Status', key='st_cargo_edi')
                    
                    temp_dict['cargo']=tab2.text_input('Cargo', key='cargo_edi').upper()

                    col3,col4=tab2.columns(2)

                    val=col3.selectbox('Área',options=[],key='cd_area_edi')
                    temp_dict['salario']=col4.text_input('Salário',key='salario_edi')

                    pass

                btn=tab2.button('Editar',type='primary',key='btn_edit')

                if btn==True:

                    resp=self.ValidarCampos(temp_dict)

                    if resp[0]!=None:

                        mensagem=tab2.warning(f'Preencher o campo {resp[0]}')
                        time.sleep(1)
                        mensagem.empty()

                        pass


                    else:

                        resp=self.Salvar(temp_dict)

                        if resp==True:

                            mensagem=tab2.success('Dados salvo com sucesso.')
                            time.sleep(1)
                            mensagem.empty()
                            streamlit_js_eval(js_expressions='parent.window.location.reload()')

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

            if v=='':

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

    def Salvar(self,dados_dict):

        querys={

            'validar':

            """
            
            SELECT COUNT(*) FROM cargo WHERE descricao='{0}'
            
            """.format(dados_dict['cargo']),

            'codigo':


            """
            
            SELECT COALESCE(MAX(CD_CARGO),0)+1 FROM cargo

            """

        }

        valide=sql.Code(querys['validar'])
        codigo=sql.Code(querys['codigo'])

        if valide<=0:

            tipo='INSERT'

            querys[tipo]="""
            
            INSERT INTO cargo (CD_CARGO,DESCRICAO,STATUS,CD_AREA,SALARIO) VALUES({0},'{1}',{2},{3},{4})            
            
            """.format(codigo,dados_dict['cargo'],dados_dict['status'],dados_dict['cd-area'],dados_dict['salario'])

            pass


        else:

            tipo='UDPATE'

            querys[tipo]="""
            
            UPDATE cargo
            SET DESCRICAO='{1}',
            STATUS={2},
            CD_AREA={3},
            SALARIO={4}
            WHERE CD_AREA={0}

            """.format(dados_dict['codigo'],dados_dict['cargo'],dados_dict['status'],dados_dict['cd-area'],dados_dict['salario'])

            pass

        sql.Save(querys[tipo])

        return True        

        pass

    pass
