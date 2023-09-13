import streamlit as st
import time
import os
from glob import glob
from SQL import SQL
from streamlit_js_eval import streamlit_js_eval

sql=SQL()

querys=dict()

tabela={

    'Area':

    """

    CREATE TABLE IF NOT EXISTS area(
    
        CD_AREA SMALLINT NOT NULL,
        DESCRICAO VARCHAR(250) NOT NULL,
        STATUS BOOLEAN NOT NULL

    )

    """

}

class Area:

    def main(self):

        temp_dict=dict()
        
        sql.CreateTable(tabela.values())

        placeholder=st.empty()

        querys={

            'Area':

            """

            SELECT * FROM area

            """
        }

        df=sql.GetDados(querys)

        with placeholder.container():

            tab1,tab2=st.tabs(['Salvar','Editar'])

            #tab1- área
            
            with tab1:

                #salvar
                querys['CODIGO']="""

                SELECT COALESCE(MAX(CD_AREA),0) FROM area

                """

                codigo=sql.Code(querys['CODIGO'])
                codigo=1 if codigo==0 else codigo+1
                
                col1,col2=tab1.columns(2)

                temp_dict['codigo']=col1.text_input('Código',key='cd_area',disabled=True,value=codigo)
                temp_dict['status']=col2.checkbox('Status',key='st_area')

                temp_dict['area']=tab1.text_input('Área',key='area').upper().strip()
                
                with tab1.expander('Lista',expanded=False):

                    st.dataframe(df['Area'],use_container_width=True)

                    pass
                
                btn_save=tab1.button('Salvar',key='save_area',type='primary')

                if btn_save==True:
                    
                    retorno=self.ValidarCampos(temp_dict)

                    if retorno[0]!=None:

                        mensagem=tab1.warning(f'Preencher o campo {retorno[0]}')
                        time.sleep(1)
                        mensagem.empty()

                        pass


                    else:

                        resp=self.Save_Area(temp_dict)

                        if resp==True:

                            mensagem=tab1.success('Dados salvo com sucesso!')
                            time.sleep(1)
                            mensagem.empty()
                            streamlit_js_eval(js_expressions='parent.window.location.reload()')


                            pass

                        pass

                    pass

                pass

            pass            

            #tab2- cargo
            with tab2:

                if len(df['Area'])>0:
                
                    temp_dict['codigo']=st.selectbox('Código',options=df['Area']['CD_AREA'].unique().tolist(),key='area_cd_edit')
                    col1,col2=st.columns(2)
                    temp_dict['area']=col1.text_input('Área',value=df['Area'].loc[df['Area']['CD_AREA']==temp_dict['codigo'],'DESCRICAO'].values[-1],key='descricao_area_edit')
                    temp_dict['status']=col2.checkbox('Status',key='st_area_edit')

                    pass

                else:

                    temp_dict['codigo']=st.selectbox('Código',options=[],key='area_cd_edit')
                    col1,col2=st.columns(2)
                    temp_dict['area']=col1.text_input('Área',key='descricao_area_edit')
                    temp_dict['status']=col2.checkbox('Status',key='st_area_edit')

                    pass

                btn_edit=st.button('Editar',type='primary',key='btn_edit')

                if btn_edit==True:

                    retorno=self.ValidarCampos(temp_dict)

                    if retorno[0]!=None:

                        mensagem=st.warning(f'Preencher o campo {retorno[0]}')
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    else:

                        resp=self.Save_Area(temp_dict)

                        if resp==True:

                            mensagem=st.success('Dados salvo com sucesso')
                            time.sleep(1)
                            mensagem.empty()
                            streamlit_js_eval(js_expressions='parent.window.location.reload()')

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

    def Save_Area(self,dados_dict: dict):

        querys['CODIGO']="""
            
        SELECT COALESCE(MAX(CD_AREA),0)+1 FROM area

        """

        querys['VALIDE']="""

        SELECT COUNT(*) FROM area WHERE DESCRICAO='{0}'

        """.format(dados_dict['area'])

        codigo=sql.Code(querys['CODIGO'])
        valide=sql.Code(querys['VALIDE'])

        if valide<=0:

            tipo='INSERT'

            querys[tipo]="""

            INSERT INTO area(CD_AREA,DESCRICAO,STATUS) VALUES({0},'{1}',{2})

            """.format(codigo,dados_dict['area'],dados_dict['status'])

            pass


        else:

            tipo='UPDATE'

            querys[tipo]="""

            UPDATE area
            SET DESCRICAO='{1}',
            STATUS={2}
            WHERE CD_AREA={0}
            
            """.format(dados_dict['codigo'],dados_dict['area'],dados_dict['status'])

            pass

        sql.Save(querys[tipo])

        return True

        pass

    pass