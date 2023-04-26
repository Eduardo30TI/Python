from Acesso import Login
from Moeda import Moeda
from Query import Query
from RemoverArquivo import Remover
from WebTransfer import Web
import telebot
from telebot import types
from datetime import datetime
from pathlib import Path
import shutil
import os
import pandas as pd
from decouple import config
from glob import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
import pyttsx3
from PIL import Image

#TOKEN_PROD - produção
#TOKEN - homologação
TOKEN=config('TOKEN_PROD')

bot=telebot.TeleBot(TOKEN,parse_mode='html')

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

path_dict=dict()

variaveis_dict=dict()

comando=None

commands_dict={

    '/comandos':'Atualizar comandos na barra de menu',
    '/foto':'Foto dos produtos',
    '/fichatecnica': 'Ficha técnica dos produtos',
    '/dadosprodutos': 'Dados dos produtos',
    '/carteira':'Carteira de cliente',
    '/vendas':'Resultado da empresa',
    '/realizado':'Resultado do dia atual',
    '/atendimento':'Atendimento X Carteira',
    '/estatistica':'Posição estatística comercial',
    '/meta': 'Meta mensais',
    '/tabelas':'Tabelas do sistema',
    '/custo':'Consultar o custo do produto',
    '/alerta':'Alerta de estoque',
    '/estoque':'Consultar estoque',
    '/vendagrupo':'Vendas por grupo',
    '/vendafabricante':'Vendas por fabricante',
    '/mixsegmento':'Sugestão de mix',
    '/devolucao':'Devolução de mercadoria',
    '/corte':'Corte de produto'       

}

start={

    '/comandos':'CommandsMenu',
    '/foto':'ValidacaoProduto',
    '/fichatecnica': 'ValidacaoProduto',
    '/dadosprodutos': 'ValidacaoProduto',
    '/carteira':'Carteira',
    '/vendas':'Opcao',
    '/realizado':'Realizado',
    '/atendimento':'Opcao',
    '/estatistica':'Opcao',
    '/meta':'Opcao',
    '/tabelas':'Opcao',
    '/custo':'ValidacaoProduto',
    '/alerta':'Alerta',
    '/estoque':'ValidacaoProduto',
    '/vendagrupo':'Opcao',
    '/vendafabricante':'Opcao',
    '/mixsegmento':'Opcao',
    '/devolucao':'Opcao',
    '/corte':'Opcao'       

}

funcoes={

    '/comandos':'CommandsMenu',
    '/foto':'Foto',
    '/fichatecnica': 'FichaTecnica',
    '/dadosprodutos': 'DadosProdutos',
    '/carteira':'Carteira',
    '/vendas':'Opcao',
    '/realizado':'Realizado',
    '/atendimento':'Opcao',
    '/estatistica':'Opcao',
    '/meta':'Opcao',
    '/tabelas':'Opcao',
    '/custo':'Custo',
    '/alerta':'Alerta',
    '/estoque':'Estoque',
    '/vendagrupo':'Opcao',
    '/vendafabricante':'Opcao',
    '/mixsegmento':'Opcao',
    '/devolucao':'Opcao',
    '/corte':'Opcao'    

}

#função usando para opções
col_dict={

    '/fabricante':['Produtos','Vendedor'],
    '/vendas':['Mensal','Vendedor'],
    '/atendimento':['Mensal','Vendedor'],
    '/estatistica':['Mensal','Vendedor'],
    '/meta':['Mensal','Vendedor'],
    '/tabelas':['Tabelas','Vendedor'],
    '/alerta':['Estoque','Vendedor'],
    '/vendagrupo':['Mensal','Vendedor'],
    '/vendafabricante':['Mensal','Vendedor'],
    '/mixsegmento':['MIXSegmento','Vendedor'],
    '/devolucao':['Mensal','Vendedor'],
    '/corte':['Mensal','Vendedor','Corte']
}

tab_dict={

    '/vendas':'Mensal',
    '/atendimento':'Mensal',
    '/estatistica': 'Mensal',
    '/meta': 'Mensal',
    '/tabelas':'Tabelas',
    '/alerta':'Estoque',
    '/vendagrupo':'Mensal',
    '/vendafabricante':'Mensal',
    '/mixsegmento':'MIXSegmento',
    '/devolucao':'Mensal',
    '/corte':'Mensal'

}

col_name={

    '/fabricante':'Fabricante',
    '/vendas':'Mês',
    '/atendimento':'Mês',
    '/estatistica': 'Mês',
    '/meta': 'Mês',
    '/tabelas':'Tabela',
    '/alerta':'Alerta',
    '/vendagrupo':'Mês',
    '/vendafabricante':'Mês',
    '/mixsegmento':'Canal',
    '/devolucao':'Mês',
    '/corte':'Mês'

}

callback_dict={

    '/vendas':2,
    '/atendimento':3,
    '/estatistica': 4,
    '/meta':5,
    '/tabelas':6,
    '/alerta':7,
    '/vendagrupo':8,
    '/vendafabricante':9,
    '/mixsegmento':10,
    '/devolucao':11,
    '/corte':12    

}

espera=3600

