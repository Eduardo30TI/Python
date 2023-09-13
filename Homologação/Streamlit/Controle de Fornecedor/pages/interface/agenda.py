import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import os
import shutil
from SQL import SQL
from datetime import datetime
from Moeda import Moeda
import time
from Gmail import Mail
import xml.etree.ElementTree as ET

gmail=Mail()

sql=SQL()

tabelas={

    'xml':

    """

    CREATE TABLE IF NOT EXISTS xml(
    
        NOTA TEXT NOT NULL,
        CNPJ VARCHAR(250) NOT NULL,
        FORNECEDOR TEXT NOT NULL,
        CODIGO VACHAR(250) NOT NULL,
        PRODUTO TEXT NOT NULL,
        QTDE DECIMAL(15,2) NOT NULL,
        UNID_CMP VARCHAR(250) NOT NULL,
        VL_UNITARIO DECIMAL(15,2) NOT NULL,
        TOTAL DECIMAL(15,2) NOT NULL,
        DT_AGENDA DATETIME NOT NULL,
        PATH TEXT NOT NULL

    )

    """

}

class Agendamento:

    def __init__(self,titulo):

        self.titulo=titulo

        pass

    def main(self):

        sql.CreateTable(tabelas.values())

        querys={

            'xml':

            """

            SELECT NOTA AS NFe,CNPJ,FORNECEDOR AS Fornecedor,CODIGO AS Código,PRODUTO AS Produto,Qtde AS [Qtde],UNID_CMP AS [Unid. CMP],VL_UNITARIO AS [Valor Unitário],TOTAL AS [Total CMP],
            strftime(DT_AGENDA) AS [Agenda],PATH AS Path
            FROM xml

            """
        }

        df=sql.GetDataframe(querys['xml'])

        placeholder=st.empty()

        with placeholder.container():

            st.header(self.titulo)
            sidebar=st.sidebar
            dt_now=sidebar.date_input('Data da Agenda')

            df=df.loc[df['Agenda']==datetime.strftime(dt_now,'%Y-%m-%d')]
            
            if len(df)<=0:

                val=st.selectbox('Notas',options=[])
                df=df.loc[df['NFe']==val]
                st.text_input('Fornecedor',key='fornecedor')
                col1,col2=st.columns(2)
                col1.text_input('Total NFe',disabled=True)
                col2.text_input('Qtde Produtos',disabled=True)

                st.dataframe(df[['Código','Produto','Qtde','Unid. CMP','Valor Unitário','Total CMP']],use_container_width=True)

                pass


            else:
            
                val=st.selectbox('Notas',options=df['NFe'].unique().tolist())
                df=df.loc[df['NFe']==val]
                st.text_input('Fornecedor',key='fornecedor',value=df['Fornecedor'].values[-1],disabled=True)
                total=Moeda.FormatarMoeda(df['Total CMP'].sum())
                mix=Moeda.Numero(len(df['Código'].unique().tolist()))
                col1,col2=st.columns(2)
                col1.text_input('Total NFe',value=f'R$ {total}',disabled=True)
                col2.text_input('Qtde Produtos',value=mix,disabled=True)

                st.dataframe(df[['Código','Produto','Qtde','Unid. CMP','Valor Unitário','Total CMP']],use_container_width=True)

                path_base=df.loc[df['NFe']==val,'Path'].values[-1]
                arq=os.path.basename(path_base)

                btn1,btn2=st.columns(2)
                btn=btn1.button('Receber',type='primary',use_container_width=True)

                tree=ET.parse(path_base)
                root=tree.getroot()

                data=ET.tostring(root)
                btn2.download_button('Download XML',data=data,file_name=arq,use_container_width=True)

                if btn==True:

                    if len(df)>0:

                        dt_now=datetime.strftime(datetime.now(),'%d/%m/%Y %H:%M:%S')
                        path_base=df.loc[df['NFe']==val,'Path'].values[-1]

                        assunto=f'Nota: {val} - {dt_now}'

                        temp_dict={'To':['compras@demarchibrasil.com.br'],'CC':[''],'Anexo':[path_base]}
                        
                        mensagem=f'nota: {val} recebida no dia {dt_now}'

                        gmail.Enviar(assunto=assunto,mensagem=mensagem,info=temp_dict)

                        querys=f"""

                        DELETE FROM xml WHERE NOTA='{val}'

                        """
                        
                        os.remove(path_base)
                        sql.Save(querys)
                        
                        mensagem=st.success('Nota recebida com sucesso.')
                        time.sleep(1)
                        mensagem.empty()
                        time.sleep(1)

                        streamlit_js_eval(js_expressions='parent.window.location.reload()')

                        pass

                    else:

                        mensagem=st.warning('Informe a nota fiscal')
                        time.sleep(1)
                        mensagem.empty()

                        pass

                    pass


                pass
                     
            pass

        pass


    pass