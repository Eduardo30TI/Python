import telebot
from telebot import types
import pyttsx3
from Acesso import Login
from Query import Query
from Moeda import Moeda
from RemoverArquivo import Remover
from decouple import config
from datetime import datetime
from glob import glob
import os
from pathlib import Path
import pandas as pd

TOKEN=config('TOKEN')

bot=telebot.TeleBot(token=TOKEN,parse_mode='HTML')

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

comando=None

espera=3600

querys={

    'Receber':

    """
    
    SELECT * FROM netfeira.vw_contareceber
    WHERE Situação='EM ABERTO'
    
    """,

    'Cliente':

    """
    
    SELECT * FROM netfeira.vw_cliente
    
    """,

    'Historico':


    """
    
     WITH TabEntrega AS (

        SELECT DISTINCT tp_entrega,
        CASE WHEN tp_entrega='TR' THEN 'TRANSPORTADORA'
        WHEN tp_entrega='RE' THEN 'RETIRA' WHEN tp_entrega='EN' THEN 'ENTREGA' END AS st_entrega
        FROM ped_vda

    ),

    TabEvento AS (

        SELECT * FROM (

            SELECT a.seq_evento,a.cd_emp,a.cd_clien,a.dt_criacao,a.nu_ped,a.des_fila,a.seq,
            MAX(a.seq)OVER(PARTITION BY a.cd_emp,a.cd_clien,a.nu_ped ORDER BY a.seq DESC) AS seq_max
            FROM (

                SELECT e.seq_evento,e.cd_emp,e.cd_clien,e.dt_criacao,e.nu_ped,f.des_fila,
                ROW_NUMBER()OVER(PARTITION BY e.cd_emp,e.cd_clien,e.nu_ped ORDER BY e.seq_evento) AS seq
                FROM evento e
                INNER JOIN fila f ON e.cd_fila=f.cd_fila
				WHERE YEAR(e.dt_criacao)= YEAR(GETDATE())

            )a

        )b
        WHERE b.seq=b.seq_max

    )

    SELECT CONVERT(DATETIME,CAST(ped.dt_cad AS DATE),101) AS [Data do Pedido],ped.dt_cad AS [Data e Hora],emp.nome_fant AS [Empresa],
    i.nu_ped AS [Pedido],tp.[Estatística Comercial],tp.[Tipo de Pedido],ped.cd_clien AS [ID Cliente],cli.[CNPJ],cli.[Nome Fantasia],cli.Matriz,
    it.cd_prod AS SKU,prod.Produto,prod.Fabricante,it.seq AS [Seq],
    it.unid_vda AS [Unid. VDA],it.qtde_unid_vda AS [Qtde VDA],
    it.vl_venda AS [Total Venda],
    CASE WHEN it.situacao='FA' THEN 'FATURADO' ELSE 'EM ABERTO' END AS [Situação]
    ,ev.des_fila AS [Fila],en.st_entrega AS [Situação de Entrega], r.situacao
    FROM it_rom i
    INNER JOIN romaneio r ON i.nu_rom=r.nu_rom AND r.situacao<>'EN'
    INNER JOIN ped_vda ped ON i.nu_ped=ped.nu_ped AND i.cd_emp=ped.cd_emp
    INNER JOIN it_pedv it ON ped.cd_emp=it.cd_emp AND ped.nu_ped=it.nu_ped
    INNER JOIN TabEvento ev ON ped.cd_emp=ev.cd_emp AND ped.cd_clien=ev.cd_clien AND ped.nu_ped=ev.nu_ped
    INNER JOIN TabEntrega en ON ped.tp_entrega=en.tp_entrega
    INNER JOIN empresa emp ON ped.cd_emp=emp.cd_emp AND emp.ativo=1
    INNER JOIN netfeira.vw_cliente cli ON ped.cd_clien=cli.[ID Cliente]
    INNER JOIN netfeira.vw_produto prod ON it.cd_prod=prod.SKU
    INNER JOIN netfeira.vw_tpped tp ON ped.tp_ped=tp.[ID Tipo]
    AND it.situacao IN('FA','AB')
    
    """

}


commands_dict={ 
    '/titulos': 'Títulos em aberto',
    '/pedidos': 'Acompanhamento de pedidos'

    
}

start={
    '/titulos': 'Opcao',
    '/pedidos': 'Historico'


}

funcoes={
    '/titulos': 'Opcao',
    '/pedidos': 'Historico'


}

#função usando para opções
col_dict={
    '/titulos': ['Receber'],
    '/pedidos': ['Historico','Cliente']

}

tab_dict={
    '/titulos': 'Receber'

}

col_name={
    '/titulos': 'Status do Título'


}

callback_dict={ 
    '/titulos': 1
   

}


@bot.message_handler(commands=['start','titulos','pedidos'])
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
        
        bot.send_message(chat_id=chat_id,text=f'{msg} por questões de segurança me informe seu CPF ou CNPJ (sem pontos e sem barra) interno para que possamos continuar.')

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


