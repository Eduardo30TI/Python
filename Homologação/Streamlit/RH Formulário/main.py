import streamlit as st
import pandas as pd
import os
from CEP import CEP
from Gmail import Mail
from glob import glob
import os
from PIL import Image
import PyPDF2
from docx import Document
from datetime import datetime
import shutil
import time
from streamlit_js_eval import streamlit_js_eval

mail=Mail()

def Main():

    path_dict=dict()
    os.chdir(os.getcwd())
    
    val_dict=dict()
    
    sidebar=st.sidebar
    sidebar.image('https://demarchi.com.br/images/logo/logo-demarchi.png')
    sidebar.markdown('<hr/>',unsafe_allow_html=True)
    

    st.title('Documentação RH')
    st.markdown('<h4>Envio de documentação para admissão</h4>',unsafe_allow_html=True)
    st.markdown('<hr/>',unsafe_allow_html=True)

    tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(['Dados Pessoais','Endereço','Documentos','Dependentes','Anexo','Banco'])

    #tab1 - dados pessoais
    val_dict['func_empresa']=tab1.selectbox('Empresa',options=['NETFEIRA PONTOCOM LTDA'],key='empresa')
    val_dict['nome']=tab1.text_input('Nome do funcionário',placeholder='Digite seu nome completo',key='nome')
    col1,col2=tab1.columns(2)
    val_dict['grau']=col1.selectbox('Grau de Instrução',options=['1º grau incompleto','1º grau completo','2º grau incompleto','2º grau completo','Superior incompleto','Superior completo','Analfabeto'],key='grau')
    dt_nascimento=col2.date_input('Data de Nascimento',key='dtnasc')
    val_dict['dt_nascimento']=datetime.strftime(dt_nascimento,'%d/%m/%Y')

    val_dict['sexo']=tab1.radio('Sexo',options=['Feminino','Masculino'],horizontal=True)

    col3,col4=tab1.columns(2)
    val_dict['civil']=col3.selectbox('Estado Civil',options=['Solteiro','Casado','Separado','Divorciado','Viúvo'],key='civil')
    val_dict['cor']=col4.selectbox('Raça/Cor',options=['Branca','Preta','Parda','Amarela','Indígina'],key='raca')

    val_dict['mae']=tab1.text_input('Nome da Mãe',key='mae',placeholder='Digite o nome completo')
    val_dict['pai']=tab1.text_input('Nome do Pai',key='pai',placeholder='Digite o nome completo')

    #tab2 - endereço
    col1,col2=tab2.columns(2)
    cep=col1.text_input('CEP',placeholder='Digite o CEP',key='cep')
    val_dict['cep']=cep
       
    temp_dict=CEP.GetCEP(cep)

    val_dict['endereco']=tab2.text_input('Endereço',value=temp_dict['logradouro'],key='logradouro')
    val_dict['bairro']=col2.text_input('Bairro',value=temp_dict['bairro'],key='bairro')

    col3,col4,col5=tab2.columns(3)
    val_dict['cidade']=col3.text_input('Cidade',value=temp_dict['cidade'],key='cidade')
    val_dict['uf']=col4.text_input('UF',value=temp_dict['uf'])
    val_dict['numero']=col5.text_input('Número')

    #tab3- documentos

    col1,col2=tab3.columns(2)
    cpf=col1.text_input('CPF',key='cpf')
    val_dict['cpf']=cpf
    col3,col4=tab3.columns(2)
    val_dict['pis']=col3.text_input('PIS',key='pis')
    #dt_pis=col4.date_input('Data')
    #val_dict['datas']=datetime.strftime(dt_pis,'%d/%m/%Y')

    col5,col6,col7=tab3.columns(3)
    val_dict['titulo']=col5.text_input('Título de Eleitor',key='titulo')
    val_dict['zona']=col6.text_input('Zona',key='zona')
    val_dict['secao']=col7.text_input('Seção',key='secao')

    col8,col9,col10,col11=tab3.columns(4)
    val_dict['registro']=col8.text_input('RG',key='rg')
    val_dict['doc_emt']=col9.text_input('Órgão Emissor',key='orgao')
    val_dict['unidadef']=col10.text_input('UF',key='uf_rg')
    dt_exped=col11.date_input('Data de Expedição',key='dt_exped')
    val_dict['dt_exped']=datetime.strftime(dt_exped,'%d/%m/%Y')

    #tab4 - dependentes

    nome_dep=tab4.text_input('Nome do Dependente',key='dependente',placeholder='Digite o nome completo')
    col1,col2=tab4.columns(2)
    dt_dep=col1.date_input('Data de Nascimento',key='dt_dep')
    cpf_dep=col2.text_input('CPF',key='cpf_dep')
    btn=tab4.button('Adicionar')

    tabela=tab4.empty()
    df=pd.DataFrame(columns=['CPF','Dependente','Data de Nascimento'])

    temp_path=os.path.join(os.getcwd(),cpf)
    os.makedirs(temp_path,exist_ok=True)
    temp_path=os.path.join(temp_path,'Dependente.xlsx')

    arq=glob(temp_path)

    if len(arq)>0:

        df=pd.read_excel(temp_path)
        
        tabela.table(df)

        pass

    if btn==True:

        if nome_dep=='' or dt_dep=='' or cpf_dep=='':
            
            tab4.error('Por favor preencher os campos')

            pass

        else:

            df.loc[len(df)]=[cpf_dep,nome_dep,dt_dep.strftime('%d/%m/%Y')]
            df.to_excel(temp_path,index=False)

            tabela.table(df)

            path_dict[cpf]=temp_path

            pass

        pass

    #tab5 - anexo

    tab5.markdown('<h4>Não inserir arquivos que não sejam da extensão informada na importação.</h4>',unsafe_allow_html=True)

    imagens=tab5.file_uploader('Documentos',accept_multiple_files=True,key='upload',type=['.png','.jpg','.jpeg'])
    path_base=os.getcwd()

    temp_path=os.path.join(os.getcwd(),cpf)

    os.chdir(temp_path)

    #converter imagem em pdf
    for imagem in imagens:

        with open(imagem.name,'wb') as file:

            file.write(imagem.getbuffer())
            
            pass

        with Image.open(imagem.name) as file:

            arq_name=str(imagem.name).split('.')[0]

            img_convert=file.convert('RGB')
            img_convert.save(f'{arq_name}.pdf')
            
            pass

        os.remove(imagem.name)

        pass
        
    arquivos=glob('*.pdf')

    merger=PyPDF2.PdfMerger()

    if len(imagens)>0:

        try:
                        
            for arq in arquivos:
                
                with open(arq,'rb') as file:

                    info=PyPDF2.PdfReader(file)
                    merger.append(info)

                    pass

                os.remove(arq)

                pass

            merger.write('Documentos.pdf')

            pass

        except Exception:

            pass

        pass

    os.chdir(path_base)

    #tab6 - banco

    col1,col2=tab6.columns(2)
    val_dict['banco']=col1.selectbox('Banco',options=['Itaú Unibanco','Bradesco','Banco do Brasil','Caixa Econômica Federal','Santander'],key='banco')
    val_dict['tpconta']=col2.selectbox('Tipo de Conta',options=['Conta Corrente','Conta Poupança'],key='tpconta')
    col3,col4=tab6.columns(2)
    val_dict['agencia']=col3.text_input('Agência',key='agencia')
    val_dict['conta']=col4.text_input('Conta',key='conta',placeholder='Digitar a conta com o digito')

    #preencher o arquivo
    btn_send=sidebar.button('Enviar')
    
    if btn_send==True:

        loop=True

        for c in val_dict.keys():

            if val_dict[c]!='' or c=='pai':

                continue

            else:

                sidebar.warning(f'Por favor preencher o campo {c}')
                loop=False

                break

            pass

        if loop==True:

            st.warning('Carregando aguarde...')

            temp_path=os.path.join(os.getcwd(),cpf,f'{cpf}-{val_dict["nome"]}.docx')
            
            doc=Document('Base.docx')

            for pag in doc.paragraphs:

                for codigo in val_dict:

                    valor=val_dict[codigo]

                    pag.text=pag.text.replace(codigo,valor)

                    pass

                pass

            doc.save(temp_path)

            msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

            assunto=f'Documentos {val_dict["nome"]}'

            mensagem=f"""
            
            <p>{msg};</p>

            <p>RH</p>

            <p>Segue o e-mail com os documentos para admissão do novo funcionário: <b>{str(val_dict["nome"]).title()}<b></p>

            <P>Por favor não responder mensagem automática</P>

            <p>Atenciosamente</p>

            <p>BOT TI</p>
            
            """

            temp_path=os.path.join(os.getcwd(),cpf,'*.*')
            arquivos=glob(temp_path)

            temp_dict={'To':['documentos.rh@demarchisaopaulo.com.br'],'CC':[],'Anexo':arquivos}

            mail.Enviar(assunto=assunto,mensagem=mensagem,info=temp_dict)

            sidebar.success('E-mail enviado com sucesso')

            temp_path=os.path.join(os.getcwd(),cpf)
            shutil.rmtree(temp_path)
            time.sleep(2)
            streamlit_js_eval(js_expressions='parent.window.location.reload()')

            pass

        pass

    pass


if __name__=='__main__':

    Main()


    pass
