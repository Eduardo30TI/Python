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
import pyttsx3
from Acentos import Acentuacao
from PIL import Image

#TOKEN_PROD de produção
#TOKEN de teste
TOKEN=config('TOKEN_PROD')

bot=telebot.TeleBot(TOKEN,parse_mode='html')

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

path_dict=dict()

comando=None

variavel_dict=dict()

commands_dict={

    '/comandos':'Atualizar comandos na barra de menu',
    '/foto':'Foto dos produtos',
    '/fichatecnica': 'Ficha técnica dos produtos',
    '/dadosprodutos': 'Dados dos produtos',
    '/custo':'Consultar o custo do produto',
    '/alerta':'Alerta de estoque',
    '/estoque':'Consultar estoque',
    '/pendente':'Pedente de roterização',
    '/corte':'Corte de produto',
    '/sellin':'Compra anual por fornecedor',
    '/roteiro':'Roteiro de entrega',
    '/devolucao':'Devolução de mercadoria'

}

start={

    '/comandos':'CommandsMenu',
    '/foto':'ValidacaoProduto',
    '/fichatecnica': 'ValidacaoProduto',
    '/dadosprodutos': 'ValidacaoProduto',
    '/custo':'ValidacaoProduto',
    '/alerta':'Alerta',
    '/estoque':'ValidacaoProduto',
    '/pendente':'Pendente',
    '/corte':'Opcao',
    '/sellin':'Opcao',
    '/roteiro':'Opcao',
    '/devolucao':'Opcao'

}

funcoes={

    '/comandos':'CommandsMenu',
    '/foto':'Foto',
    '/fichatecnica': 'FichaTecnica',
    '/dadosprodutos': 'DadosProdutos',
    '/custo':'Custo',
    '/alerta':'Alerta',
    '/estoque':'Estoque',
    '/pendente':'Pendente',
    '/corte':'Opcao',
    '/sellin':'Opcao',
    '/roteiro':'Opcao',
    '/devolucao':'Opcao'

}

#função usando para opções
col_dict={

    '/alerta':['Estoque','Usuario'],
    '/foto':['Fotos','Usuario'],
    '/fichatecnica': ['Produtos','Usuario'],
    '/dadosprodutos': ['Produtos','Usuario'],
    '/custo':['Custo','Usuario'],
    '/alerta':['Estoque','Usuario'],
    '/estoque':['Estoque','Usuario'],
    '/pendente':['Pendente','Usuario'],
    '/corte':['Calendario','Usuario','Corte'],
    '/sellin':['Ano','Usuario','SELLIN'],
    '/roteiro':['Calendario','Usuario'],
    '/devolucao':['Calendario','Usuario']

}

tab_dict={

    '/alerta':'Estoque',
    '/corte':'Calendario',
    '/sellin':'Ano',
    '/roteiro':'Calendario',
    '/devolucao':'Calendario'
}

col_name={

    '/alerta':'Alerta',
    '/corte':'Mês',
    '/sellin':'Ano',
    '/roteiro':'Mês',
    '/devolucao':'Mês'

}

callback_dict={

    '/alerta':1,
    '/corte':2,
    '/sellin':3,
    '/roteiro':4,
    '/devolucao':5

}

espera=3600