querys={

    'Produtos':

    """
        
    SELECT * FROM netfeira.vw_prod_dados
        
    """,

    'Fotos':


    """
    
    SELECT * FROM netfeira.vw_produto
    WHERE Fotos IS NOT NULL AND Fotos<>''
    
    """,

    'Vendedor':

    """
    
    SELECT LTRIM(RTRIM(vend.[ID Vendedor])) AS [ID Vendedor],vend.[Nome Resumido],
	sup.Equipe,vend.[Status do Vendedor],
    LTRIM(RTRIM(sup.[ID Sup])) AS [ID Sup],sup.Supervisor,[ID Gerente],Gerente
    FROM netfeira.vw_vendedor vend
    INNER JOIN netfeira.vw_supervisor sup ON vend.[ID Equipe]=sup.[ID Equipe]
    
    """,

    'Carteira':

    """

    SELECT cad.[ID Cliente],cad.CNPJ,cad.[Razão Social],cad.[Nome Fantasia],cad.Matriz,seg.Segmento,seg.Canal,
    cad.CEP,cad.Endereço,cad.Bairro,cad.Cidade,cad.UF,cad.Numero,cad.Complemento,cad.[Condição de Pagto],cad.Prazo,
    cad.Tabela,cad.DDD,cad.Contato,cad.[Última Compra],cad.Dias,
    cad.[ID Vendedor],cad.[Nome Resumido],cad.Equipe,cad.Supervisor,cad.Principal
    FROM netfeira.vw_carteira cad
    INNER JOIN netfeira.vw_segmento seg ON cad.[ID Segmento]=seg.[ID Segmento]
    
    """,

    'Mensal':

    """

    SELECT c.[ID Mês],c.Mês,c.[ID Vendedor],
    COALESCE(c.FATURADO,0) AS FATURADO,COALESCE(c.[DEVOLUÇÃO PARCIAL],0) AS [DEVOLUÇÃO PARCIAL],
    COALESCE(c.DEVOLUÇÃO,0) AS DEVOLUÇÃO,COALESCE(c.CANCELADO,0) AS CANCELADO,
    COALESCE(c.FATURADO,0)+COALESCE(c.[DEVOLUÇÃO PARCIAL],0)+COALESCE(c.DEVOLUÇÃO,0)+COALESCE(c.CANCELADO,0) AS [Total Líquido]
    FROM (

        SELECT *
        FROM (
            SELECT ca.[ID Mês],ca.Mês,
            LTRIM(RTRIM(v.[ID Vendedor])) AS [ID Vendedor]
            ,v.Situação,
            SUM(v.[Total Venda]) AS [Total Venda]
            FROM netfeira.vw_venda_estatico v
            INNER JOIN netfeira.vw_calend ca ON v.[Data de Faturamento]=ca.Data
            WHERE [Tipo de Operação]='VENDAS' AND YEAR(v.[Data de Faturamento])=YEAR(GETDATE())
            GROUP BY ca.[ID Mês],ca.Mês,v.[ID Vendedor],v.Situação

        )a
        PIVOT(SUM([Total Venda]) FOR Situação IN([FATURADO],[DEVOLUÇÃO],[DEVOLUÇÃO PARCIAL],[CANCELADO]))b

    )c
    ORDER BY c.[ID Mês]
    
    """,

    'Realizado':

    """
    
    SELECT *
    FROM netfeira.vw_estatistico
    WHERE [Data de Emissão]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101) AND [Tipo de Operação]='VENDAS'
    
    """,

    'Meta':
    
    """
    
    SELECT m.[Mês Meta],c.Ano,c.Mês,m.[ID Vendedor],vend.[Nome Resumido],sup.Equipe,sup.Supervisor,
	m.[Meta R$]
	FROM netfeira.vw_metavend m
	INNER JOIN netfeira.vw_calend c ON m.[Mês Meta]=c.[Mês Meta]
	INNER JOIN netfeira.vw_vendedor vend ON m.[ID Vendedor]=vend.[ID Vendedor]
	INNER JOIN netfeira.vw_supervisor sup ON vend.[ID Equipe]=sup.[ID Equipe]
	WHERE c.Ano=YEAR(GETDATE())
	GROUP BY m.[Mês Meta],c.Ano,c.Mês,m.[ID Vendedor],vend.[Nome Resumido],sup.Equipe,sup.Supervisor,
	m.[Meta R$]
    
    """,

    'Tabelas':


    """
    
    SELECT * FROM netfeira.vw_tab_vend
    
    """,

    'Estatistica':

    """

    SELECT * FROM netfeira.vw_estatistico
    WHERE YEAR([Data de Faturamento])=YEAR(GETDATE()) AND [Tipo de Operação]<>'OUTROS' AND [ID Situação] IN('FA','AB')
    
    """,

    'Calendario':

    """
    
    SELECT * FROM netfeira.vw_calend
    
    """,

    'Estatico':

    """
    
    SELECT * FROM netfeira.vw_venda_estatico
    WHERE YEAR([Data de Faturamento])=YEAR(GETDATE()) AND [Tipo de Operação]<>'OUTROS'
    
    """,

    'Uteis':

    """
    
    SELECT c.Ano,c.[ID Mês],c.Mês,COUNT(c.[Data]) AS [Dias Úteis],
    CASE WHEN [ID Mês]=MONTH(GETDATE()) THEN COUNT(c.[Data Trabalhada])-1 ELSE COUNT(c.[Data Trabalhada]) END AS [Trabalhado],
    COUNT(c.[Data])-
    CASE WHEN [ID Mês]=MONTH(GETDATE()) THEN COUNT(c.[Data Trabalhada])-1 ELSE COUNT(c.[Data Trabalhada]) END AS [Dias Restante]
    FROM netfeira.vw_calend c
    WHERE c.[Dia Útil]=1
    GROUP BY c.Ano,c.[ID Mês],c.Mês
    HAVING Ano=YEAR(GETDATE())
    ORDER BY [ID Mês]
    
    """,

    'Custo':

    """
    
    SELECT * FROM netfeira.vw_custo
    WHERE [Tipo de Custo]='ULTIMA ENTRADA'
    
    """,

    'Estoque':

    """
    
    SELECT * FROM netfeira.vw_stk_analise
    
    """,

    'MIXSegmento':

    """
        
    SELECT e.[ID Cliente],e.SKU,p.Produto,p.Fabricante,p.Seção,p.Categoria,p.Linha,s.Segmento,s.Canal,
    SUM(e.[Total Venda]) AS [Total Venda]
    FROM netfeira.vw_targetestatistico e
    INNER JOIN netfeira.vw_produto p ON e.SKU=p.SKU AND p.Status='ATIVO'
    INNER JOIN netfeira.vw_cliente c ON e.[ID Cliente]=c.[ID Cliente] AND c.[Status do Cliente]='ATIVO'
    INNER JOIN netfeira.vw_segmento s ON c.[ID Segmento]=s.[ID Segmento]
    WHERE [Data de Faturamento] BETWEEN DATEADD(DAY,-90,DATEADD(DAY,-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)))
    AND DATEADD(DAY,-1,CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)) AND [Tipo de Operação]='VENDAS' AND [ID Situação] IN('FA','AB')
    GROUP BY e.[ID Cliente],e.SKU,p.Produto,p.Fabricante,p.Seção,p.Categoria,p.Linha,s.Segmento,s.Canal
        
    """,

    'Corte':

    """
    
    SELECT f.[Data de Falta],f.[Data e Hora],f.[ID Vendedor],v.Vendedor,s.Equipe,s.Supervisor, f.[ID Cliente],f.[Nome Fantasia],f.Matriz,
    f.Segmento,f.Canal,f.Pedido,f.SKU,f.Produto,f.Fabricante,f.Linha,f.[Unid. VDA],f.[Qtde. VDA],f.[Valor Unitário],f.[Total do Pedido]
    FROM netfeira.vw_falta f
    INNER JOIN netfeira.vw_vendedor v ON f.[ID Vendedor]=v.[ID Vendedor]
    INNER JOIN netfeira.vw_supervisor s ON v.[ID Equipe]=s.[ID Equipe]
    WHERE YEAR([Data de Falta])=YEAR(GETDATE())
    
    """,

    'Devolucao':


    """
    
    SELECT d.[Data de Entrada],d.Motivo,d.[Situação do Pedido],d.[Tipo de Pedido],d.[Tipo de Operação],d.Tabelas,
    d.Pedido,d.NFe,
    d.[ID Cliente],cli.[Nome Fantasia],COALESCE(cli.Matriz,'AVULSO') AS Matriz,seg.Segmento,seg.Canal,
    d.[ID Vendedor],vend.[Nome Resumido],sup.Equipe,sup.Supervisor,
    d.SKU,prod.Produto,prod.Fabricante,prod.Linha,
    d.[Total Geral]
    FROM netfeira.vw_devolucao d
    INNER JOIN netfeira.vw_cliente cli ON d.[ID Cliente]=cli.[ID Cliente]
    INNER JOIN netfeira.vw_segmento seg ON cli.[ID Segmento]=seg.[ID Segmento]
    INNER JOIN netfeira.vw_vendedor vend ON d.[ID Vendedor]=vend.[ID Vendedor]
    INNER JOIN netfeira.vw_supervisor sup ON vend.[ID Equipe]=sup.[ID Equipe]
    INNER JOIN netfeira.vw_produto prod ON d.SKU=prod.SKU
    WHERE YEAR([Data de Entrada])=YEAR(GETDATE()) AND [Situação do Pedido]<>'CANCELADO'
        
    """

}

@bot.message_handler(commands=['start','foto','fichatecnica','dadosprodutos','carteira','vendas','realizado','atendimento','estatistica','meta','tabelas','custo','alerta','estoque','vendagrupo','vendafabricante','mixsegmento','devolucao','corte'])
def Main(message):

    CommandsMenu()

    global comando

    comando=message.text
        
    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    chat_id=message.from_user.id

    bot.delete_message(chat_id=chat_id,message_id=message.message_id)
    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    temp_path=Path(__file__)
    temp_path=temp_path.parent.joinpath('Memória')

    Path(temp_path).mkdir(exist_ok=True)
        
    path_arq=os.path.join(temp_path.joinpath('Consolidado.xlsx'))

    arquivo=glob(path_arq)

    if len(arquivo)<=0:

        temp_df=pd.DataFrame(columns=['ChatID','Código'])

        temp_df.to_excel(path_arq,index=False,sheet_name='Chat')

        pass

    temp_df=pd.read_excel(path_arq,sheet_name='Chat')

    count=len(temp_df.loc[temp_df['ChatID']==chat_id])

    if count<=0:
        
        bot.send_message(chat_id=chat_id,text=f'{msg} por questões de segurança me informe seu código de vendedor interno para que possamos continuar.')

        bot.register_next_step_handler(message=message,callback=ValidacaoID)        

        pass

    else:

        if message.text=='/start':

            pass

        else:

            func=start[str(message.text)]
                            
            globals().get(func)(message)

            pass

        pass

    pass

@bot.message_handler(commands=['comandos'])
def GetComand(message):

    chat_id=message.from_user.id

    bot.delete_message(chat_id=chat_id,message_id=message.message_id)
    bot.send_chat_action(chat_id=chat_id,action='typing')
    CommandsMenu()
    bot.send_message(chat_id=chat_id,text='Comandos atualizados com sucesso!')

    pass

