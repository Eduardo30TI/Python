from ConectionSQL import SQL
import os
from glob import glob
import pandas as pd
from Email import Email

conecta=SQL('Netfeira','sqlserver','MOINHO','192.168.0.252')

conectando=conecta.ConexaoSQL()

email_geral={'Supervisor':['edson.junior@demarchibrasil.com.br'],'Gerente':['julio@demarchibrasil.com.br']}

querys={

'Falta':

"""

WITH TabTpCorte (cd_tp_faltaprd,descrica) AS (

SELECT cd_tp_faltaprd,descricao
FROM tp_faltaprd
WHERE ativo=1
--AND descricao LIKE '%CORTE%'
),

TabFalta (dt_falta,cd_vend,cd_clien,nu_ped,cd_prod,unid_vda,qtde_falta_vda,preco_unit,vl_total) AS (

SELECT CONVERT(DATETIME,CAST(dt_falta AS date),101) AS dt_falta,
cd_vend,cd_clien,nu_ped,cd_prod,unid_vda,qtde_falta,preco_unit,
ROUND(qtde_falta*preco_basico,2) AS vl_total
FROM faltaprd
INNER JOIN TabTpCorte ON faltaprd.cd_tp_faltaprd=TabTpCorte.cd_tp_faltaprd
)

SELECT dt_falta AS 'Data de Falta',
TabFalta.cd_vend AS 'ID Vendedor',
TabFalta.cd_clien AS 'ID Cliente',cliente.nome_res AS 'Nome Fantasia',
nu_ped AS 'Pedido',TabFalta.cd_prod AS 'SKU',produto.descricao AS 'Produto',
unid_vda AS 'Unid. VDA',qtde_falta_vda AS 'Qtde. VDA',
preco_unit AS 'Valor Unitário',vl_total AS 'Total do Pedido'
FROM TabFalta
--INNER JOIN vendedor ON TabFalta.cd_vend=vendedor.cd_vend
INNER JOIN cliente ON TabFalta.cd_clien=cliente.cd_clien
INNER JOIN produto ON TabFalta.cd_prod=produto.cd_prod
WHERE YEAR(dt_falta)=YEAR(GETDATE()) AND MONTH(dt_falta)=MONTH(GETDATE())
AND DAY(dt_falta)=DAY(GETDate())

""",

'Supervisor':

"""

WITH TabSupervisor (cd_emp,cd_equipe,descricao,cd_vend_sup,nome_resumido,email) AS (

SELECT equipe.cd_emp,equipe.cd_equipe,equipe.descricao,equipe.cd_vend_sup,
CASE WHEN CHARINDEX(' ',LTRIM(RTRIM(vendedor.nome)))=0 THEN vendedor.nome ELSE
RTRIM(LEFT(vendedor.nome,(CHARINDEX(' ',LTRIM(RTRIM(vendedor.nome)))))) + ' ' + 
LTRIM(RIGHT(vendedor.nome,(CHARINDEX(' ',REVERSE(LTRIM(RTRIM(vendedor.nome))))))) END AS nome_resumido,
usuario.e_mail
FROM equipe
INNER JOIN vendedor ON equipe.cd_vend_sup=vendedor.cd_vend AND equipe.cd_emp=vendedor.cd_emp
LEFT JOIN usuario ON vendedor.cd_vend=usuario.cd_usuario
),

TabGerencia (cd_emp,cd_vend_sup,nome_resumido,email) AS (

SELECT DISTINCT equipe.cd_emp,equipe.cd_vend_sup,TabSupervisor.nome_resumido,TabSupervisor.email
FROM equipe
INNER JOIN TabSupervisor ON equipe.cd_vend_sup=TabSupervisor.cd_vend_sup 
AND equipe.cd_emp=TabSupervisor.cd_emp
WHERE equipe.cd_equipe LIKE '%N%' AND ativo=1
),

TabEquipes (cd_equipe) AS (

SELECT DISTINCT cd_equipe
FROM ped_vda
INNER JOIN tp_ped ON ped_vda.tp_ped=tp_ped.tp_ped AND tp_ped.estat_com=1
INNER JOIN vendedor ON ped_vda.cd_vend=vendedor.cd_vend AND vendedor.ativo=1
)

SELECT * FROM (
SELECT TabSupervisor.cd_equipe AS 'ID Equipe',TabSupervisor.descricao AS 'Equipe',
TabSupervisor.nome_resumido AS 'Supervisor',
TabSupervisor.email AS 'E-mail Sup',
TabGerencia.nome_resumido AS 'Gerente',TabGerencia.email AS 'E-mail Gerg',
CASE WHEN TabSupervisor.nome_resumido=TabGerencia.nome_resumido 
THEN 'N' ELSE 'S' END AS 'Diferente'
FROM TabSupervisor
INNER JOIN TabGerencia ON TabSupervisor.cd_emp=TabGerencia.cd_emp
INNER JOIN TabEquipes ON TabSupervisor.cd_equipe=TabEquipes.cd_equipe
)equipes
ORDER BY 1

""",

'Vendedor':

"""

SELECT V.CD_VEND AS 'ID Vendedor',V.NOME AS 'Vendedor',
CASE WHEN 
CHARINDEX(' ',LTRIM(RTRIM(V.NOME)))=0 THEN V.NOME ELSE
LTRIM(RTRIM(LEFT(V.NOME,CHARINDEX(' ',LTRIM(RTRIM(V.NOME))))))+ ' '+
LTRIM(RTRIM(RIGHT(V.NOME,CHARINDEX(' ',REVERSE(LTRIM(RTRIM(V.NOME))))))) 
END AS 'Nome Resumido',V.CD_EQUIPE AS 'ID Equipe',
U.E_MAIL AS 'E-mail',categ.descricao AS 'Categoria'
FROM VENDEDOR AS V
LEFT JOIN USUARIO AS U ON V.CD_VEND=U.CD_USUARIO
LEFT JOIN categ ON V.CATEG=categ.categ
WHERE V.ATIVO=1

"""

}