tab_user='Usuario'

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

    'Usuario':

    """
    
    SELECT * FROM netfeira.vw_usuario
    WHERE [Status do Usuário]='ATIVO'
    
    """,

    'Calendario':

    """
    
    SELECT * 
    FROM netfeira.vw_calend
    WHERE [Data Trabalhada] IS NOT NULL AND YEAR(Data)=YEAR(GETDATE())
    
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

    'Corte':

    """
    
    SELECT f.[Data de Falta],f.[Data e Hora],f.[ID Vendedor],v.Vendedor,s.Equipe,s.Supervisor, f.[ID Cliente],f.[Nome Fantasia],f.Matriz,
    f.Segmento,f.Canal,f.Pedido,f.SKU,f.Produto,f.Fabricante,f.Linha,f.[Unid. VDA],f.[Qtde. VDA],f.[Valor Unitário],f.[Total do Pedido]
    FROM netfeira.vw_falta f
    INNER JOIN netfeira.vw_vendedor v ON f.[ID Vendedor]=v.[ID Vendedor]
    INNER JOIN netfeira.vw_supervisor s ON v.[ID Equipe]=s.[ID Equipe]
    WHERE YEAR([Data de Falta])=YEAR(GETDATE())
    
    """,

    'Pendente':

    """
    
    SELECT p.Rota,p.[Tipo de Entrega],p.[Data da Expedição],p.[Data do Pedido],
    p.Fila,p.Origem,p.Tabelas,p.Pedido,p.[ID Cliente],cli.[Nome Fantasia],
    p.[ID Vendedor],vend.[Nome Resumido] AS [Vendedor],sup.Equipe,sup.Supervisor
    ,SUM(p.[Total Venda]) AS [Total Venda],SUM(p.[Peso Bruto KG]) AS [Peso Bruto KG]
    FROM netfeira.vw_pedpendente p
    INNER JOIN netfeira.vw_cliente cli ON p.[ID Cliente]=cli.[ID Cliente]
    INNER JOIN netfeira.vw_vendedor vend ON p.[ID Vendedor]=vend.[ID Vendedor]
    INNER JOIN netfeira.vw_supervisor sup ON vend.[ID Equipe]=sup.[ID Equipe]
    GROUP BY p.Rota,p.[Tipo de Entrega],p.Fila,p.Origem,p.Tabelas,p.Pedido,p.[ID Cliente],cli.[Nome Fantasia]
    ,p.[Data da Expedição],p.[Data do Pedido],
    p.[ID Vendedor],vend.[Nome Resumido],sup.Equipe,sup.Supervisor
    ORDER BY Pedido
    
    """,

    'SELLIN':

    """
    
    SELECT * FROM netfeira.vw_sellin
    WHERE NOT LEFT(Fornecedor,3)='DEV'
    
    """,

    'Ano':

    """
    
    SELECT * FROM netfeira.vw_calend
    
    """,

    'Roteiro':

    """
    
    SELECT r.Empresa,r.Romaneio,r.Rota,r.Pedido,r.NFe,r.[Situação da Rota],r.[Data da Montagem],r.[Data da Saída],
    r.Motorista,r.Veículo,r.[ID Cliente],cli.[Nome Fantasia],cli.Matriz,seg.Segmento,seg.Canal,
    r.[ID Vendedor],vend.[Nome Resumido],sup.Equipe,sup.Supervisor,r.[Frete Pago],
    SUM(r.[Total Venda]) AS [Total Venda], COUNT(r.SKU) AS [MIX],SUM(r.[Peso Bruto KG]) AS [Peso Bruto KG]
    FROM netfeira.vw_roteiros r
    INNER JOIN netfeira.vw_cliente cli ON r.[ID Cliente]=cli.[ID Cliente]
    INNER JOIN netfeira.vw_vendedor vend ON r.[ID Vendedor]=vend.[ID Vendedor]
    INNER JOIN netfeira.vw_supervisor sup ON vend.[ID Equipe]=sup.[ID Equipe]
    INNER JOIN netfeira.vw_segmento seg ON cli.[ID Segmento]=seg.[ID Segmento]
    WHERE YEAR(r.[Data da Montagem])=YEAR(GETDATE())
    GROUP BY r.Empresa,r.Romaneio,r.Rota,r.Pedido,r.NFe,r.[Situação da Rota],r.[Data da Montagem],r.[Data da Saída],
    r.Motorista,r.Veículo,r.[ID Cliente],cli.[Nome Fantasia],cli.Matriz,seg.Segmento,seg.Canal,
    r.[ID Vendedor],vend.[Nome Resumido],sup.Equipe,sup.Supervisor,r.[Frete Pago]
    ORDER BY r.[Data da Montagem]
    
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