@bot.callback_query_handler(func=lambda call:True)
def call_handler(message):
        
    path=Path(__file__).parent.joinpath('Extrato')

    path.mkdir(exist_ok=True)

    global path_dict

    global variaveis_dict

    chat_id=message.from_user.id
    
    conteudo=str(message.data)

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    id=int(conteudo[:conteudo.find('/')])

    val=str(conteudo[conteudo.find('/')+1:])

    bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)
    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    match id:

        #lista de vendedores extração da carteira do vendedor
        case 1:
            
            df=sql.GetDados(querys=querys,colunas=['Vendedor','Carteira'])

            col_leach={'Equipe':'ID Vendedor','ID Sup':'ID Equipe'}

            for c,d in col_leach.items():

                try:

                    lista=df['Vendedor'].loc[(df['Vendedor'][c]==val)&(df['Vendedor']['Status do Vendedor']=='ATIVO'),d].unique().tolist()

                    if len(lista)>0:

                        break

                    pass

                except:

                    continue

                pass

            if len(lista)>1:

                markup=InlineKeyboardMarkup(lista,call_back=id)

                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                #bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)

                bot.send_message(chat_id=chat_id,text='Escolha uma das opções abaixo:',reply_markup=markup)

                pass

            else:
                
                temp_df=Memoria(chat_id=chat_id)

                codigo=temp_df['Código'].tolist()[-1]

                nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

                id=df['Vendedor'].loc[df['Vendedor']['Nome Resumido']==val,'ID Vendedor'].tolist()[-1]

                vendedor=val.title()

                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                #bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)
                
                for c in ['Carteira']:

                    df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)

                    pass
                
                df['Carteira']=df['Carteira'].loc[df['Carteira']['ID Vendedor']==id]

                if len(df['Carteira'])>0:

                    df['Carteira'].to_excel('Carteira.xlsx',index=False)

                    with open('Carteira.xlsx','rb') as file:

                        bot.send_document(chat_id=chat_id,document=file,caption=f'{msg} {nome}, segue a relação da carteira do vendedor: <strong>{vendedor}</strong>')

                        pass

                else:

                    bot.send_message(chat_id=chat_id,text=f'{nome} não consegui encontrar nenhuma informação do vendedor: {val}')

                    pass

                Remover.RemoverArquivo('.xlsx')

                pass

            pass
        
        #extrair a relação do que foi vendido por equipe.
        case 2:

            temp_dict=Colunas()

            df=sql.GetDados(querys,['Mensal','Vendedor'])

            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            for c in ['Mensal','Vendedor']:

                df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)
                    
                pass            

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].unique().tolist()[-1]).title()

            codigos=df['Vendedor'].loc[df['Vendedor'][temp_dict[codigo]]==codigo,'ID Vendedor'].unique().tolist()
            
            df['Mensal']=df['Mensal'].loc[(df['Mensal']['ID Vendedor'].isin(codigos))&(df['Mensal']['Mês']==val)]

            df['Mensal']=df['Mensal'].merge(df['Vendedor'],on='ID Vendedor',how='inner')[['ID Mês', 'Mês','ID Vendedor', 'Nome Resumido', 'Equipe', 'ID Sup', 'Supervisor',
                'ID Gerente', 'Gerente','FATURADO', 'DEVOLUÇÃO PARCIAL','DEVOLUÇÃO', 'CANCELADO', 'Total Líquido']]
            
            vl_fat=Moeda.FormatarMoeda(df['Mensal']['FATURADO'].sum())

            vl_dev=Moeda.FormatarMoeda(df['Mensal']['DEVOLUÇÃO'].sum()+df['Mensal']['DEVOLUÇÃO PARCIAL'].sum())

            vl_can=Moeda.FormatarMoeda(df['Mensal']['CANCELADO'].sum())

            vl_liq=Moeda.FormatarMoeda(df['Mensal']['Total Líquido'].sum())
                        
            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                                    
            mensagem=f'{msg} {nome}, segue o arquivo com as informações do resultado. Abaixo tem um resumo das informações:\n\nFaturado: R${vl_fat}\nDevolução: R$ {vl_dev}\nCanelado: R$: {vl_can}\nTotal Líquido: R$ {vl_liq}.\n\nObs. Se quiser o relatório clique nesse link: /extrato'

            name_arq=f'Resultado {nome}.xlsx'

            temp_path=os.path.join(os.getcwd(),path.name,name_arq)

            df['Mensal'].to_excel(temp_path,index=False)
            
            arquivo=glob(temp_path)

            path_dict[chat_id]=arquivo

            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
            bot.send_message(chat_id=chat_id,text=mensagem)

            pass
        
        #analise de positivação
        case 3:

            temp_dict=Colunas()
            
            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            col=temp_dict[codigo]

            df=sql.GetDados(querys=querys,colunas=['Estatistica','Vendedor','Calendario','Carteira'])

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            codigos=df['Vendedor'].loc[df['Vendedor'][col]==codigo,'ID Vendedor'].tolist()

            for c in ['Estatistica','Carteira']:

                df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)

                pass

            df['Estatistica']=df['Estatistica'].merge(df['Calendario'],left_on='Data de Faturamento',right_on='Data',how='inner')

            df['Estatistica']=df['Estatistica'].loc[(df['Estatistica']['Mês']==val)&(df['Estatistica']['ID Vendedor'].isin(codigos))&(df['Estatistica']['Tipo de Operação']=='VENDAS')]

            df['Estatistica']=df['Estatistica'].groupby(['ID Cliente','ID Vendedor','Mês'],as_index=False).agg({'Total Venda':'sum'})

            df['Carteira']=df['Carteira'].loc[(df['Carteira']['ID Vendedor'].isin(codigos))]

            df['Carteira']=df['Carteira'].merge(df['Estatistica'],on=['ID Cliente','ID Vendedor'],how='left')
                        
            if col=='ID Gerente':

                df['Carteira']=df['Carteira'].loc[df['Carteira']['Principal']=='SIM']

                pass

            qtd_atend=len(df['Carteira'].loc[df['Carteira']['Total Venda'].notnull(),'ID Cliente'].unique().tolist())

            qtd_null=len(df['Carteira'].loc[df['Carteira']['Total Venda'].isnull(),'ID Cliente'].unique().tolist())

            qtd_cad=len(df['Carteira']['ID Cliente'].unique().tolist())

            perc=round(qtd_atend/qtd_cad,4)*100 if qtd_null>0 else 0

            mensagem=f'{msg} {nome} você atendeu {Moeda.Numero(qtd_atend)} cliente(s) de uma carteira contendo {Moeda.Numero(qtd_cad)} isso representa {Moeda.FormatarMoeda(perc)}%. Além disso ficou de fora dessa relação {Moeda.Numero(qtd_null)} que não foram positivados no mês de {val.title()}.\n\nObs. Se quiser o relatório clique nesse link: /extrato' if qtd_null>0 else f'{msg} {nome} parabéns você conseguiu atender toda sua carteira.'
                        
            bot.send_chat_action(chat_id=chat_id,action='typing')

            if qtd_null>0:

                df['Carteira']=df['Carteira'].loc[df['Carteira']['Total Venda'].isnull()]

                name_arq=f'Positivação {nome}.xlsx'

                temp_path=os.path.join(os.getcwd(),path.name,name_arq)     

                df['Carteira'].to_excel(temp_path,index=False)

                arquivo=glob(temp_path)

                path_dict[chat_id]=arquivo            

                bot.send_message(chat_id=chat_id,text=mensagem)

                pass

            else:

                bot.send_message(chat_id=chat_id,text=mensagem)

                pass

            pass
        
        #posição estatística comercial
        case 4:
            
            temp_dict=Colunas()
            
            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            col=temp_dict[codigo]

            df=sql.GetDados(querys=querys,colunas=['Estatistica','Vendedor','Calendario','Carteira'])

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            codigos=df['Vendedor'].loc[df['Vendedor'][col]==codigo,'ID Vendedor'].tolist()

            for c in ['Estatistica','Carteira']:

                df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)

                pass

            df['Estatistica']=df['Estatistica'].merge(df['Calendario'],left_on='Data de Faturamento',right_on='Data',how='inner')

            df['Estatistica']=df['Estatistica'].loc[(df['Estatistica']['Mês']==val)&(df['Estatistica']['ID Vendedor'].isin(codigos))&(df['Estatistica']['Tipo de Operação']=='VENDAS')]

            vl_real=Moeda.FormatarMoeda(df['Estatistica']['Total Venda'].sum())

            qtd_cli=Moeda.Numero(len(df['Estatistica']['ID Cliente'].unique().tolist()))

            mix=Moeda.Numero(len(df['Estatistica']['SKU'].unique().tolist()))

            pedido=Moeda.Numero(len(df['Estatistica']['Pedido'].unique().tolist()))
            
            peso=Moeda.FormatarMoeda(df['Estatistica']['Peso Bruto KG'].sum())

            mensagem=f'{msg} {nome} segue o realizado no mês de {val.title()}, na posição estatística comercial conforme abaixo:\n\n<strong>Realizado: R$ {vl_real} </strong>\n<strong>Pedidos: {pedido}</strong>\n<strong>Atendimento: {qtd_cli}</strong>\n<strong>MIX: {mix}</strong>\n<strong>Peso: {peso}</strong>'

            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
            bot.send_message(chat_id=chat_id,text=mensagem)

            pass

        #meta mensal
        case 5:

            try:

                temp_dict=Colunas()
                
                temp_df=Memoria(chat_id=chat_id)

                codigo=temp_df['Código'].tolist()[-1]

                col=temp_dict[codigo]

                df=sql.GetDados(querys=querys,colunas=['Estatistica','Calendario','Vendedor','Meta','Uteis','Estatico'])

                for c in ['Estatistica','Estatico']:

                    df[c]=df[c].merge(df['Calendario'],left_on='Data de Faturamento',right_on='Data',how='inner')

                    pass
                
                df['Estatistica']=df['Estatistica'].loc[df['Estatistica']['ID Situação']=='AB']

                nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

                codigos=df['Vendedor'].loc[(df['Vendedor'][col]==codigo),'ID Vendedor'].tolist()

                for c in ['Estatistica','Meta','Estatico']:

                    df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)
                    df[c]=df[c].loc[(df[c]['ID Vendedor'].isin(codigos))&(df[c]['Mês']==val)]
                    
                    pass

                colunas={'Estatistica':'Em Aberto','Estatico':'Faturado'}

                for c in ['Estatico','Estatistica']:

                    df[c]=df[c].groupby(['ID Vendedor'],as_index=False).agg({'Total Venda':'sum'})
                    df[c].rename(columns={'Total Venda':colunas[c]},inplace=True)

                    df['Meta']=df['Meta'].merge(df[c],on='ID Vendedor',how='left')

                    pass

                for c in ['Em Aberto','Faturado']:

                    df['Meta'].loc[df['Meta'][c].isnull(),c]=0

                    pass

                for i in range(0,len(df['Meta'])):

                    soma=0

                    for c in ['Em Aberto','Faturado']:

                        soma+=df['Meta'].loc[i,c].sum()
                        
                        pass

                    df['Meta'].loc[i,'Realizado']=soma

                    pass

                val_dict=dict()

                for c in ['Meta R$','Faturado','Em Aberto','Realizado']:

                    val_dict[c]=df['Meta'][c].sum()
                    
                    pass

                df['Meta']['Perc']=df['Meta'].apply(lambda info: round(info['Realizado']/info['Meta R$'],4)*100 if info['Realizado']>0 and info['Meta R$']>0 else 0,axis=1)

                df['Uteis']=df['Uteis'].loc[df['Uteis']['Mês']==val]
                
                perc=round(val_dict['Realizado']/val_dict['Meta R$'],4)*100 if val_dict['Realizado']>0 else 0

                dif=round(val_dict['Meta R$']-val_dict['Realizado'],2)

                val_dict['Dias Úteis']=df['Uteis']['Dias Úteis'].sum()
                val_dict['Trabalhado']=df['Uteis']['Trabalhado'].sum()

                projecao=round((val_dict['Realizado']/val_dict['Trabalhado'])*val_dict['Dias Úteis'],2) if val_dict['Trabalhado']>0 else 0

                mensagem=f'Olá {nome} tudo bem? conforme solicitado segue as informações de quanto já realizou da meta de {val.title()}:\nMeta: R$ {Moeda.FormatarMoeda(val_dict["Meta R$"])}\nRealizado: R$ {Moeda.FormatarMoeda(val_dict["Realizado"])}\nPercentual: {Moeda.FormatarMoeda(perc)}%\nÁ Realizar: R$ {Moeda.FormatarMoeda(dif)}\nProjeção: R$ {Moeda.FormatarMoeda(projecao)}\n\nObs. Se quiser o relatório clique nesse link: /extrato' if perc<100 else f'Olá {nome} tudo bem? Parabéns você atingiu sua meta de {val.title()}:\nMeta: R$ {Moeda.FormatarMoeda(val_dict["Meta R$"])}\nRealizado: R$ {Moeda.FormatarMoeda(val_dict["Realizado"])}\nPercentual: {Moeda.FormatarMoeda(perc)}%\nRealizou: R$ {Moeda.FormatarMoeda(dif*-1)}\n\nObs. Se quiser o relatório clique nesse link: /extrato'

                name_arq=f'Meta {nome}.xlsx'

                temp_path=os.path.join(os.getcwd(),path.name,name_arq)            

                df['Meta'].to_excel(temp_path,index=False)

                arquivo=glob(temp_path)

                path_dict[chat_id]=arquivo            

                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                bot.send_message(chat_id=chat_id,text=mensagem)

                pass

            except:

                bot.send_message(chat_id=chat_id,text=f'{msg} {nome} não encontrei nenhum meta para o mês de {val.title()}')

                pass
         
            pass
        
        #tabelas de preço do sistema
        case 6:

            temp_dict=Colunas()
            
            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            col=temp_dict[codigo]

            df=sql.GetDados(querys=querys,colunas=['Tabelas','Vendedor'])

            for c in ['Tabelas','Vendedor']:

                df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)
                    
                pass

            codigos=df['Vendedor'].loc[df['Vendedor'][col]==codigo,'ID Vendedor'].unique().tolist()

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            df['Tabelas']=df['Tabelas'].loc[(df['Tabelas']['ID Vendedor'].isin(codigos))&((df['Tabelas']['Tabela']==val))]

            df['Tabelas']=df['Tabelas'][['Tabela','SKU', 'Produto', 'Fabricante','Categoria', 'Linha', 'Unid. VDA', 'Peso Liquido', 'Fator CX','Peso Liquido Caixa', 'Preço VDA','Desc Máx', 'Valor C/Desc']].drop_duplicates()

            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

            if len(df['Tabelas'])>0:        

                df['Tabelas'].to_excel(f'{val}.xlsx',index=False)
                
                with open(f'{val}.xlsx','rb') as file:

                    bot.send_document(chat_id=chat_id,document=file)

                    pass

                pass


            else:

                bot.send_message(chat_id=chat_id,text=f'{msg} {nome} você não tem autorização para acessar a tabela: <strong>{val.lower()}</strong>.')

                pass

            Remover.RemoverArquivo('.xlsx')

            pass

        #alerta de estoque
        case 7:

            temp_dict=Colunas()
            
            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            df=sql.GetDados(querys=querys,colunas=['Estoque','Vendedor'])

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            colunas=df['Estoque'].columns.tolist()

            df['Estoque']['SKU']=df['Estoque']['SKU'].astype(str)

            df['Estoque']['Descrição']=df['Estoque']['SKU'] +' - '+ df['Estoque']['Produto']
            
            lista=df['Estoque'].loc[df['Estoque']['Alerta']==val,'Descrição'].unique().tolist()

            count=Moeda.Numero(len(lista))
            
            mensagem=f'{msg} {nome} segue a relação dos produtos com o alerta de <strong>{val.lower()}</strong> no estoque. Nesta relação contém {count} itens.\nAbaixo segue os itens:\n\n.' if val!='ATENÇÃO' else f'{msg} {nome} segue a relação dos produtos com o alerta de <strong>{val.lower()}</strong> esses produtos tiveram índice de corte maior que um dia mesmo tendo saldo em estoque. Nesta relação contém {count} itens.\nAbaixo segue os itens:\n\n.'

            name_arq=f'{val.title()} {nome}.xlsx'

            temp_path=os.path.join(os.getcwd(),path.name,name_arq)            

            df['Estoque'][colunas].loc[df['Estoque']['Alerta']==val].to_excel(temp_path,index=False)

            arquivo=glob(temp_path)

            path_dict[chat_id]=arquivo     

            mensagem+='\n.'.join([l for l in lista])
            
            mensagem+='\n\nObs. Se quiser o relatório clique nesse link: /extrato'

            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
            bot.send_message(chat_id=chat_id,text=mensagem)

            pass

        #vendas por grupo
        case 8:

            temp_dict=Colunas()
            
            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            col=temp_dict[codigo]

            df=sql.GetDados(querys=querys,colunas=['Estatico','Realizado','Calendario','Produtos','Vendedor'])

            codigos=df['Vendedor'].loc[df['Vendedor'][col]==codigo,'ID Vendedor'].tolist()

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            df['Realizado']=df['Realizado'].loc[df['Realizado']['ID Situação']=='AB']

            dados_df=pd.DataFrame()
            
            for c in ['Estatico','Realizado']:

                df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)
                df[c]=df[c].loc[(df[c]['ID Vendedor'].isin(codigos))&(df[c]['Tipo de Operação']=='VENDAS')]
                df[c]=df[c].merge(df['Calendario'],left_on='Data de Faturamento',right_on='Data',how='inner')
                df[c]=df[c].merge(df['Produtos'],on='SKU',how='inner')
                df[c]=df[c].loc[df[c]['Mês']==val]
                df[c]=df[c].groupby(['ID Vendedor','Grupo DM'],as_index=False).agg({'Total Venda':'sum'})
                dados_df=pd.concat([dados_df,df[c]],axis=0,ignore_index=True)

                pass

            dados_df=dados_df.groupby(['ID Vendedor','Grupo DM'],as_index=False).agg({'Total Venda':'sum'})
            col_leach=dados_df['Grupo DM'].unique().tolist()
            col_id=dados_df.columns.tolist()
            dados_df=dados_df.merge(df['Vendedor'],on='ID Vendedor',how='inner')
            colunas=df['Vendedor'].columns.tolist()

            dados_df=dados_df.pivot(index=colunas,columns=col_id[1],values=col_id[-1]).reset_index()

            for c in col_leach:

                dados_df.loc[dados_df[c].isnull(),c]=0

                pass

            for i in range(0,len(dados_df)):

                soma=0

                for c in col_leach:

                    soma+=dados_df.loc[i,c].sum()

                    pass

                dados_df.loc[i,'Total Geral']=soma

                pass

            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

            if len(dados_df)>0:

                name_arq=f'Vendas por grupo {nome}.xlsx'

                temp_path=os.path.join(os.getcwd(),path.name,name_arq)            

                dados_df.to_excel(temp_path,index=False)

                arquivo=glob(temp_path)

                path_dict[chat_id]=arquivo                  

                vl_total=Moeda.FormatarMoeda(dados_df['Total Geral'].sum())

                mensagem=f'{msg} {nome} tudo bem identifiquei que no mês de {val.title()} você realizou <strong>R$ {vl_total}</strong>.\n\nMarcas:\n.'

                mensagem+='\n.'.join([f'{l}: R$ {Moeda.FormatarMoeda(dados_df[l].sum())}' for l in col_leach])

                mensagem+='\n\nObs. Se quiser o relatório clique nesse link: /extrato'

                bot.send_message(chat_id=chat_id,text=mensagem)

                pass


            else:

                bot.send_message(chat_id=chat_id,text=f'{msg} {nome} não encontrei venda para o mês de {val.title()}')

                pass


            pass

        #vendas por fabricante
        case 9:

            temp_dict=Colunas()
            
            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            col=temp_dict[codigo]

            df=sql.GetDados(querys=querys,colunas=['Estatico','Realizado','Calendario','Produtos','Vendedor'])

            codigos=df['Vendedor'].loc[df['Vendedor'][col]==codigo,'ID Vendedor'].tolist()

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            df['Realizado']=df['Realizado'].loc[df['Realizado']['ID Situação']=='AB']

            dados_df=pd.DataFrame()
            
            for c in ['Estatico','Realizado']:

                df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)
                df[c]=df[c].loc[(df[c]['ID Vendedor'].isin(codigos))&(df[c]['Tipo de Operação']=='VENDAS')]
                df[c]=df[c].merge(df['Calendario'],left_on='Data de Faturamento',right_on='Data',how='inner')
                df[c]=df[c].merge(df['Produtos'],on='SKU',how='inner')
                df[c]=df[c].loc[df[c]['Mês']==val]
                df[c]=df[c].groupby(['ID Vendedor','Fabricante'],as_index=False).agg({'Total Venda':'sum'})
                dados_df=pd.concat([dados_df,df[c]],axis=0,ignore_index=True)

                pass

            dados_df=dados_df.groupby(['ID Vendedor','Fabricante'],as_index=False).agg({'Total Venda':'sum'})
            col_leach=dados_df['Fabricante'].unique().tolist()
            col_id=dados_df.columns.tolist()
            dados_df=dados_df.merge(df['Vendedor'],on='ID Vendedor',how='inner')
            colunas=df['Vendedor'].columns.tolist()

            dados_df=dados_df.pivot(index=colunas,columns=col_id[1],values=col_id[-1]).reset_index()

            for c in col_leach:

                dados_df.loc[dados_df[c].isnull(),c]=0

                pass

            for i in range(0,len(dados_df)):

                soma=0

                for c in col_leach:

                    soma+=dados_df.loc[i,c].sum()

                    pass

                dados_df.loc[i,'Total Geral']=soma

                pass

            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

            if len(dados_df)>0:

                name_arq=f'Vendas por fabricante {nome}.xlsx'

                temp_path=os.path.join(os.getcwd(),path.name,name_arq)            

                dados_df.to_excel(temp_path,index=False)

                arquivo=glob(temp_path)

                path_dict[chat_id]=arquivo                  

                vl_total=Moeda.FormatarMoeda(dados_df['Total Geral'].sum())

                mensagem=f'{msg} {nome} tudo bem identifiquei que no mês de {val.title()} você realizou <strong>R$ {vl_total}</strong>.\n\nMarcas:\n.'

                mensagem+='\n.'.join([f'{l}: R$ {Moeda.FormatarMoeda(dados_df[l].sum())}' for l in col_leach])

                mensagem+='\n\nObs. Se quiser o relatório clique nesse link: /extrato'

                bot.send_message(chat_id=chat_id,text=mensagem)

                pass


            else:

                bot.send_message(chat_id=chat_id,text=f'{msg} {nome} não encontrei venda para o mês de {val.title()}')

                pass


            pass

        #sugestão de mix
        case 10:

            temp_dict=Colunas()
            
            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            col=temp_dict[codigo]

            df=sql.GetDados(querys=querys,colunas=['MIXSegmento','Vendedor','Produtos'])

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            lista=df['MIXSegmento']['Canal'].unique().tolist()

            if val in lista:

                lista=df['MIXSegmento'].loc[df['MIXSegmento']['Canal']==val,'Segmento'].unique().tolist()

                markup=InlineKeyboardMarkup(lista,call_back=id)
                
                #bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)

                bot.send_message(chat_id=chat_id,text=f'{msg} {nome} escolha uma das opções abaixo:',reply_markup=markup)

                pass

            else:

                bot.send_message(chat_id=chat_id,text='Aguarde estou análisando...')

                df['Consolidado']=AnaliseABC(colunas=['Segmento','Fabricante','Seção','Categoria','Linha','SKU'],tabela='Base ABC',col='Total Venda',df_tab=df['MIXSegmento'])

                df['Consolidado']=df['Consolidado'].loc[df['Consolidado']['Segmento']==val]

                if len(df['Consolidado'])>0:

                    qtde_prod=Moeda.Numero(len(df['Consolidado']['SKU'].unique().tolist()))

                    lista=df['Consolidado']['SKU'].unique().tolist()

                    mensagem=f'{msg} {nome} fez uma análise com base nas vendas de todos os clientes até <strong>90 dias</strong> para esse segmento e identifiquei {qtde_prod} produto(s) com potêncial de vendas.\n\n{val.title()} sugestão de mix:\n.'

                    mensagem+='\n.'.join([str(df["Produtos"].loc[df["Produtos"]["SKU"]==l,"Produto"].tolist()[-1]).title() for l in lista])

                    dados_df=pd.DataFrame()

                    for l in lista:

                        querys['XY']=f"""
                        
                        WITH TabBase AS (

                            SELECT vda.cd_clien,i.cd_prod,i.nu_ped,SUM(i.qtde) AS qtde,SUM(i.vl_venda) AS vl_venda
                            FROM it_pedv i
                            INNER JOIN ped_vda vda ON i.cd_emp=vda.cd_emp AND i.nu_ped=vda.nu_ped
                            INNER JOIN tp_ped t ON vda.tp_ped=t.tp_ped AND t.estat_com=1
                            INNER JOIN nota nf ON i.cd_emp=nf.cd_emp AND i.nu_nf=nf.nu_nf AND i.nu_ped=nf.nu_ped
                            INNER JOIN empresa emp ON i.cd_emp=emp.cd_emp AND emp.ativo=1
                            INNER JOIN par_cfg c ON emp.cd_emp=c.cd_emp
                            INNER JOIN produto p ON i.cd_prod=p.cd_prod AND p.ativo=1
                            WHERE i.situacao IN ('FA') AND CONVERT(DATETIME,CAST(nf.dt_emis AS DATE),101) BETWEEN DATEADD(DAY,c.nu_dias_vdamedia*-1,
                            CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)) AND CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)
                            GROUP BY vda.cd_clien,i.cd_prod,i.nu_ped

                        )


                        SELECT * FROM (

                            SELECT f.quem_comprou AS [SKU],f.tambem_comprou AS [Lista],f.contagem AS [Valor],f.classificacao AS [Classificação],
                            ROW_NUMBER()OVER(PARTITION BY f.quem_comprou ORDER BY f.contagem DESC) AS [Seq]
                            FROM (

                                SELECT e.quem_comprou,e.tambem_comprou,e.contagem,e.acumulado,e.total,e.perc,
                                CASE WHEN (e.perc*100)<=80 THEN 'A' WHEN (e.perc*100)<=95 THEN 'B' ELSE 'C' END AS classificacao
                                FROM (

                                    SELECT d.quem_comprou,d.tambem_comprou,d.contagem,d.acumulado,d.total,
                                    CONVERT(DECIMAL(15,4),CONVERT(DECIMAL(15,2),d.acumulado)/NULLIF(CONVERT(DECIMAL(15,2),d.total),0)) AS perc
                                    FROM (

                                        SELECT c.quem_comprou,c.tambem_comprou,c.contagem,
                                        SUM(c.contagem)OVER(ORDER BY c.contagem DESC) AS acumulado,
                                        SUM(c.contagem)OVER() AS total
                                        FROM (

                                            SELECT a.cd_prod AS quem_comprou,b.cd_prod AS tambem_comprou,COUNT(b.nu_ped) AS contagem
                                            FROM TabBase a
                                            INNER JOIN TabBase b ON a.nu_ped=b.nu_ped AND a.cd_prod<>b.cd_prod
                                            WHERE a.cd_prod={l}
                                            GROUP BY a.cd_prod,b.cd_prod

                                        )c

                                    )d

                                )e

                            )f

                        )g
                        WHERE g.Seq<=5
                        ORDER BY g.Valor DESC
                        
                        """

                        df=sql.GetDados(querys,colunas=['XY'])

                        dados_df=pd.concat([dados_df,df['XY']],axis=0,ignore_index=True)

                        pass

                    dados_df=dados_df.loc[~dados_df['Lista'].isin(lista)]

                    df=sql.GetDados(querys=querys,colunas=['MIXSegmento','Vendedor','Produtos'])

                    for i in lista:

                        prod_x=str(df['Produtos'].loc[df['Produtos']['SKU']==i,'Produto'].tolist()[-1]).title()

                        mensagem+=f'\n\nQuem compra <strong>{prod_x}</strong> leva esses itens:\n.'

                        df['Consolidado']=dados_df.loc[dados_df['SKU']==i]

                        if len(df['Consolidado'])<=0:

                            continue

                        for j in df['Consolidado']['Lista'].unique().tolist():

                            prod_y=str(df['Produtos'].loc[df['Produtos']['SKU']==j,'Produto'].tolist()[-1]).title()
                            
                            mensagem+=f'\n.{prod_y}'

                            pass

                        pass

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=mensagem)

                    pass

                else:

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=f'{nome} não encontrei nenhum mix ideal para esse segmento.')

                    pass

                pass

            pass

        #devolução
        case 11:

            arr_list=col_dict[comando]
            arr_list.append('Devolucao')
            arr_list.append('Calendario')

            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            temp_dict=Colunas()

            col=temp_dict[codigo]
            
            df=sql.GetDados(querys=querys,colunas=col_dict[comando])

            codigos=df['Vendedor'].loc[df['Vendedor'][col]==codigo,'ID Vendedor'].tolist()

            for c in ['Devolucao','Vendedor']:

                df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)

                pass

            df['Devolucao']=df['Devolucao'].loc[df['Devolucao']['ID Vendedor'].isin(codigos)]

            df['Devolucao']=df['Devolucao'].merge(df['Calendario'],left_on='Data de Entrada',right_on='Data',how='inner')

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            df['Devolucao']=df['Devolucao'].loc[(df['Devolucao']['Mês']==val)&((df['Devolucao']['Ano']==datetime.now().year))]

            df['Devolucao'].sort_values('Data de Entrada',ascending=True,ignore_index=True,inplace=True)

            df['Devolucao']['Data Converte']=df['Devolucao']['Data de Entrada'].apply(DataConverte)

            lista=df['Devolucao']['Data Converte'].unique().tolist()
                
            if len(lista)>1:

                markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                #bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)

                bot.send_message(chat_id=chat_id,text='Escolha uma das opções abaixo:',reply_markup=markup)      

                pass

            else:

                bot.send_message(chat_id=chat_id,text='Aguarde estou análisando...')

                arr_list=col_dict[comando]
                arr_list.append('Devolucao')

                df=sql.GetDados(querys=querys,colunas=col_dict[comando])

                for c in ['Vendedor','Devolucao']:

                    df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)

                    pass

                df['Devolucao']=df['Devolucao'].loc[df['Devolucao']['ID Vendedor'].isin(codigos)]                
                
                df['Devolucao']['Data Converte']=df['Devolucao']['Data de Entrada'].apply(DataConverte)                 

                val=val if val.find('/')>0 else lista[-1]

                df['Devolucao']=df['Devolucao'].loc[df['Devolucao']['Data Converte']==val]

                if len(df['Devolucao'])>0:

                    vl_total=Moeda.FormatarMoeda(df['Devolucao']['Total Geral'].sum())

                    pedidos=Moeda.Numero(len(df['Devolucao']['Pedido'].unique().tolist()))

                    mensagem=f'{msg} {nome} no dia {val} identifiquei <strong>{pedidos} pedido(s)</strong> que foram devolvidos totalizando <strong>R$ {vl_total}</strong>.\n\nMotivos:\n\n.'

                    name_arq=f'Devolução {nome}.xlsx'

                    temp_path=os.path.join(os.getcwd(),path.name,name_arq)

                    df['Devolucao'].to_excel(temp_path,index=False)

                    arquivo=glob(temp_path)

                    path_dict[chat_id]=arquivo

                    df['Consolidado']=df['Devolucao'].groupby(['Motivo'],as_index=False).agg({'Total Geral':'sum'})
                    df['Consolidado'].sort_values('Total Geral',ascending=False,ignore_index=True,inplace=True)

                    df['Consolidado']['Info']=df['Consolidado'].apply(lambda info: f'{str(info["Motivo"]).capitalize()} - Total: R$ {Moeda.FormatarMoeda(info["Total Geral"])}',axis=1)

                    mensagem+='\n.'.join([l for l in df['Consolidado']['Info'].unique().tolist()])

                    mensagem+='\n\nObs. Se quiser o relatório clique nesse link: /extrato'

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=mensagem)

                    pass

                else:

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=f'{msg} {nome} não encontrei nenhuma devolução para o dia informado!')

                    pass

                pass

            pass
        
        #corte de produto
        case 12:

            arr_list=col_dict[comando]
            arr_list.append('Corte')
            arr_list.append('Calendario')

            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            temp_dict=Colunas()

            col=temp_dict[codigo]
            
            df=sql.GetDados(querys=querys,colunas=col_dict[comando])

            codigos=df['Vendedor'].loc[df['Vendedor'][col]==codigo,'ID Vendedor'].tolist()

            for c in ['Vendedor','Corte']:

                df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)

                pass

            df['Corte']=df['Corte'].loc[df['Corte']['ID Vendedor'].isin(codigos)]
            
            df['Corte']=df['Corte'].merge(df['Calendario'],left_on='Data de Falta',right_on='Data',how='inner')

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            df['Corte']=df['Corte'].loc[(df['Corte']['Mês']==val)&((df['Corte']['Ano']==datetime.now().year))]

            df['Corte'].sort_values('Data de Falta',ascending=True,ignore_index=True,inplace=True)

            df['Corte']['Data Converte']=df['Corte']['Data de Falta'].apply(DataConverte)

            lista=df['Corte']['Data Converte'].unique().tolist()
            
            if len(lista)>1:

                markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                #bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)

                bot.send_message(chat_id=chat_id,text='Escolha uma das opções abaixo:',reply_markup=markup)      

                pass

            else:

                bot.send_message(chat_id=chat_id,text='Aguarde estou análisando...')

                arr_list=col_dict[comando]
                arr_list.append('Corte')

                df=sql.GetDados(querys=querys,colunas=col_dict[comando])

                for c in ['Vendedor','Corte']:

                    df[c]['ID Vendedor']=df[c]['ID Vendedor'].apply(RemoverEspaco)

                    pass

                df['Corte']=df['Corte'].loc[df['Corte']['ID Vendedor'].isin(codigos)]                
                
                df['Corte']['Data Converte']=df['Corte']['Data de Falta'].apply(DataConverte)       

                val=val if val.find('/')>0 else lista[-1]

                df['Corte']=df['Corte'].loc[df['Corte']['Data Converte']==val]

                if len(df['Corte'])>0:

                    qtde_pedido=Moeda.Numero(len(df['Corte']['Pedido'].unique().tolist()))

                    qtde_cortada=Moeda.Numero(df['Corte']['Qtde. VDA'].sum())

                    vl_total=Moeda.FormatarMoeda(df['Corte']['Total do Pedido'].sum())

                    mensagem=f'{msg} {nome}, identifiquei que no dia {val} teve {qtde_pedido} pedido(s) cortados, isso representa um total de R$ {vl_total} e {qtde_cortada} unidade(s). Segue os itens abaixo:\n\n.'

                    df['Consolidado']=df['Corte'].groupby(['Produto'],as_index=False).agg({'Qtde. VDA':'sum'})

                    df['Consolidado'].sort_values('Qtde. VDA',ascending=False,ignore_index=True,inplace=True)

                    df['Consolidado']['Qtde. VDA']=df['Consolidado']['Qtde. VDA'].astype(str)

                    df['Consolidado']['Info']=df['Consolidado'].apply(lambda info: f'{str(info["Produto"]).capitalize()} - Qtde cortada: {Moeda.FormatarMoeda(info["Qtde. VDA"])}',axis=1)                    

                    lista=df['Consolidado']['Info'].unique().tolist()
                    
                    mensagem+='\n.'.join([l for l in lista])

                    mensagem+='\n\nObs. Se quiser o relatório clique nesse link: /extrato'

                    name_arq=f'Corte {nome}.xlsx'

                    temp_path=os.path.join(os.getcwd(),path.name,name_arq)            

                    df['Corte'].to_excel(temp_path,index=False)

                    arquivo=glob(temp_path)

                    path_dict[chat_id]=arquivo

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=mensagem)

                    pass


                else:

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=f'{msg} {nome} não encontrei corte para o dia informado!')

                    pass

                pass

            pass

    pass

