import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from SQL import SQL
from glob import glob
import os
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import shutil
from Moeda import Moeda
import time
from Gmail import Mail
import socket as s

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

class Importador:

    def __init__(self,titulo) -> None:

        self.titulo=titulo

        pass    


    def main(self):

        sql.CreateTable(tabelas.values())

        path_base=os.path.join(os.getcwd(),'XML')
        os.makedirs(path_base,exist_ok=True)

        placeholder=st.empty()

        df=pd.DataFrame(columns=['Agenda','NFe','CNPJ','Fornecedor','Código','Produto','Qtde','Unid CMP','Valor Unitário','Total CMP','Path'])

        with placeholder.container():

            st.header(self.titulo)
            st.markdown('----')

            sidebar=st.sidebar
            btn_reset=sidebar.button('Resetar XML')

            files=st.file_uploader('Importar arquivo',type=['.xml'],accept_multiple_files=True)
            
            for file in files:

                tree=ET.parse(file)
                root=tree.getroot()

                nsNFE={'ns0':'http://www.portalfiscal.inf.br/nfe'}
       
                nota=root.find('ns0:NFe/ns0:infNFe/ns0:ide/ns0:nNF',nsNFE).text
                fornecedor=root.find('ns0:NFe/ns0:infNFe/ns0:emit/ns0:xNome',nsNFE).text
                cnpj_forn=root.find('ns0:NFe/ns0:infNFe/ns0:emit/ns0:CNPJ',nsNFE).text
                itens=root.findall('ns0:NFe/ns0:infNFe/ns0:det',nsNFE)

                arq=file.name
                temp_path=os.path.join(path_base,arq)
                
                for item in itens:

                    sku=item.find('ns0:prod/ns0:cProd',nsNFE).text
                    produto=item.find('ns0:prod/ns0:xProd',nsNFE).text
                    qtde=float(item.find('ns0:prod/ns0:qCom',nsNFE).text)
                    unid_cmp=item.find('ns0:prod/ns0:uCom',nsNFE).text
                    vl_unit=float(item.find('ns0:prod/ns0:vUnCom',nsNFE).text)
                    total_cmp=float(item.find('ns0:prod/ns0:vProd',nsNFE).text)

                    df.loc[len(df)]=['',nota,cnpj_forn,fornecedor,sku,produto,qtde,unid_cmp,vl_unit,total_cmp,temp_path]

                    pass

                tree.write(temp_path)

                #break

                pass

            df.drop_duplicates(inplace=True)

            if len(df)>0:

                dt_now=st.date_input('Data de Agendamento')
                notas=Moeda.Numero(len(df['NFe'].unique().tolist()))
                total=Moeda.FormatarMoeda(df['Total CMP'].sum())
                total=f'R$ {total}'
                col1,col2=st.columns(2)
                col1.text_input('Qtde NFe',value=notas,disabled=True)
                col2.text_input('Total NFe',value=total,disabled=True)
                df['Agenda']=dt_now
                st.dataframe(df)

                btn_enviar=st.button('Salvar',type='primary')

                if btn_enviar==True:

                    for i in df.index.tolist():

                        temp_dict=dict()

                        for c in df.columns:

                            temp_dict[c]=df.loc[i,c]

                            pass

                        querys={

                            'validar':

                            """

                            SELECT COUNT(*) FROM xml WHERE NOTA='{0}' AND CODIGO='{1}'

                            """.format(temp_dict['NFe'],temp_dict['Código']),

                            'insert':

                            """

                            INSERT INTO xml(NOTA,CNPJ,FORNECEDOR,CODIGO,PRODUTO,QTDE,UNID_CMP,VL_UNITARIO,TOTAL,DT_AGENDA,PATH)VALUES('{0}','{1}','{2}','{3}','{4}',{5},'{6}',{7},{8},'{9}','{10}')

                            """.format(temp_dict['NFe'],temp_dict['CNPJ'],temp_dict['Fornecedor'],temp_dict['Código'],temp_dict['Produto'],temp_dict['Qtde'],temp_dict['Unid CMP'],temp_dict['Valor Unitário'],temp_dict['Total CMP'],temp_dict['Agenda'],temp_dict['Path']),

                            'update':


                            """

                            UPDATE xml
                            SET DT_AGENDA='{1}',
                            PATH='{2}'
                            WHERE NOTA='{0}'
                            
                            """.format(temp_dict['NFe'],temp_dict['Agenda'],temp_dict['Path'])
                                
                        }                   

                        validar=sql.Code(querys['validar'])

                        if validar<=0:

                            tipo='insert'

                            pass

                        else:

                            tipo='update'

                            pass


                        sql.Save(querys[tipo])

                        pass

                    dt_now=datetime.strftime(datetime.now(),'%d/%m/%Y %H:%M:%S')
                    assunto=f'NETFEIRA - {dt_now}'

                    IP=s.gethostbyname(s.gethostname())

                    temp_path=os.path.join(os.getcwd(),IP,f'Consolidado.csv')
                    df=sql.GetDataframe('SELECT * FROM xml')
                    df.to_csv(temp_path,encoding='UTF-8',index=False)
                    
                    #bot.ti@demarchibrasil.com.br
                    temp_dict={'To':['bot.ti@demarchibrasil.com.br'],'CC':[''],'Anexo':[temp_path]}
                    mensagem=f'Dados do dia {dt_now}'
                    gmail.Enviar(assunto=assunto,mensagem=mensagem,info=temp_dict)
                    os.remove(temp_path)

                    mensagem=st.success('Dado salvo com sucesso.')
                    time.sleep(1)
                    mensagem.empty()

                    streamlit_js_eval(js_expressions='parent.window.location.reload()')

                    pass

                pass
            
            pass


        if btn_reset==True:

            shutil.rmtree(path_base)

            pass

        pass

    pass