@bot.message_handler(commands=['start','foto','fichatecnica','dadosprodutos','carteira','custo','alerta','estoque','pendente','corte','sellin','roteiro','devolucao'])
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
        
        bot.send_message(chat_id=chat_id,text=f'{msg} por questões de segurança me informe seu código de usuário para que possamos continuar.')

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

    global variavel_dict

    chat_id=message.from_user.id
    
    conteudo=str(message.data)

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    id=int(conteudo[:conteudo.find('/')])

    val=str(conteudo[conteudo.find('/')+1:])

    bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)

    match id:

        #alerta de estoque
        case 1:
            
            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            df=sql.GetDados(querys=querys,colunas=col_dict[comando])

            df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

            nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

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

            mensagem+='\n.'.join([str(l).title() for l in lista])
            
            mensagem+='\n\nObs. Se quiser o relatório clique nesse link: /extrato'

            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
            bot.send_message(chat_id=chat_id,text=mensagem)

            pass

        #corte de produto
        case 2:

            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            df=sql.GetDados(querys=querys,colunas=col_dict[comando])

            df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

            nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

            lista=df['Calendario'].loc[df['Calendario']['Mês']==val,'Data'].unique().tolist()

            df['Calendario']['Data Converte']=df['Calendario']['Data'].apply(DataConverte)
            
            if len(lista)>1:

                lista=[datetime.strftime(l,'%d/%m/%Y') for l in lista]

                markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                #bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)

                bot.send_message(chat_id=chat_id,text='Escolha uma das opções abaixo:',reply_markup=markup)      

                pass

            else:

                dt_now=df['Calendario'].loc[df['Calendario']['Data Converte']==val,'Data'].tolist()[-1]

                df['Corte']=df['Corte'].loc[df['Corte']['Data de Falta']==dt_now]

                if len(df['Corte'])>0:

                    qtde_pedido=Moeda.Numero(len(df['Corte']['Pedido'].unique().tolist()))

                    qtde_cortada=Moeda.Numero(df['Corte']['Qtde. VDA'].sum())

                    vl_total=Moeda.FormatarMoeda(df['Corte']['Total do Pedido'].sum())

                    mensagem=f'{msg} {nome}, identifiquei que no dia {val} teve {qtde_pedido} pedido(s) cortados, isso representa um total de R$ {vl_total} e {qtde_cortada} unidade(s). Segue os itens abaixo:\n\n.'

                    df['Consolidado']=df['Corte'].groupby(['Produto'],as_index=False).agg({'Qtde. VDA':'sum'})

                    df['Consolidado'].sort_values('Qtde. VDA',ascending=False,ignore_index=True,inplace=True)

                    df['Consolidado']['Qtde. VDA']=df['Consolidado']['Qtde. VDA'].astype(str)

                    df['Consolidado']['Info']=df['Consolidado']['Produto'] + ' - Qtde cortada: ' + df['Consolidado']['Qtde. VDA']

                    lista=df['Consolidado']['Info'].unique().tolist()
                    
                    mensagem+='\n.'.join([str(l).title() for l in lista])

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

        #sellin
        case 3:

            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]    

            df=sql.GetDados(querys,colunas=col_dict[comando])

            df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

            nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

            df['SELLIN']['Nome Fantasia']=df['SELLIN']['Nome Fantasia'].apply(RemoverEspaco)

            df['SELLIN']['Nome Fantasia']=df['SELLIN']['Nome Fantasia'].apply(Acentuacao.RemoverAcento)

            if val.isnumeric()==True:

                lista=df['SELLIN'].loc[df['SELLIN']['Data de Recebimento'].dt.year==int(val),'Nome Fantasia'].unique().tolist()

                lista.sort()

                markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                #bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)

                bot.send_message(chat_id=chat_id,text='Escolha um dos fornecedores abaixo:',reply_markup=markup)

                variavel_dict['Data de Recebimento']=val

                pass

            else:

                variavel_dict['Nome Fantasia']=val
                colunas=[l for l in variavel_dict.keys()]

                ano=int(variavel_dict[colunas[0]])

                fornec=variavel_dict[colunas[-1]]                

                df['SELLIN']=df['SELLIN'].loc[(df['SELLIN'][colunas[0]].dt.year==ano)&(df['SELLIN'][colunas[-1]]==fornec)]

                if len(df['SELLIN'])>0:

                    vl_peso=Moeda.FormatarMoeda(df['SELLIN']['Peso Bruto'].sum())
                    vl_total=Moeda.FormatarMoeda(df['SELLIN']['Total NFe'].sum())

                    mensagem=f'{msg} {nome} a empresa já comprou cerca de <strong>{vl_peso}</strong> tonelada(s) de <strong>{fornec}</strong> ficando um total de <strong>R$ {vl_total}</strong>'

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=mensagem)

                    pass

                else:

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=f'Olá {nome} não identifiquei nehum compra realizada no período selecionado.')

                    pass

                pass

            pass

        #roteiro
        case 4:

            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            df=sql.GetDados(querys=querys,colunas=col_dict[comando])

            df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

            nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

            lista=df['Calendario'].loc[df['Calendario']['Mês']==val,'Data'].unique().tolist()

            df['Calendario']['Data Converte']=df['Calendario']['Data'].apply(DataConverte)
            
            if len(lista)>1:

                lista=[datetime.strftime(l,'%d/%m/%Y') for l in lista]

                markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                #bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)

                bot.send_message(chat_id=chat_id,text='Escolha uma das opções abaixo:',reply_markup=markup)      

                pass

            else:

                arr_list=col_dict[comando]
                arr_list.append('Roteiro')

                col_dict[comando]=arr_list

                df=sql.GetDados(querys=querys,colunas=col_dict[comando])

                df['Calendario']['Data Converte']=df['Calendario']['Data'].apply(DataConverte)

                dt_now=df['Calendario'].loc[df['Calendario']['Data Converte']==val,'Data'].tolist()[-1]

                df['Roteiro']=df['Roteiro'].loc[df['Roteiro']['Data da Montagem']==dt_now]

                if len(df['Roteiro'])>0:

                    peso=Moeda.FormatarMoeda(df['Roteiro']['Peso Bruto KG'].sum())

                    vl_total=Moeda.FormatarMoeda(df['Roteiro']['Total Venda'].sum())

                    pedidos=Moeda.Numero(len(df['Roteiro']['Pedido'].unique().tolist()))

                    entrega=Moeda.Numero(len(df['Roteiro']['ID Cliente'].unique().tolist()))

                    veiculo=Moeda.Numero(len(df['Roteiro']['Romaneio'].unique().tolist()))

                    frete=Moeda.FormatarMoeda(df['Roteiro']['Frete Pago'].sum())

                    mensagem=f'{msg} {nome} no dia {val} teve saída de <strong>{veiculo} veículo(s)</strong> com <strong>{pedidos} pedido(s)</strong> um total de <strong>R$ {vl_total}</strong> e pesando <strong>{peso} KG</strong>.Total de frete <strong>R$ {frete}</strong> e <strong>{entrega} entrega(s)</strong> .\n\nRegiões:\n.'

                    name_arq=f'Roteiro {nome}.xlsx'

                    temp_path=os.path.join(os.getcwd(),path.name,name_arq)

                    df['Roteiro'].to_excel(temp_path,index=False)

                    arquivo=glob(temp_path)

                    path_dict[chat_id]=arquivo

                    df['Consolidado']=df['Roteiro'].groupby(['Rota'],as_index=False).agg({'Peso Bruto KG':'sum'})
                    df['Consolidado'].sort_values('Peso Bruto KG',ascending=False,ignore_index=True,inplace=True)

                    mensagem+='\n.'.join([str(l).title() for l in df['Consolidado']['Rota'].unique().tolist()])

                    mensagem+='\n\nObs. Se quiser o relatório clique nesse link: /extrato'

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=mensagem)

                    pass


                else:

                    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                    bot.send_message(chat_id=chat_id,text=f'{msg} {nome} não encontrei roteiro para o dia informado!')

                    pass

                pass

            pass

        #devolução
        case 5:

            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]

            df=sql.GetDados(querys=querys,colunas=col_dict[comando])

            df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

            nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

            lista=df['Calendario'].loc[df['Calendario']['Mês']==val,'Data'].unique().tolist()

            df['Calendario']['Data Converte']=df['Calendario']['Data'].apply(DataConverte)
            
            if len(lista)>1:

                lista=[datetime.strftime(l,'%d/%m/%Y') for l in lista]

                markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                #bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)

                bot.send_message(chat_id=chat_id,text='Escolha uma das opções abaixo:',reply_markup=markup)      

                pass

            else:

                arr_list=col_dict[comando]
                arr_list.append('Devolucao')

                col_dict[comando]=arr_list

                df=sql.GetDados(querys=querys,colunas=col_dict[comando])

                df['Calendario']['Data Converte']=df['Calendario']['Data'].apply(DataConverte)

                dt_now=df['Calendario'].loc[df['Calendario']['Data Converte']==val,'Data'].tolist()[-1]

                df['Devolucao']=df['Devolucao'].loc[df['Devolucao']['Data de Entrada']==dt_now]

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

                    df['Consolidado']['Info']=df['Consolidado'].apply(lambda info: f'{info["Motivo"]} - Total: R$ {Moeda.FormatarMoeda(info["Total Geral"])}',axis=1)

                    mensagem+='\n.'.join([str(l).title() for l in df['Consolidado']['Info'].unique().tolist()])

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

    pass