@bot.message_handler(commands=['extrato'])
def Extrair(message):

    chat_id=message.from_user.id

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=['Vendedor'])

    nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)    
    bot.delete_message(chat_id=chat_id,message_id=message.message_id)

    try:
        
        arquivo=path_dict[chat_id]

        if len(arquivo)>0:

            with open(arquivo[-1],'rb') as file:

                bot.send_document(chat_id=chat_id,document=file)

                pass
            
            path_dict.pop(chat_id)
            Remover.Remove(arquivo[-1])

            pass

        else:

            bot.send_message(chat_id=chat_id,text=f'Olá {nome} caso queira o extrato do relatório você deve executar o comando novamente! Grato')

            pass

        pass

    except:

        bot.send_message(chat_id=chat_id,text=f'{nome} não encontrei nenhum arquivo no extrato recomendo você executar novamente o comando.')

        pass

    pass

def ValidacaoProduto(message):

    chat_id=message.from_user.id

    func=funcoes[message.text]

    bot.send_chat_action(chat_id=chat_id,action='typing')
    #bot.delete_message(chat_id=chat_id,message_id=message.message_id)

    bot.send_message(chat_id=chat_id,text=f'Assunto: {func}\n\nInforme o código do(s) produto(s), caso for mais de um produto inserir uma virgula para fazer a inserção de mais códigos.')

    bot.register_next_step_handler(message=message,callback=globals().get(func))

    pass