@bot.callback_query_handler(func=lambda call:True)
def call_handler(message):

    chat_id=message.from_user.id
    
    conteudo=str(message.data)

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    id=int(conteudo[:conteudo.find('/')])

    val=str(conteudo[conteudo.find('/')+1:])

    bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)
    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    match id:
        case 1:

            temp_df=Memoria(chat_id=chat_id)

            temp_df['Código']=temp_df['Código'].astype(str)

            codigo=temp_df['Código'].tolist()[-1]
            
            df=sql.GetDados(querys=querys,colunas=['Cliente','Receber'])

            df['Receber']['CNPJ']=df['Receber']['CNPJ'].astype(str)

            if len(df['Receber'])>0:

                df['Receber']=df['Receber'].loc[(df['Receber']['CNPJ']==codigo)&(df['Receber']['Status do Título']==val)]

                qtd_titulos=Moeda.Numero(len(df['Receber']['Título'].unique().tolist()))

                soma=Moeda.FormatarMoeda(df['Receber']['Valor Líquido'].sum())

                nome=str(df['Cliente'].loc[df['Cliente']['CNPJ']==codigo,'Nome Fantasia'].tolist()[-1]).title()

                mensagem = f'{msg}, {nome} identifiquei <strong>{qtd_titulos}</strong> títulos no nosso sistema, totalizando <strong>R$ {soma}</strong>.'

                bot.send_message(chat_id=chat_id,text=mensagem)
            else:

                bot.send_message(chat_id=chat_id,text='Não encontrei nenhuma informação no sistema.')

            pass

    pass

def ValidacaoID(message):

    chat_id=message.from_user.id

    codigo=str(message.text).upper().strip()

    temp_path=Path(__file__)

    temp_path=os.path.join(temp_path.parent.joinpath('Memória','Consolidado.xlsx'))

    temp_df=pd.read_excel(temp_path)

    df=sql.GetDados(querys=querys,colunas=['Cliente'])

    df['Cliente']['CNPJ']=df['Cliente']['CNPJ'].astype(str)

    count=len(df['Cliente'].loc[df['Cliente']['CNPJ']==codigo])
    
    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
    #bot.delete_message(chat_id=chat_id,message_id=message.message_id)

    if count>0:
        temp_df['Código']=temp_df['Código'].astype(str)
        id_temp=temp_df.loc[temp_df['Código']==codigo,'ChatID'].tolist()
        if len(id_temp)>0:

            bot.send_message(chat_id=chat_id,text='Identificamos que o código desse usuário já está sendo usando em outro aparelho. Caso você desconheça essa informação entrar em contato com o administrador da plataforma.')

            bot.register_next_step_handler(message=message,callback=ValidacaoID)

            pass

        else:

            bot.send_chat_action(chat_id=message.from_user.id,action='typing')
            #bot.delete_message(chat_id=message.from_user.id,message_id=message.message_id)

            nome=str(df['Cliente'].loc[df['Cliente']['CNPJ']==codigo,'Nome Fantasia'].tolist()[-1]).title()

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

def Historico(message):

    chat_id=message.from_user.id

    temp_df=Memoria(chat_id=chat_id)

    temp_df['Código']=temp_df['Código'].astype(str)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    for c in ['Historico','Cliente']:

        df[c]['CNPJ']=df[c]['CNPJ'].astype(str)

        df[c]=df[c].loc[df[c]['CNPJ']==codigo]

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    if len(df['Historico'])>0:

        dt_ult = datetime.strftime(df['Cliente']['Última Compra'].max(),'%d/%m/%Y')

        qtd_ped = len(df['Historico']['Pedido'].unique().tolist())

        bot.send_chat_action(chat_id=message.from_user.id,action='typing')

        mensagem = f'{msg}, você tem <strong>{qtd_ped}</strong> pedidos em aberto, e sua última compra foi em <strong>{dt_ult}</strong>.'

        bot.send_message(chat_id=chat_id,text=mensagem)

        pass

    else:

        bot.send_chat_action(chat_id=message.from_user.id,action='typing')
        bot.send_message(chat_id=chat_id,text='Não encontrei nenhuma informação no sistema.')

        pass


    pass


def Opcao(message):

    chat_id=message.from_user.id
    
    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    lista=df[tab_dict[comando]][col_name[comando]].unique().tolist() 

    markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
    bot.send_message(chat_id=chat_id,text=f'{msg} escolha uma das opções abaixo:',reply_markup=markup)

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

def DataConverte(data):

    return datetime.strftime(data,'%d/%m/%Y')

    pass

def Voice(mensagem):

    engine=pyttsx3.init()

    caracteres=len([l for l in mensagem])
   
    rate=engine.getProperty('rate')
    velocidade=caracteres-rate if (caracteres-rate)>0 else rate+caracteres
    engine.setProperty('rate',velocidade)
    engine.save_to_file(mensagem,'audio.mp3')
    #engine.say(mensagem)
    engine.runAndWait()

    temp_path=os.path.join(os.getcwd(),'audio.mp3')

    return temp_path

    pass

def RemoverEspaco(val):

    return str(val).strip()

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