@bot.message_handler(commands=['extrato'])
def Extrair(message):

    chat_id=message.from_user.id

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=[tab_user])

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

    bot.send_chat_action(chat_id=chat_id,action='typing')
    bot.delete_message(chat_id=chat_id,message_id=message.message_id)

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

def ValidacaoProduto(message):

    chat_id=message.from_user.id

    func=funcoes[message.text]

    bot.send_chat_action(chat_id=chat_id,action='typing')
    #bot.delete_message(chat_id=chat_id,message_id=message.message_id)

    bot.send_message(chat_id=chat_id,text=f'Assunto: {func}\n\nInforme o código do(s) produto(s), caso for mais de um produto inserir uma virgula para fazer a inserção de mais códigos.')

    bot.register_next_step_handler(message=message,callback=globals().get(func))

    pass

def Foto(message):

    chat_id=message.from_user.id

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    codigos=[int(l) for l in str(message.text).split(',') if str(l).isnumeric()]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    df['Fotos']=df['Fotos'].loc[(df['Fotos']['SKU'].isin(codigos))]

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

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

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()  

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
        
        mensagem=f'{msg};\n{nome} tudo bem?\n\nSegue o link das fichas técnicas: {link}' if len(erros)<=0 else f'{msg};\n{nome} tudo bem?\n\nSegue o link das fichas técnicas: {link}.\n\nObs: Não encontrei na relação esses códigos com as fotos: <strong>{erros}</strong>'

        bot.send_chat_action(chat_id=chat_id,action='typing')
        bot.send_message(chat_id=chat_id,text=mensagem)

        pass


    else:
        
        #bot.delete_message(chat_id=message.from_user.id,message_id=message.message_id)
        bot.send_chat_action(chat_id=message.from_user.id,action='typing')

        bot.send_message(chat_id=message.from_user.id,text=f'{msg} {nome} tudo bem! não identifiquei nenhum produto com esses códigos: <strong>{erros}</strong>')

        pass

    Remover.RemoverArquivo('.zip')

    pass