def Carteira(message):

    chat_id=message.from_user.id

    #bot.delete_message(chat_id=chat_id,message_id=message.message_id)

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=['Vendedor'])

    temp_dict=Colunas()

    col_dict={'ID Gerente':'ID Sup','ID Sup':'Equipe','ID Vendedor':'Nome Resumido'}

    lista=df['Vendedor'].loc[(df['Vendedor']['Status do Vendedor']=='ATIVO')&(df['Vendedor'][temp_dict[codigo]]==codigo),col_dict[temp_dict[codigo]]].unique().tolist()

    markup=InlineKeyboardMarkup(lista,call_back=1)
        
    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
    
    bot.send_message(chat_id=chat_id,text='Escolha uma das opções abaixo:',reply_markup=markup)

    pass

def Foto(message):

    chat_id=message.from_user.id

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    codigos=[int(l) for l in str(message.text).split(',') if str(l).isnumeric()]

    df=sql.GetDados(querys=querys,colunas=['Vendedor','Fotos'])

    df['Fotos']=df['Fotos'].loc[(df['Fotos']['SKU'].isin(codigos))&(df['Fotos']['Fotos'].notnull())]

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

    erros=[l for l in codigos if not l in df['Fotos']['SKU'].unique().tolist()]

    erros=','.join([str(l) for l in erros])

    if len(df['Fotos'])>0:

        #bot.delete_message(chat_id=message.from_user.id,message_id=message.message_id)
        bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

        path_base=Path(__file__).parent.joinpath('Fotos')
        path_base.mkdir(exist_ok=True)

        mensagem=f'Obs: Não encontramos na relação esses códigos com as fotos: <strong>{erros}</strong>'
        temp=[]
        for arq in df['Fotos']['Fotos'].unique().tolist():

            arq_name=os.path.basename(arq)

            path_destino=os.path.join(path_base,arq_name)

            shutil.copy(arq,path_destino)

            with Image.open(arq) as img:

                width,heigth=img.size

                new_width=2240
                
                if width>new_width:
                    
                    new_height=Calc_img(width,heigth,new_width)

                    new_img=img.resize((new_width,new_height),Image.LANCZOS)
                    new_img.save(path_destino)
                    
                    pass                

                pass

            try:

                with open(path_destino,'rb') as file:

                    temp.append(types.InputMediaPhoto(

                        file.read()
                    ))

                pass

            except:

                continue            

            pass

        bot.send_media_group(chat_id=chat_id,media=temp)
        shutil.rmtree(os.path.join(path_base))

        if len(erros)>0:

            bot.send_message(chat_id=chat_id,text=mensagem)

            pass

        pass


    else:
        
        #bot.delete_message(chat_id=message.from_user.id,message_id=message.message_id)
        bot.send_chat_action(chat_id=chat_id,action='typing')
        bot.send_message(chat_id=chat_id,text=f'{msg} {nome} tudo bem! não identificamos nenhum produto com esse código com foto: <strong>{erros}</strong>')

        pass

    pass

