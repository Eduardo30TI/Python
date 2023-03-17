from openpyxl import load_workbook
import os
from glob import glob
from Acesso import Login
from Query import Query
from Email import Email
from RemoverArquivo import Remover

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'Fornecedores':

    """
    
    SELECT * FROM netfeira.vw_fornecedores
    WHERE [Nome Fantasia] LIKE '%NETFEIRA%' AND [Plano de Conta]='FORNECEDORES'
    
    """,

    'Produtos':

    """
    
    SELECT * FROM netfeira.vw_prod_dados
    
    """

}

def JOANIN(produtos:list):

    df=sql.CriarTabela(kwargs=querys)

    col_leach='joanin'

    path_base=os.path.join(os.getcwd(),'Planilhas','*.xlsx')

    df['Produtos']=df['Produtos'].loc[df['Produtos']['SKU'].isin(produtos)]

    for arq in glob(path_base):

        arq_name=os.path.basename(arq)

        if str(arq_name).lower().find(col_leach)<0:

            continue
        
        temp_path=arq

        pass

    sheet=load_workbook(temp_path)
    sheet.active

    sheet_names=sheet.sheetnames[-1]

    range=sheet[sheet_names]
    
    for i,c in enumerate(df['Produtos']['Produto'].tolist()):
        
        if i==0:

            name_sheet=str(c)
            range.title=name_sheet

            pass

        else:

            name_sheet=str(c)
            range=sheet.copy_worksheet(range)
            range.title=name_sheet
            
            pass

        temp_dict={'C5':'Razão Social','C6':'CNPJ Formatado','F6':'Inscrição Formatada','C7':'Endereço','C8':'Bairro','C9':'Município','C10':'Complemento','F7':'Número','F8':'CEP','F9':'UF'}
        
        #preencher dados do fornecedor
        sheet_names=sheet.sheetnames[-1]

        for key,value in temp_dict.items():
            
            range[key]=str(df['Fornecedores'][value].max())

            #break

            pass

        temp_dict={''}
        
        #preencher dados dos produtos
        for key,value in temp_dict.items():
            
            range[key]=str(df['Produtos'][value].max())

            #break

            pass        

        pass

    sheet.save('Teste.xlsx')

    pass


if __name__=='__main__':

    JOANIN([3,8,12])

    pass