def DadosProdutos(message):

    chat_id=message.from_user.id

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    codigos=[int(l) for l in str(message.text).split(',') if str(l).isnumeric()]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    df['Produtos']=df['Produtos'].loc[df['Produtos']['SKU'].isin(codigos)]

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

    erros=[l for l in codigos if not l in df['Produtos']['SKU'].unique().tolist()]

    erros=','.join([str(l) for l in erros])

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)    

    if len(df['Produtos'])>0:

        df['Produtos'].to_excel('Dados dos produtos.xlsx',index=False)

        with open('Dados dos produtos.xlsx','rb') as file:
        
            mensagem=f'{msg};\n{nome} tudo bem?\n\nSegue o arquivo com os dados dos produtos.' if len(erros)<=0 else f'{msg};\n{nome} tudo bem?\n\nSegue o arquivo com os dados dos produtos.\n\nObs: Não encontrei na relação esses códigos: <strong>{erros}</strong>'
            
            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)  
            bot.send_document(chat_id=chat_id,document=file,caption=mensagem)

            pass

        Remover.RemoverArquivo('.xlsx')

        pass

    else:

        bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)  
        bot.send_message(chat_id=chat_id,text=f'{msg} {nome} tudo bem! não identifiquei nenhum produto com esses códigos: <strong>{erros}</strong>')

        pass    

    pass