def FichaTecnica(message):

    chat_id=message.from_user.id

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=['Vendedor'])

    nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()      

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    codigos=[int(l) for l in str(message.text).split(',') if str(l).isnumeric()]
    
    path_base=Path(r'V:\Documentos Empresa')

    temp_dict=dict()

    for l in path_base.rglob('*.pdf*'):

        id=int(str(Path(l).name).split('.')[0])

        temp_dict[id]=os.path.join(l)

        pass

    df=pd.DataFrame(data=temp_dict.items(),columns=['SKU','Paths'])

    df=df.loc[df['SKU'].isin(codigos)]

    erros=[l for l in codigos if not l in df['SKU'].unique().tolist()]

    erros=','.join([str(l) for l in erros])

    if len(df)>0:

        #bot.delete_message(chat_id=message.from_user.id,message_id=message.message_id)
        bot.send_chat_action(chat_id=chat_id,action='typing')

        #criar a pasta
        temp_path=Path(__file__)

        temp_path=temp_path.parent.joinpath('Ficha Técnica')
        temp_path.mkdir(exist_ok=True)

        #mover as fichas
        for arq in df['Paths'].unique().tolist():

            try:

                arq_name=Path(arq).name
            
                path_destino=temp_path.joinpath(arq_name)

                shutil.copy(arq,path_destino)

                pass

            except:

                continue

            pass

        
        shutil.make_archive(temp_path.name,'zip',os.path.join(temp_path))

        shutil.rmtree(temp_path)

        zip_path=os.path.join(os.getcwd(),f'{temp_path.name}.zip')

        zips=Web(zip_path)

        link=zips.WebLink()
        
        mensagem=f'{msg};\n{nome} tudo bem?\n\nSegue o link das fichas técnicas: {link}' if len(erros)<=0 else f'{msg};\n{nome} tudo bem?\n\nSegue o link das fichas técnicas: {link}.\n\nObs: Não encontramos na relação esses códigos com as fotos: <strong>{erros}</strong>'

        bot.send_chat_action(chat_id=chat_id,action='typing')
        bot.send_message(chat_id=chat_id,text=mensagem)

        pass


    else:
        
        #bot.delete_message(chat_id=message.from_user.id,message_id=message.message_id)
        bot.send_chat_action(chat_id=message.from_user.id,action='typing')

        bot.send_message(chat_id=message.from_user.id,text=f'{msg} {nome} tudo bem! não identificamos nenhum produto com esses códigos: <strong>{erros}</strong>')

        pass

    Remover.RemoverArquivo('.zip')

    pass