def CorpoEmail(mix,total,usuario,texto):

    mensagem="""
        
        <p>{3}</p>

        <p>{0}</p>

        <p>Foram identificados cerca de {1} itens que foram cortados. Totalizando R$ {2:.2f}</p>

        <p>Por favor não responder mensagem automática</p>

        <p>Atenciosamente</p>

        <p>Robô Autonomo</p>        
        
    """.format(usuario.title(),mix,total,texto)

    return mensagem

    pass

def ConstruirBase():

    falta_df=pd.read_sql(querys['Falta'],conectando)

    supervisor_df=pd.read_sql(querys['Supervisor'],conectando)

    vendedor_df=pd.read_sql(querys['Vendedor'],conectando)

    temp_df=falta_df.merge(vendedor_df,on='ID Vendedor',how='inner')

    temp_df=temp_df.merge(supervisor_df,on='ID Equipe',how='inner')

    temp_df.drop(columns=['ID Equipe'],inplace=True)

    return temp_df

    pass

def AnaliseBase(dados):

    colunas=['Vendedor','Supervisor']
    
    vendedores=dados[['Vendedor','Equipe','E-mail','Supervisor','E-mail Sup','Gerente','E-mail Gerg']]
    
    for coluna in colunas:

        for linha in vendedores[coluna].unique().tolist():
            
            temp_df=dados.loc[dados[coluna]==linha]
            
            mix=len(temp_df['SKU'].unique().tolist())
            
            total=round(temp_df['Total do Pedido'].sum(),2)

            if(coluna=='Vendedor'):

                env_to=temp_df['E-mail'].str.lower().unique().tolist()

                env_cc=temp_df['E-mail Sup'].str.lower().unique().tolist()

                nome=temp_df['Nome Resumido'].unique().tolist()

                assunto='Corte de Produto' 

                pass

            else:

                env_to=temp_df['E-mail Sup'].str.lower().unique().tolist()

                env_cc=temp_df['E-mail Gerg'].str.lower().unique().tolist()

                nome=temp_df['Supervisor'].unique().tolist()  

                assunto='Corte de Produto - Geral'

                pass

            if(mix==0):

                continue

            temp_df=temp_df[['Data de Falta', 'ID Vendedor','Vendedor', 'Nome Resumido','Equipe', 'Supervisor', 'ID Cliente', 'Nome Fantasia', 'Pedido','SKU', 'Produto', 'Unid. VDA', 'Qtde. VDA', 'Valor Unitário','Total do Pedido']]

            produtos=temp_df[['SKU','Produto','Total do Pedido']].groupby(['SKU','Produto']).sum().reset_index()

            produtos.to_excel('Produtos Cortados.xlsx',index=False,encoding='ISO-8859-1')

            temp_df.to_excel(f'{nome[0]}.xlsx',index=False,encoding='ISO-8859-1')

            mensagem=CorpoEmail(texto='Bom dia',mix=mix,total=total,usuario=nome[0])

            temp_path=os.path.join(os.getcwd(),'*.xlsx')

            arquivo=[linha for linha in glob(temp_path) if linha]

            temp_dict={'To':env_to,'CC':env_cc,'Anexo':arquivo}
            
            Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

            RemoverArquivo(os.getcwd(),'.xlsx')
            
            pass

        pass

    pass

def BaseGeral(dados):
    
    colunas=['Vendedor','Supervisor']

    temp_df=dados
              
    mix=len(temp_df['SKU'].unique().tolist())
            
    total=round(temp_df['Total do Pedido'].sum(),2)

    env_to=[linha for linha in email_geral['Supervisor'] if linha]

    env_cc=[linha for linha in email_geral['Gerente'] if linha]

    nome=temp_df['Nome Resumido'].unique().tolist()

    assunto='Corte de Produto' 

    if(mix>0):

        produtos=temp_df[['SKU','Produto','Total do Pedido']].groupby(['SKU','Produto']).sum().reset_index()

        produtos.to_excel('Produtos Cortados.xlsx',index=False,encoding='ISO-8859-1')     

        temp_df.to_excel('Corte de Produto.xlsx',index=False,encoding='ISO-8859-1')

        mensagem=CorpoEmail(texto='Bom dia',mix=mix,total=total,usuario=nome[0])

        temp_path=os.path.join(os.getcwd(),'*.xlsx')

        arquivo=[linha for linha in glob(temp_path) if linha]

        temp_dict={'To':env_to,'CC':env_cc,'Anexo':arquivo}
            
        Email.EnviarEmail(corpo=mensagem,assunto=assunto,kwargs=temp_dict)

        RemoverArquivo(os.getcwd(),'.xlsx')
           
        pass

    pass

def RemoverArquivo(caminho,filtro):

    os.chdir(caminho)

    for arq in os.listdir():

        if(arq.find(filtro)<0):

            continue

        os.remove(arq)

        pass

    pass

if __name__=='__main__':

    os.system('cls')

    dados=ConstruirBase()

    AnaliseBase(dados)

    BaseGeral(dados)
    
    pass