def ValidacaoID(message):

    chat_id=message.from_user.id

    codigo=str(message.text).upper().strip()

    temp_path=Path(__file__)

    temp_path=os.path.join(temp_path.parent.joinpath('Memória','Consolidado.xlsx'))

    temp_df=pd.read_excel(temp_path)

    df=sql.GetDados(querys=querys,colunas=[tab_user])

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    count=len(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo])
    
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

            nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

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

def Custo(message):

    chat_id=message.from_user.id

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    codigos=[int(l) for l in str(message.text).split(',') if str(l).isnumeric()]

    df=sql.GetDados(querys,colunas=col_dict[comando])

    df['Custo']=df['Custo'].loc[df['Custo']['SKU'].isin(codigos)]

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

    erros=[l for l in codigos if not l in df['Custo']['SKU'].unique().tolist()]

    erros=','.join([str(l) for l in erros])

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    if len(df['Custo'])>0:

        if len(df['Custo'])==1:

            produto=df['Custo']['Produto'].tolist()[-1]

            unid=df['Custo']['Unid. CMP'].tolist()[-1]

            vl_custo=df['Custo']['Atual C/ST'].sum()

            vl_ant=df['Custo']['Anterior C/ST'].sum()

            perc=df['Custo']['Perc %'].sum()

            dif=df['Custo']['Dif R$'].sum()

            mensagem=f'{msg};\n{nome} tudo bem?\n\nO custo do item <strong>{produto}</strong>:\nUnidade de Compra: {unid}\nCusto Atual: R$ {Moeda.FormatarMoeda(vl_custo)}\nCusto Anterior: R$ {Moeda.FormatarMoeda(vl_ant)}\nPercentual de Ajuste: {Moeda.FormatarMoeda(perc)}%\nDiferença: R$ {Moeda.FormatarMoeda(dif)}' if len(erros)<=0 else f'{msg};\n{nome} tudo bem?\n\nO custo do item <strong>{produto}</strong>:\nUnidade de Compra: {unid}\nCusto Atual: R$ {Moeda.FormatarMoeda(vl_custo)}\nCusto Anterior: R$ {Moeda.FormatarMoeda(vl_ant)}\nPercentual de Ajuste: {Moeda.FormatarMoeda(perc)}%\nDiferença: R$ {Moeda.FormatarMoeda(dif)}\n\nObs: Não encontramos na relação esses códigos: <strong>{erros}</strong'
            
            bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
            bot.send_message(chat_id=chat_id,text=mensagem)

            pass

        else:

            df['Custo'].to_excel('Custo dos produtos.xlsx',index=False)

            with open('Custo dos produtos.xlsx','rb') as file:
            
                mensagem=f'{msg};\n{nome} tudo bem?\n\nSegue o arquivo com os dados dos produtos.' if len(erros)<=0 else f'{msg};\n{nome} tudo bem?\n\nSegue o arquivo com os dados dos produtos.\n\nObs: Não encontramos na relação esses códigos: <strong>{erros}</strong>'
                
                bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
                bot.send_document(chat_id=chat_id,document=file,caption=mensagem)

                pass

            pass

        Remover.RemoverArquivo('.xlsx')


        pass


    else:

        bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
        bot.send_message(chat_id=chat_id,text=f'{msg} {nome} tudo bem! não identificamos nenhum produto com esses códigos: <strong>{erros}</strong>')

        pass

    pass

def Estoque(message):

    chat_id=message.from_user.id

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]    

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    codigos=[int(l) for l in str(message.text).split(',') if str(l).isnumeric()]    

    df=sql.GetDados(querys,colunas=col_dict[comando])

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

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
        
        bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
        bot.send_message(chat_id=chat_id,text=mensagem)

        pass

    else:

        bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
        bot.send_message(chat_id=chat_id,text=f'{msg} {nome} tudo bem! não identificamos nenhum produto com esses códigos: <strong>{erros}</strong>')

        pass

    pass