def DadosProdutos(message):

    chat_id=message.from_user.id

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    codigos=[int(l) for l in str(message.text).split(',') if str(l).isnumeric()]

    df=sql.GetDados(querys=querys,colunas=['Vendedor','Produtos'])

    df['Produtos']=df['Produtos'].loc[df['Produtos']['SKU'].isin(codigos)]

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

    erros=[l for l in codigos if not l in df['Produtos']['SKU'].unique().tolist()]

    erros=','.join([str(l) for l in erros])

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)    

    if len(df['Produtos'])>0:

        df['Produtos'].to_excel('Dados dos produtos.xlsx',index=False)

        with open('Dados dos produtos.xlsx','rb') as file:
        
            mensagem=f'{msg};\n{nome} tudo bem?\n\nSegue o arquivo com os dados dos produtos.' if len(erros)<=0 else f'{msg};\n{nome} tudo bem?\n\nSegue o arquivo com os dados dos produtos.\n\nObs: Não encontramos na relação esses códigos: <strong>{erros}</strong>'
            
            bot.send_document(chat_id=chat_id,document=file,caption=mensagem)

            pass

        Remover.RemoverArquivo('.xlsx')

        pass

    else:

        bot.send_message(chat_id=chat_id,text=f'{msg} {nome} tudo bem! não identificamos nenhum produto com esses códigos: <strong>{erros}</strong>')

        pass    

    pass

def ValidacaoID(message):

    chat_id=message.from_user.id

    codigo=str(message.text).upper().strip()

    temp_path=Path(__file__)

    temp_path=os.path.join(temp_path.parent.joinpath('Memória','Consolidado.xlsx'))

    temp_df=pd.read_excel(temp_path)

    df=sql.GetDados(querys=querys,colunas=['Vendedor'])

    count=len(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo])
    
    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
    #bot.delete_message(chat_id=chat_id,message_id=message.message_id)

    if count>0:

        id_temp=temp_df.loc[temp_df['Código']==codigo,'ChatID'].tolist()

        if len(id_temp)>0:

            bot.send_message(chat_id=chat_id,text='Identificamos que o código desse usuário já está sendo usando em outro aparelho. Caso você desconheça essa informação entrar em contato com o administrador da plataforma.')

            bot.register_next_step_handler(message=message,callback=ValidacaoID)

            pass

        else:

            bot.send_chat_action(chat_id=message.from_user.id,action='typing')
            #bot.delete_message(chat_id=message.from_user.id,message_id=message.message_id)

            nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

            temp_df.loc[len(temp_df)]=[chat_id,codigo]

            temp_df.to_excel(temp_path,index=False,sheet_name='Chat')

            bot.send_message(chat_id=chat_id,text=f'Seja bem vindo {nome}.')

            CommandsMenu()

            pass

        pass

    else:

        bot.send_message(chat_id=chat_id,text='Usuário informado não existe no sistema!')

        bot.register_next_step_handler(message=message,callback=ValidacaoID)

        pass

    pass

def Realizado(message):

    chat_id=message.from_user.id

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    dt_atual=datetime.strftime(datetime.now().date(),'%d/%m/%Y')

    temp_df=Memoria(chat_id=chat_id)

    temp_dict=Colunas()
    
    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys,colunas=['Realizado','Vendedor'])

    lista=df['Vendedor'].loc[df['Vendedor'][temp_dict[codigo]]==codigo,'ID Vendedor'].tolist()

    df['Realizado']['ID Vendedor']=df['Realizado']['ID Vendedor'].apply(RemoverEspaco)

    nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

    df['Realizado']=df['Realizado'].loc[df['Realizado']['ID Vendedor'].isin(lista)]

    MIX=Moeda.Numero(len(df['Realizado']['SKU'].unique().tolist()))

    cliente=Moeda.Numero(len(df['Realizado']['ID Cliente'].unique().tolist()))

    pedidos=len(df['Realizado']['Pedido'].unique().tolist())

    vl_total=df['Realizado']['Total Geral'].sum()

    ticket=round(vl_total/pedidos,2)

    ticket=Moeda.FormatarMoeda(ticket)

    pedidos=Moeda.Numero(len(df['Realizado']['Pedido'].unique().tolist()))

    vl_total=Moeda.FormatarMoeda(df['Realizado']['Total Geral'].sum())

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    if len(df['Realizado'])>0:

        mensagem=f'{msg} {nome} segue as informações abaixo referente ao dia: <strong>{dt_atual}.</strong>\nRealizado: R$ {vl_total}\nPedidos: {pedidos}\nAtendimento: {cliente}\nMIX: {MIX}\nTicket Médio: R$ {ticket}'

        bot.send_message(chat_id=chat_id,text=mensagem)

        pass


    else:

        bot.send_message(chat_id=chat_id,text=f'{msg} {nome} não encontramos venda realizadas no dia: <strong>{dt_atual}</strong>')

        pass


    pass

def Custo(message):

    chat_id=message.from_user.id

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    codigos=[int(l) for l in str(message.text).split(',') if str(l).isnumeric()]    

    df=sql.GetDados(querys,colunas=['Custo','Vendedor'])

    df['Custo']=df['Custo'].loc[df['Custo']['SKU'].isin(codigos)]

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    temp_dict=Colunas()

    col=temp_dict[codigo]

    nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    if col=='ID Vendedor':

        bot.send_message(chat_id=chat_id,text=f'{msg} {nome} você não tem autorização para fazer essa consulta.')

        pass

    else:
        
        erros=[l for l in codigos if not l in df['Custo']['SKU'].unique().tolist()]

        erros=','.join([str(l) for l in erros])
        
        if len(df['Custo'])>0:

            if len(df['Custo'])==1:

                produto=df['Custo']['Produto'].tolist()[-1]

                unid=df['Custo']['Unid. CMP'].tolist()[-1]

                vl_custo=df['Custo']['Atual C/ST'].sum()

                vl_ant=df['Custo']['Anterior C/ST'].sum()

                perc=df['Custo']['Perc %'].sum()

                dif=df['Custo']['Dif R$'].sum()

                mensagem=f'{msg};\n{nome} tudo bem?\n\nO custo do item <strong>{produto}</strong>:\nUnidade de Compra: {unid}\nCusto Atual: R$ {Moeda.FormatarMoeda(vl_custo)}\nCusto Anterior: R$ {Moeda.FormatarMoeda(vl_ant)}\nPercentual de Ajuste: {Moeda.FormatarMoeda(perc)}%\nDiferença: R$ {Moeda.FormatarMoeda(dif)}' if len(erros)<=0 else f'{msg};\n{nome} tudo bem?\n\nO custo do item <strong>{produto}</strong>:\nUnidade de Compra: {unid}\nCusto Atual: R$ {Moeda.FormatarMoeda(vl_custo)}\nCusto Anterior: R$ {Moeda.FormatarMoeda(vl_ant)}\nPercentual de Ajuste: {Moeda.FormatarMoeda(perc)}%\nDiferença: R$ {Moeda.FormatarMoeda(dif)}\n\nObs: Não encontramos na relação esses códigos: <strong>{erros}</strong'
                
                bot.send_message(chat_id=chat_id,text=mensagem)

                pass

            else:

                df['Custo'].to_excel('Custo dos produtos.xlsx',index=False)

                with open('Custo dos produtos.xlsx','rb') as file:
                
                    mensagem=f'{msg};\n{nome} tudo bem?\n\nSegue o arquivo com os dados dos produtos.' if len(erros)<=0 else f'{msg};\n{nome} tudo bem?\n\nSegue o arquivo com os dados dos produtos.\n\nObs: Não encontramos na relação esses códigos: <strong>{erros}</strong>'
                    
                    bot.send_document(chat_id=chat_id,document=file,caption=mensagem)

                    pass

                pass
            

            Remover.RemoverArquivo('.xlsx')


            pass


        else:

            bot.send_message(chat_id=chat_id,text=f'{msg} {nome} tudo bem! não identificamos nenhum produto com esses códigos: <strong>{erros}</strong>')

            pass

        pass

    pass

def Estoque(message):

    chat_id=message.from_user.id

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]    

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    codigos=[int(l) for l in str(message.text).split(',') if str(l).isnumeric()]    

    df=sql.GetDados(querys,colunas=['Estoque','Vendedor'])

    nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

    df['Estoque']=df['Estoque'].loc[df['Estoque']['SKU'].isin(codigos)]

    colunas=df['Estoque'].columns.tolist()

    erros=[l for l in codigos if not l in df['Estoque']['SKU'].unique().tolist()]

    erros=','.join([str(l) for l in erros])

    if len(df['Estoque'])>0:

        for c in ['SKU','Saldo Caixa']:

            df['Estoque'][c]=df['Estoque'][c].astype(str)

            pass

        df['Estoque']['Info']=df['Estoque']['SKU'] + ' - ' + df['Estoque']['Produto'] + ' Caixa: ' + df['Estoque']['Saldo Caixa']

        mensagem=f'{msg} {nome} segue o saldo dos itens em estoque conforme abaixo:\n\n.'

        mensagem+='\n.'.join([l for l in df['Estoque']['Info'].unique().tolist()])

        if len(erros)>0:

            mensagem+='\n\nObs: Não encontramos na relação esses códigos: <strong>{erros}</strong'

            pass

        bot.send_message(chat_id=chat_id,text=mensagem)

        pass

    else:

        bot.send_message(chat_id=chat_id,text=f'{msg} {nome} tudo bem! não identificamos nenhum produto com esses códigos: <strong>{erros}</strong>')

        pass

    pass

def Classificacao(val):

    if val<=33.33:

        tipo='A'

        pass

    elif val<=66.66:

        tipo='B'

        pass


    else:

        tipo='C'

        pass


    return tipo


    pass

def AnaliseABC(colunas: list,tabela: str,col: None,df_tab: None):

    df=dict()

    df['Temp']=df_tab

    for i,c in enumerate(colunas):
        
        temp_df=pd.DataFrame()
        
        if i==0:
                
            df[tabela]=df['Temp'].groupby(c,as_index=False).agg({col:'sum'})
            
            df[tabela].sort_values(col,ascending=False,ignore_index=True,inplace=True)

            df[tabela]['Total']=df[tabela][col].sum()

            df[tabela]['Perc Geral']=round(df[tabela][col]/df[tabela]['Total'],4)*100

            valores=[]

            total=0

            for j in range(0,len(df[tabela])):

                total+=df[tabela].loc[j,col].sum()

                valores.append(total)

                pass

            df[tabela]['Acumulado']=valores

            df[tabela]['Perc']=round(df[tabela]['Acumulado']/df[tabela]['Total'],4)*100

            df[tabela]['Classificação']=df[tabela]['Perc'].apply(Classificacao)

            #df[tabela]=df[tabela].loc[df[tabela]['Classificação']!='C']
            
            pass
        
        else:
                    
            indixe=df[tabela][colunas[i-1]].unique().tolist()
                    
            for g in indixe:
            
                df[tabela]=df['Temp'].loc[df['Temp'][colunas[i-1]]==g].groupby(colunas[:i+1],as_index=False).agg({col:'sum'})

                df[tabela].sort_values(col,ascending=False,ignore_index=True,inplace=True)

                df[tabela]['Total']=df[tabela][col].sum()

                df[tabela]['Perc Geral']=round(df[tabela][col]/df[tabela]['Total'],4)*100        

                valores=[]

                total=0

                for j in range(0,len(df[tabela])):

                    total+=df[tabela].loc[j,col].sum()

                    valores.append(total)

                    pass

                df[tabela]['Acumulado']=valores

                df[tabela]['Perc']=round(df[tabela]['Acumulado']/df[tabela]['Total'],4)*100

                df[tabela]['Classificação']=df[tabela]['Perc'].apply(Classificacao)

                df[tabela]=df[tabela].loc[df[tabela]['Classificação']!='C']
                
                temp_df=pd.concat([temp_df,df[tabela]],axis=0,ignore_index=True)
                
                pass
            
            df[tabela]=temp_df
                    
            pass

        pass

    return df[tabela]

    pass

#opções
def Opcao(message):

    chat_id=message.from_user.id
    
    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    df['Vendedor']['ID Vendedor']=df['Vendedor']['ID Vendedor'].apply(RemoverEspaco)

    nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

    lista=df[tab_dict[comando]][col_name[comando]].unique().tolist()

    markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
    bot.send_message(chat_id=chat_id,text=f'{msg} {nome} escolha uma das opções abaixo:',reply_markup=markup)

    pass

def Alerta(message):

    chat_id=message.from_user.id

    temp_dict=Colunas()
    
    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==codigo,'Nome Resumido'].tolist()[-1]).title()

    lista=df[tab_dict[comando]].loc[(df[tab_dict[comando]][col_name[comando]]!='OK'),col_name[comando]].unique().tolist()
    
    markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
    bot.send_message(chat_id=chat_id,text=f'{msg} {nome} escolha uma das opções abaixo:',reply_markup=markup)    
    
    pass

#funções
def Colunas():

    df=sql.GetDados(querys=querys,colunas=['Vendedor'])

    lista=[]

    temp_dict=dict()

    for c in ['ID Gerente','ID Sup','ID Vendedor']:

        codigos=df['Vendedor'][c].unique().tolist()

        for i in codigos:

            if i in lista:
                
                continue

            lista.append(i)

            temp_dict[i]=c

            pass

        pass

    return temp_dict

    pass

def ReplyKeyboardMarkup(lista: list):

    markup=types.ReplyKeyboardMarkup(row_width=1)

    for l in lista:

        markup.add(

            types.KeyboardButton(text=l)

        )

        pass

    return markup

    pass

def InlineKeyboardMarkup(lista: list,call_back: int):

    markup=types.InlineKeyboardMarkup(row_width=1)

    for l in lista:

        markup.add(

            types.InlineKeyboardButton(text=l,callback_data=f'{str(call_back)}/{l}')
        )

        pass

    return markup    

    pass

def CommandsMenu():

    bot.delete_my_commands()
    
    bot.set_my_commands([

        types.BotCommand(command=str(comando),description=str(descricao)) for comando,descricao in commands_dict.items()
    ])

    bot.set_my_commands(bot.get_my_commands())

    pass

def Memoria(chat_id):
    
    temp_path=Path(__file__)

    temp_path=os.path.join(temp_path.parent.joinpath('Memória','Consolidado.xlsx'))

    temp_df=pd.read_excel(temp_path)

    temp_df=temp_df.loc[temp_df['ChatID']==chat_id]

    return temp_df

    pass

def RemoverEspaco(val):

    return str(val).strip()

    pass

def Voice(mensagem):

    engine=pyttsx3.init()

    caracteres=len([l for l in mensagem])

    rate=engine.getProperty('rate')
    engine.setProperty('rate',(rate-caracteres)+caracteres)
    engine.save_to_file(mensagem,'audio.mp3')
    engine.runAndWait()

    temp_path=os.path.join(os.getcwd(),'audio.mp3')

    return temp_path

    pass

def DataConverte(data):

    return datetime.strftime(data,'%d/%m/%Y')

    pass

def Calc_img(width,height,new_width):

    return round(new_width*(height/width))

    pass

def Start():

    while True:

        try:
           
            print('BOT Telegram conectado!')

            bot.polling()

            pass

        except Exception as erro:

            print('BOT Telegram desconectado!')

            Start()          

            pass

        pass

    pass

if __name__=='__main__':

    Start()

    pass