def Pendente(message):

    path=Path(__file__).parent.joinpath('Extrato')

    path.mkdir(exist_ok=True)

    global path_dict

    chat_id=message.from_user.id

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]    

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    df=sql.GetDados(querys,colunas=col_dict[comando])

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

    qtd_ped=Moeda.Numero(len(df['Pendente']['Pedido'].unique().tolist()))

    vl_total=Moeda.FormatarMoeda(df['Pendente']['Total Venda'].sum())

    mensagem=f'{msg} {nome} identifiquei {qtd_ped} pedido(s) pendente de roterização, o total dos pedidos é R$ {vl_total}. Abaixo mostrar as regiões com pedido:\n\n.' if len(df['Pendente'])>0 else f'{msg} {nome} identifiquei {qtd_ped} não encontrei nenhum pedido pendente de roterização'

    if len(df['Pendente'])>0:

        name_arq=f'Pendente {nome}.xlsx'

        df['Consolidado']=df['Pendente'].groupby(['Rota'],as_index=False).agg({'Pedido':'count'})

        df['Consolidado'].sort_values('Pedido',ascending=False,ignore_index=True,inplace=True)

        df['Consolidado']['Pedido']=df['Consolidado']['Pedido'].astype(str)

        df['Consolidado']['Pedido']=df['Consolidado']['Pedido'].apply(Moeda.Numero)

        df['Consolidado']['Info']=df['Consolidado']['Rota'] + ' - Quantidade de pedidos: ' + df['Consolidado']['Pedido']

        lista=df['Consolidado']['Info'].unique().tolist()

        mensagem+='\n.'.join([str(l).title() for l in lista])

        mensagem+='\n\nObs. Se quiser o relatório clique nesse link: /extrato'

        temp_path=os.path.join(os.getcwd(),path.name,name_arq)            

        df['Pendente'].to_excel(temp_path,index=False)

        arquivo=glob(temp_path)

        path_dict[chat_id]=arquivo

        bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
        bot.send_message(chat_id=chat_id,text=mensagem)

        pass


    else:

        bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
        bot.send_message(chat_id=chat_id,text=mensagem)

        pass
    
    pass

#opções
def Opcao(message):

    chat_id=message.from_user.id
    
    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

    lista=df[tab_dict[comando]][col_name[comando]].unique().tolist()

    markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
    bot.send_message(chat_id=chat_id,text=f'{msg} {nome} escolha uma das opções abaixo:',reply_markup=markup)

    pass

def Alerta(message):

    chat_id=message.from_user.id
    
    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    df[tab_user]['ID Usuário']=df[tab_user]['ID Usuário'].apply(RemoverEspaco)

    nome=str(df[tab_user].loc[df[tab_user]['ID Usuário']==codigo,'Nome Resumido'].tolist()[-1]).title()

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

    for c in ['ID Sup','ID Gerente','ID Vendedor']:

        codigos=df['Vendedor'][c].unique().tolist()

        for i in codigos:

            if i in lista:
                
                continue
            
            lista.append(i)

            pass

        pass

    df['Vendedor']=df['Vendedor'].loc[df['Vendedor']['ID Vendedor'].isin(lista)]

    col_dict={'ID Vendedor':'ID Sup','ID Sup':'ID Gerente'}

    for col1,col2 in col_dict.items():

        df['Vendedor'][f'Igual {col1}']=df['Vendedor'].apply(lambda info: 1 if info[col1]==info[col2] else 0,axis=1)

        pass

    colunas=[l for l in df['Vendedor'].columns.tolist() if str(l).find('Igual')>=0]

    for c in colunas:

        df['Vendedor']=df['Vendedor'].loc[df['Vendedor'][c]==0]

        pass

    colunas=[l for l in df['Vendedor'].columns.tolist() if str(l).find('ID')>=0]

    colunas.sort(reverse=False)

    temp_dict=dict()

    for i,c in enumerate(colunas):

        for key in lista:

            count=len(df['Vendedor'].loc[df['Vendedor'][c]==key])

            if count<=0:

                continue
            
            temp_dict[key]=c

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
           
            print('LogBOT Telegram conectado!')

            bot.polling()

            pass

        except Exception as erro:

            print('LogBOT Telegram desconectado!')

            Start()

            pass

        pass

    pass

if __name__=='__main__':

    Start()

    pass